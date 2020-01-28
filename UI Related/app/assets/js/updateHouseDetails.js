var postHttpClient = function() { 
    this.post = function(url, data,callback) {
      var httpRequest = new XMLHttpRequest();
      httpRequest.open("POST", url, false);
      httpRequest.onreadystatechange = function() {
        if (httpRequest.readyState == 4 && httpRequest.status == 200){
          callback(httpRequest.responseText);
        }
        else{
            document.getElementById('updateError').innerHTML = httpRequest.responseText
            document.getElementById("updateError").style.color = "red";
            document.getElementById("updateError").style.display= "inline";
        }
      };     
      httpRequest.send(JSON.stringify(data));
    };
  };

function getHouseInfo(houseID)
{  
  addUserData = {
    "call": "getInfo",
    "data": {"by": "houseID", "input": houseID}
} 
  var req = new postHttpClient();
  req.responseType = 'json';
  rURL ="http://"+sessionStorage.getItem("serverIP")+":9292/houseservice";
  req.post(rURL,addUserData, function(response) {    
    jsonResponse = JSON.parse(response);
      if (jsonResponse.Result === "success"){
        document.getElementById('updatecatalogURL').value = jsonResponse.Output["catalogURL"];        
        document.getElementById("updateplugLimit").value = jsonResponse.Output["plugLimit"];       
        document.getElementById("updatepirLimit").value = jsonResponse.Output["pirLimit"];   
        document.getElementById("updatetempLimit").value = jsonResponse.Output["tempLimit"];   
        
      }
      else{        
        document.getElementById('updateError').innerHTML = jsonResponse.Output
        document.getElementById("updateError").style.display= "inline";
        document.getElementById("updateError").style.color = "red";   
      }
    
    });  
}

window.addEventListener('load', function() {
    var list1 = document.getElementById('housedropdown');
    list1.onchange = function(){
        var houseID = list1.options[list1.selectedIndex].value
        if (houseID == "noVal"){
            document.getElementById('updatecatalogURL').value = "";        
            document.getElementById("updateplugLimit").value = "";
            document.getElementById("updatepirLimit").value = "";  
            document.getElementById("updatetempLimit").value = "";
        }
        else{
            getHouseInfo(houseID)
        }
    }
});

function updateHouse (button) {
    var houseID = list1.options[list1.selectedIndex].value
    var newCatURL = document.getElementById('updatecatalogURL').value       
    var newPlugLimit = document.getElementById("updateplugLimit").value
    var newPIRLimit = document.getElementById("updatepirLimit").value 
    var newtempLimit = document.getElementById("updatetempLimit").value
    document.getElementById('housedropdown').disabled = true
    document.getElementById('updatecatalogURL').disabled = true;       
    document.getElementById("updateplugLimit").disabled = true;
    document.getElementById("updatepirLimit").disabled = true; 
    document.getElementById("updatetempLimit").disabled = true;
    document.getElementById("updateHouse").disabled = true;
    
    var updateHouse = {
        "call": "updateHouse",
        "data": {"houseID":houseID,"catalogURL":newCatURL,"plugLimit":newPlugLimit,"tempLimit":newtempLimit,"pirLimit":newPIRLimit}
    }
    if (newCatURL === "" || newCatURL === undefined||newPlugLimit === "" || newPlugLimit === undefined|| newPIRLimit === "" || newPIRLimit === undefined||newtempLimit === "" || newtempLimit === undefined){
        document.getElementById('updateError').innerHTML = "Fill all fields"
        document.getElementById("updateError").style.display= "inline";
        document.getElementById("updateError").style.color = "red";
        document.getElementById('housedropdown').disabled = false;
        document.getElementById('updatecatalogURL').disabled = false;       
        document.getElementById("updateplugLimit").disabled = false;
        document.getElementById("updatepirLimit").disabled = false; 
        document.getElementById("updatetempLimit").disabled = false;
        document.getElementById("updateHouse").disabled = false;
        return false
    }
  var req = new postHttpClient();
  req.responseType = 'json';
  rURL = rURL ="http://"+sessionStorage.getItem("serverIP")+":9292/houseservice" ;
  req.post(rURL,updateHouse, function(response) {    
    jsonResponse = JSON.parse(response);
    console.log(jsonResponse.Output)
      if (jsonResponse.Result === "success"){
        $("#updatesuccess-alert").fadeTo(1000, 500).slideUp(500, function() {
            $("#updatesuccess-alert").slideUp(500);});
        document.getElementById("updateError").style.display= "none"; 
        document.getElementById('housedropdown').disabled = false;       
        document.getElementById('updatecatalogURL').disabled = false;       
        document.getElementById("updateplugLimit").disabled = false;
        document.getElementById("updatepirLimit").disabled = false; 
        document.getElementById("updatetempLimit").disabled = false;
        document.getElementById("updateHouse").disabled = false;
      }
      else{        
        document.getElementById('updateError').innerHTML = jsonResponse.Output
        document.getElementById("updateError").style.display= "inline";
        document.getElementById("updateError").style.color = "red";
        document.getElementById('housedropdown').disabled = false;       
        document.getElementById('updatecatalogURL').disabled = false;       
        document.getElementById("updateplugLimit").disabled = false;
        document.getElementById("updatepirLimit").disabled = false; 
        document.getElementById("updatetempLimit").disabled = false;
        document.getElementById("updateHouse").disabled = false;
        
      }
    
    });
}