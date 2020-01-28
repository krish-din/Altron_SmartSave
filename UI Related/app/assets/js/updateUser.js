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

function updateUser(updateData)
{  
  addUserData = {
    "call":"updateUser",
    "Users":{"name":updateData[0],"paswd":updateData[1]}
  }  
  var req = new postHttpClient();
  req.responseType = 'json';
  rURL = "http://127.0.0.1:9191/loginservice"
  req.post(rURL,addUserData, function(response) {    
    jsonResponse = JSON.parse(response);
      if (jsonResponse.Result === "success"){
        document.getElementById('error').innerHTML = "Updated"
        document.getElementById("error").style.display= "inline";
        document.getElementById("error").style.color = "green";       
        location.href=window.location.href.replace('/newpassword','/login');
      }
      else{        
        document.getElementById('error').innerHTML = jsonResponse.Output
        document.getElementById("error").style.display= "inline";
        document.getElementById("error").style.color = "red";   
      }
    
    });  
}

window.addEventListener('load', function() {
  
    var updatePwdBtn = document.getElementById("updatepwd");
    updatePwdBtn.onclick = function(){
      document.getElementById("error").style.display= "none";
      var updateData = []
      updateData.push(document.getElementById("updateEmail").value)
      updateData.push(document.getElementById("upinputPassword").value);
      updateData.push(document.getElementById("upreinputPassword").value);
      
      
      if (updateData.includes("")||updateData.includes(undefined)){
        document.getElementById('error').innerHTML = "* Enter All Values"
        document.getElementById("error").style.display= "inline";
        document.getElementById("error").style.color = "red";
        return false;
      }
      else if (updateData[1] != updateData[2]){
        document.getElementById('error').innerHTML = "Passwords doesn't match"
        document.getElementById("error").style.display= "inline";
        document.getElementById("error").style.color = "red";
        return false;
      }
      else{
        updateUser(updateData)        
      }
    }
  });