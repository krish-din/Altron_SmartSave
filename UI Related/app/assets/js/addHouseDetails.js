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


function zeroFill( number, width )
{
  width -= number.toString().length;
  if ( width > 0 )
  {
    return new Array( width + (/\./.test( number ) ? 2 : 1) ).join( '0' ) + number;
  }
  return number + ""; // always return a string
}

var postHttpClient = function() { 
    this.post = function(url, data,callback) {
      var httpRequest = new XMLHttpRequest();
      httpRequest.open("POST", url, false);
      httpRequest.onreadystatechange = function() {
        if (httpRequest.readyState == 4 && httpRequest.status == 200){
          callback(httpRequest.responseText);
        }
        else{
            document.getElementById('addError').innerHTML = httpRequest.responseText
            document.getElementById("addError").style.color = "red";
            document.getElementById("addError").style.display= "inline";
        }
      };     
      httpRequest.send(JSON.stringify(data));
    };
  };


window.addEventListener('load', function() {
    document.getElementById('houseID').value = "";
    document.getElementById('catalogURL').value = "";    
    document.getElementById('deviceID').value = "";
    document.getElementById("plugLimit").value = "";   
    document.getElementById("pirLimit").value = "";
    document.getElementById("tempLimit").value = "";
    houseNumbers = []
    req.post(rURL, function(response) {    
      jsonResponse = JSON.parse(response);
      houseIDs = jsonResponse.Output;
      });
    for (const val of houseIDs){
        houseNumbers.push(parseInt(val.substring(1)))
    }
    console.log(houseNumbers)
    lastHouseNumber =  Math.max.apply(0, houseNumbers );
    console.log(lastHouseNumber)
    document.getElementById('houseID').value = "H"+zeroFill(lastHouseNumber+1,3)
    // "H"+zeroFill(parseInt(sessionStorage.getItem("HouseIDs").split(",")[0].substring(1))+1,3)
});

function addHouse (button) {
    var houseID = document.getElementById('houseID').value
    var newCatURL = document.getElementById('catalogURL').value       
    var newDevID = document.getElementById('deviceID').value   
    var newPlugLimit = document.getElementById("plugLimit").value    
    var newPIRLimit = document.getElementById("pirLimit").value 
    var newtempLimit = document.getElementById("tempLimit").value
    
    document.getElementById('catalogURL').disabled = true;       
    document.getElementById("deviceID").disabled = true;
    document.getElementById("plugLimit").disabled = true; 
    document.getElementById("pirLimit").disabled = true;
    document.getElementById("tempLimit").disabled = true;
    document.getElementById("addHouse").disabled = true;
    
    var updateHouse = {
        "call": "addHouse",
        "data": {"houseID":houseID,"catalogURL":newCatURL,"deviceID":newDevID,"plugLimit":newPlugLimit,"tempLimit":newtempLimit,"pirLimit":newPIRLimit}
    }
    if (newCatURL === "" || newCatURL === undefined||newDevID === "" || newDevID === undefined||newPlugLimit === "" || newPlugLimit === undefined|| newPIRLimit === "" || newPIRLimit === undefined||newtempLimit === "" || newtempLimit === undefined){
        document.getElementById('addError').innerHTML = "Fill all fields"
        document.getElementById("addError").style.display= "inline";
        document.getElementById("addError").style.color = "red";
        document.getElementById('catalogURL').disabled = false;       
        document.getElementById("deviceID").disabled = false;
        document.getElementById("plugLimit").disabled = false; 
        document.getElementById("pirLimit").disabled = false;
        document.getElementById("tempLimit").disabled = false;
        document.getElementById("addHouse").disabled = false;
        return false
    }
  var req = new postHttpClient();
  req.responseType = 'json';
  rURL ="http://"+sessionStorage.getItem("serverIP")+":9292/houseservice" ;
  req.post(rURL,updateHouse, function(response) {    
    jsonResponse = JSON.parse(response);
    console.log(jsonResponse.Output)
      if (jsonResponse.Result === "success"){
        $("#addsuccess-alert").fadeTo(1000, 500).slideUp(500, function() {
            $("#addsuccess-alert").slideUp(500);});
        document.getElementById("addError").style.display= "none"; 
        document.getElementById('catalogURL').disabled = false;       
        document.getElementById("deviceID").disabled = false;
        document.getElementById("plugLimit").disabled = false; 
        document.getElementById("pirLimit").disabled = false;
        document.getElementById("tempLimit").disabled = false;
        document.getElementById("addHouse").disabled = false;
        location.reload()
      }
      else{        
        document.getElementById('addError').innerHTML = jsonResponse.Output
        document.getElementById("addError").style.display= "inline";
        document.getElementById("addError").style.color = "red";
        document.getElementById('catalogURL').disabled = false;       
        document.getElementById("deviceID").disabled = false;
        document.getElementById("plugLimit").disabled = false; 
        document.getElementById("pirLimit").disabled = false;
        document.getElementById("tempLimit").disabled = false;
        document.getElementById("addHouse").disabled = false;
        
      }
    
    });
}