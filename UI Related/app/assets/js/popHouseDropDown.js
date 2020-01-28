var HttpClient = function() { 
    this.post = function(url, callback) {
      var httpRequest = new XMLHttpRequest();
      httpRequest.open("GET", url, false);
      httpRequest.onreadystatechange = function() {
        if (httpRequest.readyState == 4 && httpRequest.status == 200)
          callback(httpRequest.responseText);
      };     
      httpRequest.send(); 
    };
  };
var houseIDList = []
var req = new HttpClient();
req.responseType = 'json';
rURL = "http://"+sessionStorage.getItem("serverIP")+":9292/houseservice/gethouseids";
req.post(rURL, function(response) {    
jsonResponse = JSON.parse(response);
houseIDList = jsonResponse.Output;
});
var list1 = document.getElementById('housedropdown');
document.getElementById('updatecatalogURL').value = "";        
document.getElementById("updateplugLimit").value = "";
document.getElementById("updatepirLimit").value = "";  
document.getElementById("updatetempLimit").value = "";

list1.options[0] = new Option('--', 'noVal');

for (const val of houseIDList){
    list1.options[list1.options.length] = new Option(val, val);}
  

