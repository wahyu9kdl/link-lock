var url = "https://wahyu9kdl.github.io/link-lock/create/"; // destination url var count = 10; // in seconds function countDown() { if (count > 0) { count--; var time = count + 1; $('#word').html('<b>This Page Will Automatically Redirect To </b> ' + url + ' in ' + time + ' seconds.'); setTimeout("countDown()", 1000); } else { window.location.href = url; } } countDown();
