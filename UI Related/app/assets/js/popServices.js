
var getHttpClient = function() { 
  this.post = function(url, callback) {
    var httpRequest = new XMLHttpRequest();
    httpRequest.open("GET", url, false);
    httpRequest.onreadystatechange = function() {
      if (httpRequest.readyState == 4 && httpRequest.status == 200){
        callback(httpRequest.responseText);}
        else{
          document.getElementById("serviceError").style.color = "red";
          document.getElementById("serviceError").style.display= "inline";
        }
    };     
    httpRequest.send(); 
  };
};


var postHttpClient = function() { 
    this.post = function(url, data,callback) {
      var httpRequest = new XMLHttpRequest();
      httpRequest.open("POST", url, false);
      httpRequest.onreadystatechange = function() {
        if (httpRequest.readyState == 4 && httpRequest.status == 200){
          callback(httpRequest.responseText);
        }
        else{
          document.getElementById("serviceError").style.color = "red";
          document.getElementById("serviceError").style.display= "inline";
        }
      };     
      httpRequest.send(JSON.stringify(data));
    };
  };

  var req = new postHttpClient();
  req.responseType = 'json';
  rURL = localStorage.getItem("SC");
  console.log(rURL)
  req.post(rURL,{"call": "getService","houseID": localStorage.getItem("HouseID"),"deviceID": localStorage.getItem("deviceID"),"data": ["Threshold", "Plugs","T-Sensors","M-Sensors"]}, function(response) {
  console.log(response)
  
  jsonResponse = JSON.parse(response);
  document.getElementById ("mymonthCAP").value = jsonResponse.Output["Threshold"]["MonthlyCap"]
  document.getElementById ("mytemperature").value = jsonResponse.Output["Threshold"]["Temperature"]
  document.getElementById ("mytemperatureFEQ").value = jsonResponse.Output["T-Sensors"]["Frequency"]
  document.getElementById ("myplugFEQ").value = jsonResponse.Output["Plugs"]["Frequency"]
  document.getElementById ("mymsensorFEQ").value = jsonResponse.Output["M-Sensors"]["Frequency"]  
  });


  
// var rURL = localStorage.getItem("catalogURL") + '/gettelusers/' + localStorage.getItem("HouseID");

// var req = new getHttpClient();
// req.responseType = 'json';

// req.post(rURL, function(response) {
//     console.log(response)
    
//   jsonResponse = JSON.parse(response);
//   jsonResponse.Output["Tel_Users"].forEach(element => {
    
//   });
//   console.log(jsonResponse.Output["Tel_Users"]);  
//   });