print("Initializing...")

from os import unlink
from random import randint
from pyrogram import Client
from pyrogram.types import Message
import asyncio
from aiohttp_socks import ProxyConnector
import aiohttp
from yarl import URL
import re
import urllib.parse
import json
from bs4 import BeautifulSoup

from conf import *


async def get_token(base_url: URL, user: str, passw: str, proxy: str = ""):
    query: dict = {
        "service": "moodle_mobile_app",
        "username": user,
        "password": passw,
    }
    token_url: URL = base_url.with_path("login/token.php").with_query(query)
    try:
        if proxy == "":
            connector = aiohttp.TCPConnector()
        else:
            connector = ProxyConnector.from_url(proxy)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(token_url) as response:
                result = await response.json()
                return result["token"]
    except Exception as e:
        print("Error in get_token('{}', '{}', '{}')".format(base_url, user, passw))
        print(e)
        return False


def proxy_decrypt(text):
    trans = str.maketrans(
        "@./=#$%&:,;_-|0123456789abcd3fghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "ZYXWVUTSRQPONMLKJIHGFEDCBAzyIwvutsrqponmlkjihgf3dcba9876543210|-_;,:&%$#=/.@",
    )
    return str.translate(text[::2], trans)


def sign_url(token: str, url: URL):
    query: dict = dict(url.query)
    query["token"] = token
    path = "webservice" + url.path
    return url.with_path(path).with_query(query)


async def shorten_url(url: URL):
    query = {"url": str(url)}
    base = URL(" ")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base.with_query(query)) as response:
                return URL(await response.text())
    except Exception as e:
        print("Error in shorten_url('{}')".format(url))
        print(e)
        return False


async def send_calendar(moodle: str, user: str, passw: str, urls: list, proxy: str = "") -> list:
    if proxy == "":
        connector = aiohttp.TCPConnector()
    else:
        connector = ProxyConnector.from_url(proxy)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Extraer el token de inicio de sesión
        try:
            # Login
            async with session.get(moodle + "/login/index.php") as response:
                html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            token = soup.find("input", attrs={"name": "logintoken"})
            if token:
                token = token["value"]
            else:
                token = ""
            payload = {
                "anchor": "",
                "logintoken": token,
                "username": user,
                "password": passw,
                "rememberusername": 1,
            }
            async with session.post(moodle + "/login/index.php", data=payload) as response:
                html = await response.text()

            sesskey = re.findall('(?<="sesskey":")(.*?)(?=")', html)[-1]
            userid = re.findall('(?<=userid=")(.*?)(?=")', html)[-1]
            # Mover a calendario
            base_url = (
                "{}/lib/ajax/service.php?sesskey={}&info=core_calendar_submit_create_update_form"
            )
            payload = [
                {
                    "index": 0,
                    "methodname": "core_calendar_submit_create_update_form",
                    "args": {
                        "formdata": "id=0&userid={}&modulename=&instance=0&visible=1&eventtype=user&sesskey={}&_qf__core_calendar_local_event_forms_create=1&mform_showmore_id_general=1&name=Evento&timestart[day]=4&timestart[month]=4&timestart[year]=2022&timestart[hour]=18&timestart[minute]=55&description[text]={}&description[format]=1&description[itemid]={}&location=&duration=0"
                    },
                }
            ]
            urls_payload = '<p dir="ltr"><span style="font-size: 14.25px;">{}</span></p>'
            base_url = base_url.format(moodle, sesskey)
            urlparse = lambda url: urllib.parse.quote_plus(urls_payload.format(url))
            urls_parsed = "".join(list(map(urlparse, urls)))
            payload[0]["args"]["formdata"] = payload[0]["args"]["formdata"].format(
                userid, sesskey, urls_parsed, randint(1000000000, 9999999999)
            )
            async with session.post(base_url, data=json.dumps(payload)) as result:
                resp = await result.json()
                resp = resp[0]["data"]["event"]["description"]

            return re.findall("https?://[^\s\<\>]+[a-zA-z0-9]", resp)
        except Exception as e:
            print(
                "Error in send_calendar()\nMoodle: {}\nUser: {}\nPassword: {}\nURLs: {}".format(
                    moodle, user, passw, urls
                )
            )
            print(e)
            return False


# url_list = {
#     101010101: {
#         "proxy": "asdadadadsd"
#         "http://adasdad": ["user", "pass", "token"],
#         "urls": ["url1", "url2", "url3"],
#     },
# }
url_list = {}
bot = Client("bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


@bot.on_message()
async def message_handler(client: Client, message: Message):
    uid: str = message.from_user.username
    msg: str = message.text
    if not msg:
        msg = ""
    if msg.lower() == "/start":
        await message.reply("Bienvenido -> {}\nUser -> @{}".format(message.from_user.first_name,uid))
        return

    # Comprobar que el usuario esté autorizado.
    if not url_list.get(uid):
        # url_list[uid] = {"proxy": "", "urls": []}
        # return
        auth = False
        if uid == admin_user or uid in authorized_users:
            auth = True
            url_list[uid] = {"proxy": "", "urls": []}
        if auth == False:
            return
            
    #Proxy
    if msg.lower().startswith("/proxy"):
        try:
            proxy = msg.split(" ")[1]
            proxy_parts = proxy.split("/")
            proxy_parts[-1] = proxy_decrypt(proxy_parts[-1])
            url_list[uid]["proxy"] = "/".join(proxy_parts)
        except:
            url_list[uid]["proxy"] = ""
        await message.reply("✅ Proxy guardado.")
        return

    # Autenticación
    if msg.lower().startswith("/setauth"):
        progress_message = await message.reply(
            "⏳ Autenticando...")
        auth: list = msg.split(" ")
        print(auth)
        if len(auth) != 4:
            await progress_message.edit(
                "❌ La forma correcta es: /setauth https://moodle.cu/ Usuario Contraseña\n\n"
                + "❌ El url, el usuario y la contraseña no deben contener espacios."
            )
            return
        try:
            url = URL(auth[1]).origin()
        except:
            await progress_message.edit("❌ El primer parámetro debe ser el URL del moodle")
            return
        user = auth[2]
        passw = auth[3]
        token = await get_token(url, user, passw, url_list[uid]["proxy"])
        if token:
            url_list[uid][str(url).lower()] = [user, passw, token]
            await progress_message.edit("✅ Usuario y contraseña guardados.")
        else:
            if not token:
                await progress_message.edit(
                    "❌ Error al obtener token con las creenciales actuales."
                )
        return

    # Firmar enlaces
    if re.search("https?://[^\s]+[a-zA-z0-9]", msg, re.IGNORECASE):
        urls = re.findall("https?://[^\s]+[a-zA-z0-9]", msg, re.IGNORECASE)
        progress_message = await message.reply(
            "⏳ Firmando {} links...".format(len(urls)))

        base_url = URL(urls[0]).origin()
        auth = url_list[uid].get(str(base_url).lower())
        if auth:
            user = auth[0]
            passw = auth[1]
            token = auth[2]
        else:
            await message.reply(
                "❌ No se encuentra autenticación para " + str(base_url))
            return
        counter = 0

        if str(urls[0]).__contains__("/draftfile.php/"):
            await progress_message.edit("⏳ Moviendo Drafts a calenario...")
            urls = await send_calendar(str(base_url), user, passw, urls, url_list[uid]["proxy"])
            if not urls:
                await message.reply(
                    "❌ Error moviendo a calendario")
                return
            await progress_message.edit("⏳ Firmando {} links...".format(len(urls)))

        for url in urls:
            url_signed = sign_url(token, URL(url))
            url_short = await shorten_url(url_signed)
            if url_short:
                url_list[uid]["urls"].append(str(url_short))
            else:
                url_list[uid]["urls"].append(str(url_signed))
            counter += 1

        await progress_message.edit(
            "✅ Firmados {}/{} links. Puede usar /txt para generar el .txt".format(
                counter, len(urls)
            )
        )
        return

    # Generar TXT
    if msg == "/txt":
        if url_list[uid]["urls"] == []:
            await message.reply(
                "❌ No hay ningún link firmado.")
        else:
            links = "\n".join(url_list[uid]["urls"])
            fname = str(randint(100000000, 9999999999)) + ".txt"
            with open(fname, "w") as f:
                f.write(links)
            try:
                await message.reply(links)
            except:
                pass
            await message.reply_document(fname)
            url_list[uid]["urls"] = []
            unlink(fname)


print("Starting...")
bot.start()
print("Ready.")
bot.send_message(admin_user, "Bot reiniciado.")
loop: asyncio.AbstractEventLoop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_forever()
