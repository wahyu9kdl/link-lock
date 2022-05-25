var url = 'https://github.com/wahyu9kdl/link-lock/archive/refs/heads/main.zip';
 var request = new XMLHttpRequest();
 request.responseType = "blob"; // Not sure if this is needed
 request.open("POST", url);
 
 var self = this;
 request.onreadystatechange = function () {
 if (request.readyState === 4) {
 var file = $(self).data('file');            
 var anchor = document.createElement('a');
 anchor.download = file;
 anchor.href = window.URL.createObjectURL(request.response);
 anchor.click();            
 }
 };
 
 request.addEventListener("progress", function (e) {
 if(e.lengthComputable) {
 var completedPercentage = e.loaded / e.total;
 console.log("Completed: ", completedPercentage , "%");
 }
 }, false);
 request.send();
 
