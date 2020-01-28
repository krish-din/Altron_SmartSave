var postHttpClient = function() { 
    this.post = function(url, data,callback) {
      var httpRequest = new XMLHttpRequest();
      httpRequest.open("POST", url, false);
      httpRequest.onreadystatechange = function() {
        if (httpRequest.readyState == 4 && httpRequest.status == 200){
          callback(httpRequest.responseText);
        }
        else{
            document.getElementById('error').innerHTML = httpRequest.responseText
            document.getElementById("error").style.color = "red";
            document.getElementById("error").style.display= "inline";
        }
      };     
      httpRequest.send(JSON.stringify(data));
    };
  };

function registerUser(regData)
{  
  addUserData = {
    "call":"addUser",
    "Users":{"name":regData[0],"paswd":regData[1],"houseID":regData[3]}
  }
  console.log(addUserData)
  var req = new postHttpClient();
  req.responseType = 'json';
  rURL = rURL ="http://"+localStorage.getItem("serverIP")+":9191/loginservice"
  req.post(rURL,addUserData, function(response) {    
    jsonResponse = JSON.parse(response);
    console.log(jsonResponse.Output)
      if (jsonResponse.Result === "success"){
        document.getElementById('error').innerHTML = "Registered"
        document.getElementById("error").style.display= "inline";
        document.getElementById("error").style.color = "green";       
        location.href=window.location.href.replace('/registra','/login');
      }
      else{        
        document.getElementById('error').innerHTML = jsonResponse.Output
        document.getElementById("error").style.display= "inline";
        document.getElementById("error").style.color = "red";   
      }
    
    });  
}

window.addEventListener('load', function() {
  
    var registerBtn = document.getElementById("registerBtn");
    registerBtn.onclick = function(){
      document.getElementById("error").style.display= "none";
      var regData = []
      regData.push(document.getElementById("email").value)
      regData.push(document.getElementById("inputPassword").value);
      regData.push(document.getElementById("reinputPassword").value);
      regData.push(document.getElementById("houseID").value);
      
      if (regData.includes("")||regData.includes(undefined)){
        document.getElementById('error').innerHTML = "* Enter All Values"
        document.getElementById("error").style.display= "inline";
        document.getElementById("error").style.color = "red";
        return false;
      }
      else if (regData[1] != regData[2]){
        document.getElementById('error').innerHTML = "Passwords doesn't match"
        document.getElementById("error").style.display= "inline";
        document.getElementById("error").style.color = "red";
        return false;
      }
      else{
        registerUser(regData)        
      }
    }
  });