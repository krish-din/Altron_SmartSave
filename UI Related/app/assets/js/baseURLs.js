let headers = new Headers();

headers.append('Content-Type', 'application/json');
headers.append('Accept', 'application/json');

headers.append('Access-Control-Allow-Origin', '*');
//  headers.append('Access-Control-Allow-Credentials', 'true');
//  headers.append("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
headers.append('GET', 'POST', 'OPTIONS');
var getHttpClient = function() { 
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

  var postHttpClient = function() { 
    this.post = function(url, data,callback) {
      var httpRequest = new XMLHttpRequest();
      httpRequest.open("POST", url, false);
      httpRequest.onreadystatechange = function() {
        if (httpRequest.readyState == 4 && httpRequest.status == 200)
          callback(httpRequest.responseText);
      };     
      httpRequest.send(JSON.stringify(data));
    };
  };

var catalogUrl = localStorage.getItem("catalogURL")
var HouseID = localStorage.getItem("HouseID")
var deviceID = localStorage.getItem("deviceID")
// localStorage.setItem("catalogURL",catalogUrl)
// localStorage.setItem("HouseID",HouseID)
// localStorage.setItem("deviceID",deviceID)
console.log(localStorage.getItem("catalogURL"));
var rURL = catalogUrl + '/geturlinfo/' + HouseID +'/' + deviceID ;

var req = new getHttpClient();
req.responseType = 'json';

req.post(rURL, function(response) {
    console.log(response)
    
  jsonResponse = JSON.parse(response);
  console.log(jsonResponse.Output.Devices[deviceID]["DC"]);  
  localStorage.setItem("DC",jsonResponse.Output.Devices[deviceID]["DC"]);
  localStorage.setItem("SC",jsonResponse.Output.Devices[deviceID]["SC"]);
  
  });

var req = new postHttpClient();
req.responseType = 'json';
rURL = localStorage.getItem("SC");
console.log(rURL)
req.post(rURL,{"call": "getService","houseID": localStorage.getItem("HouseID"),"deviceID": localStorage.getItem("deviceID"),"data": ["DataCollection", "sensorStatusAPI","Cost"]}, function(response) {
console.log(response)

jsonResponse = JSON.parse(response);
console.log(jsonResponse.Output["DataCollection"]["DataInsertAPI"]);  
localStorage.setItem("dataAPI",jsonResponse.Output["DataCollection"]["DataInsertAPI"]);
localStorage.setItem("statusAPI",jsonResponse.Output["sensorStatusAPI"]["API"]);
localStorage.setItem("costKey",jsonResponse.Output["Cost"]["read_key"]);
localStorage.setItem("costAPI",jsonResponse.Output["Cost"]["CostAPI"]);
});

var rURL = localStorage.getItem("catalogURL") + '/getsensorInfo/' + localStorage.getItem("HouseID")+'/' + localStorage.getItem("deviceID") ;

var req = new getHttpClient();
req.responseType = 'json';
var plugID = "plugcards"

req.post(rURL, function(response) {
    console.log(response)
    
    jsonResponse = JSON.parse(response);    
    localStorage.setItem("SensorIDs",JSON.stringify(jsonResponse.Output.Devices[localStorage.getItem("deviceID")]["Sensors"]))
});

var req = new postHttpClient();
req.responseType = 'json';
rURL = localStorage.getItem("DC");
console.log(rURL)
req.post(rURL,{"call": "getDeviceName","houseID": localStorage.getItem("HouseID"),"deviceID": localStorage.getItem("deviceID"),"data":JSON.parse(localStorage.getItem("SensorIDs"))}, function(response) {


jsonResponse = JSON.parse(response);
localStorage.setItem("Sensors",JSON.stringify(jsonResponse.Output))
console.log(jsonResponse)
});