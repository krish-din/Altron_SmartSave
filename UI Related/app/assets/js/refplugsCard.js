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
var rURL = localStorage.getItem("catalogURL") + '/getsensorInfo/' + localStorage.getItem("HouseID")+'/' + localStorage.getItem("deviceID") ;

var req = new HttpClient();
req.responseType = 'json';
var plugID = "plugcards"

req.post(rURL, function(response) {
    console.log(response)
    
    jsonResponse = JSON.parse(response);
    var sensors = jsonResponse.Output.Devices[localStorage.getItem("deviceID")]["Sensors"]
    for (const val of sensors)
    {
        if (val.indexOf("plug") >= 0){
            var req = new HttpClient();
            req.responseType = 'json';
            var rURL= localStorage.getItem("statusAPI")+"/getstatus/"+val
            req.post(rURL, function(response) {
                jsonResponse = JSON.parse(response);
                if (jsonResponse.Output){
                    var chkd= "checked=true"
                }
                else{
                    var chkd= "checked"
                }
                var btn = $('<div class="row">    <div class="col-sm-4">        <h5 style="text-align: center;">'+val+'</h5>    </div>    <div class="col-sm-8" style="text-align: left;">        <label class="switch">            <input type="checkbox" id='+val+' '+chkd +'">            <div class="slider round">                <span class="on">Yes</span>                <span class="off">No</span>            </div>        </label>    </div></div>');
                $(btn).appendTo('#'+plugID);
            });
            
        }
    }


    
// $(document).ready(function(){
//     console.log("working")
//     var tboxValue  = "fsd"
//     var plugID = "plugcards"
//     var chkd= "checked=true"
//     var btn = $('<div class="row">    <div class="col-sm-4">        <h5 style="text-align: center;">Plug 1</h5>    </div>    <div class="col-sm-8" style="text-align: left;">        <label class="switch">            <input type="checkbox" name="def" id="togBtn"'+chkd +'">            <div class="slider round">                <span class="on">Yes</span>                <span class="off">No</span>            </div>        </label>    </div></div>');
// $(btn).appendTo('#'+plugID);
// var chkd= "checked"
// var btn = $('<div class="row">    <div class="col-sm-4">        <h5 style="text-align: center;">Plug 2</h5>    </div>    <div class="col-sm-8" style="text-align: left;">        <label class="switch">            <input type="checkbox" name="def1" id="togBtn1"'+chkd +'">            <div class="slider round">                <span class="on">Yes</span>                <span class="off">No</span>            </div>        </label>    </div></div>');
// $(btn).appendTo('#'+plugID);

// $('#'+plugID).on('click', ':checkbox', function(event){
//     if (this.checked){
//     console.log(event.target.id)
//     } else {
//         console.log("unchckd")   
//     } 
// });
// });

// console.log($('input[name=def]').attr('checked'))
// var box = document.getElementById('togBtn')
// box.checked = true
// document.getElementById('togBtn').addEventListener('change',function() {
    
//     console.log(box.checked);
// });