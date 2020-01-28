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


function monthCAP (button) {
    var MonthlyCapVal = document.getElementById ("mymonthCAP").value ;
    document.getElementById("mymonthCAP").disabled = true;
    document.getElementById("mymonthCAPbutton").disabled = true;
    console.log(MonthlyCapVal)
    var updateCap = {
        "call": "updateService",
        "houseID": "H001",
        "deviceID": "D1",
        "data": {"service":"Threshold","properties":{"MonthlyCap":parseInt(MonthlyCapVal)}}
    }
    if (MonthlyCapVal === "" || MonthlyCapVal === undefined){
        document.getElementById('serviceError').innerHTML = "Invalid Value"
        document.getElementById("serviceError").style.display= "inline";
        document.getElementById("serviceError").style.color = "red";
        document.getElementById("mymonthCAP").disabled = false;
        document.getElementById("mymonthCAPbutton").disabled = false;
        return false
    }
  var req = new postHttpClient();
  req.responseType = 'json';
  rURL = localStorage.getItem("SC");
  req.post(rURL,updateCap, function(response) {    
    jsonResponse = JSON.parse(response);
    console.log(jsonResponse.Output)
      if (jsonResponse.Result === "success"){
        $("#success-alert").fadeTo(1000, 500).slideUp(500, function() {
            $("#success-alert").slideUp(500);});
        document.getElementById("serviceError").style.display= "none";        
        document.getElementById("mymonthCAP").disabled = false;
        document.getElementById("mymonthCAPbutton").disabled = false;
      }
      else{        
        document.getElementById('serviceError').innerHTML = jsonResponse.Output
        document.getElementById("serviceError").style.display= "inline";
        document.getElementById("serviceError").style.color = "red";
        
      }
    
    });
}

function temperature (button) {
    var tempThreshold = document.getElementById ("mytemperature").value ;
    document.getElementById("mytemperature").disabled = true;
    document.getElementById("mytemperaturebutton").disabled = true;
    if (tempThreshold === "" || tempThreshold === undefined){
        document.getElementById('serviceError').innerHTML = "Invalid Value"
        document.getElementById("serviceError").style.display= "inline";
        document.getElementById("serviceError").style.color = "red";
        document.getElementById("mytemperature").disabled = false;
        document.getElementById("mytemperaturebutton").disabled = false;
        return false
    }
    var updateCap = {
        "call": "updateService",
        "houseID": "H001",
        "deviceID": "D1",
        "data": {"service":"Threshold","properties":{"Temperature":parseInt(tempThreshold)}}
    }
  var req = new postHttpClient();
  req.responseType = 'json';
  rURL = localStorage.getItem("SC");
  req.post(rURL,updateCap, function(response) {    
    jsonResponse = JSON.parse(response);
    console.log(jsonResponse.Output)
      if (jsonResponse.Result === "success"){
        $("#success-alert").fadeTo(1000, 500).slideUp(500, function() {
            $("#success-alert").slideUp(500);});
        document.getElementById("serviceError").style.display= "none";        
        document.getElementById("mytemperature").disabled = false;
        document.getElementById("mytemperaturebutton").disabled = false;
      }
      else{        
        document.getElementById('serviceError').innerHTML = jsonResponse.Output
        document.getElementById("serviceError").style.display= "inline";
        document.getElementById("serviceError").style.color = "red";
        
      }
    
    });
}

function temperatureFEQ (button) {
    var tempFreq = document.getElementById ("mytemperatureFEQ").value ;
    document.getElementById("mytemperatureFEQ").disabled = true;
    document.getElementById("mytemperatureFEQbutton").disabled = true;
    if (tempFreq === "" || tempFreq === undefined){
        document.getElementById('serviceError').innerHTML = "Invalid Value"
        document.getElementById("serviceError").style.display= "inline";
        document.getElementById("serviceError").style.color = "red";
        document.getElementById("mytemperatureFEQ").disabled = false;
        document.getElementById("mytemperatureFEQbutton").disabled = false;
        return false
    }
    var updateCap = {
        "call": "updateService",
        "houseID": "H001",
        "deviceID": "D1",
        "data": {"service":"T-Sensors","properties":{"Frequency":parseInt(tempFreq)}}
    }
  var req = new postHttpClient();
  req.responseType = 'json';
  rURL = localStorage.getItem("SC");
  req.post(rURL,updateCap, function(response) {    
    jsonResponse = JSON.parse(response);
    console.log(jsonResponse.Output)
      if (jsonResponse.Result === "success"){
        $("#success-alert").fadeTo(1000, 500).slideUp(500, function() {
            $("#success-alert").slideUp(500);});
        document.getElementById("serviceError").style.display= "none";        
        document.getElementById("mytemperatureFEQ").disabled = false;
        document.getElementById("mytemperatureFEQbutton").disabled = false;
      }
      else{        
        document.getElementById('serviceError').innerHTML = jsonResponse.Output
        document.getElementById("serviceError").style.display= "inline";
        document.getElementById("serviceError").style.color = "red";
        
      }
    
    });
}

function plugFEQ (button) {
    var plugFreq = document.getElementById ("myplugFEQ").value ;
    document.getElementById("myplugFEQ").disabled = true;
    document.getElementById("myplugFEQbutton").disabled = true;
    if (plugFreq === "" || plugFreq === undefined){
        document.getElementById('serviceError').innerHTML = "Invalid Value"
        document.getElementById("serviceError").style.display= "inline";
        document.getElementById("serviceError").style.color = "red";
        document.getElementById("myplugFEQ").disabled = false;
        document.getElementById("myplugFEQbutton").disabled = false;
        return false
    }
    var updateCap = {
        "call": "updateService",
        "houseID": "H001",
        "deviceID": "D1",
        "data": {"service":"Plugs","properties":{"Frequency":parseInt(plugFreq)}}
    }
  var req = new postHttpClient();
  req.responseType = 'json';
  rURL = localStorage.getItem("SC");
  req.post(rURL,updateCap, function(response) {    
    jsonResponse = JSON.parse(response);
    console.log(jsonResponse.Output)
      if (jsonResponse.Result === "success"){
        $("#success-alert").fadeTo(1000, 500).slideUp(500, function() {
            $("#success-alert").slideUp(500);});
        document.getElementById("serviceError").style.display= "none";        
        document.getElementById("myplugFEQ").disabled = false;
        document.getElementById("myplugFEQbutton").disabled = false;
      }
      else{        
        document.getElementById('serviceError').innerHTML = jsonResponse.Output
        document.getElementById("serviceError").style.display= "inline";
        document.getElementById("serviceError").style.color = "red";
        
      }
    
    });
}

function msensorfrq (button) {
    var msenFreq = document.getElementById ("mymsensorFEQ").value ;
    document.getElementById("mymsensorFEQ").disabled = true;
    document.getElementById("mymsensorFEQbutton").disabled = true;
    if (msenFreq === "" || msenFreq === undefined){
        document.getElementById('serviceError').innerHTML = "Invalid Value"
        document.getElementById("serviceError").style.display= "inline";
        document.getElementById("serviceError").style.color = "red";
        document.getElementById("mymsensorFEQ").disabled = false;
        document.getElementById("mymsensorFEQbutton").disabled = false;
        return false
    }
    var updateCap = {
        "call": "updateService",
        "houseID": "H001",
        "deviceID": "D1",
        "data": {"service":"M-Sensors","properties":{"Frequency":parseInt(msenFreq)}}
    }
  var req = new postHttpClient();
  req.responseType = 'json';
  rURL = localStorage.getItem("SC");
  req.post(rURL,updateCap, function(response) {    
    jsonResponse = JSON.parse(response);
    console.log(jsonResponse.Output)
      if (jsonResponse.Result === "success"){
        $("#success-alert").fadeTo(1000, 500).slideUp(500, function() {
            $("#success-alert").slideUp(500);});
        document.getElementById("serviceError").style.display= "none";        
        document.getElementById("mymsensorFEQ").disabled = false;
        document.getElementById("mymsensorFEQbutton").disabled = false;
      }
      else{        
        document.getElementById('serviceError').innerHTML = jsonResponse.Output
        document.getElementById("serviceError").style.display= "inline";
        document.getElementById("serviceError").style.color = "red";
        
      }
    
    });
}

function addTelegramUser() {
  
  if(confirm("Do you need to add a new Telegram account?")){
    var newTelUser = document.getElementById ("addTelegramUser").value ;
    document.getElementById("addTelegramUser").disabled = true;
    document.getElementById("addTelegramUserButton").disabled = true;
    if (newTelUser === "" || newTelUser === undefined){
        document.getElementById('serviceError').innerHTML = "Invalid Value"
        document.getElementById("serviceError").style.display= "inline";
        document.getElementById("serviceError").style.color = "red";
        document.getElementById("addTelegramUser").disabled = false;
        document.getElementById("addTelegramUserButton").disabled = false;
        return false
    }
    var TelUsers = newTelUser.split(",")
    var updateCap = {
        "call": "addtelusers",
        "HouseID": "H001",        
        "Users": TelUsers
    }
    var updateSerTel = {
      "call":"addTelUser",
      "data":{"users":TelUsers,"houseID":"H001"}
    }
  var servreq = new postHttpClient();
  servreq.responseType = 'json';
  var req = new postHttpClient();
  req.responseType = 'json';
  rURL = localStorage.getItem("catalogURL");
  servURL = "http://"+localStorage.getItem("serverip")+":9292/houseservice"
  req.post(rURL,updateCap, function(response) {    
    jsonResponse = JSON.parse(response);
    
      if (jsonResponse.Result === "success"){
        servreq.post(servURL,updateSerTel, function(response) 
          {    
              jsonResponse = JSON.parse(response);
              console.log(jsonResponse.Output)
              if (jsonResponse.Result === "success")
              {
                  $("#success-alert").fadeTo(1000, 500).slideUp(500, function() {
                      $("#success-alert").slideUp(500);});
                  document.getElementById("serviceError").style.display= "none";     
                  document.getElementById ("addTelegramUser").value = ""   
                  document.getElementById("addTelegramUser").disabled = false;
                  document.getElementById("addTelegramUserButton").disabled = false;
              }
              else
              {
                document.getElementById('serviceError').innerHTML = jsonResponse.Output
                document.getElementById("serviceError").style.display= "inline";
                document.getElementById("serviceError").style.color = "red";
              }
          });
      }
      else{        
        document.getElementById('serviceError').innerHTML = jsonResponse.Output
        document.getElementById("serviceError").style.display= "inline";
        document.getElementById("serviceError").style.color = "red";
        
      }
    
    });    
  }
  else{
      return false
  }  
}
