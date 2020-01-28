// const mqttclient = new Paho.MQTT.Client("ws://test.mosquitto.org",Number(8080), "myClientId" + new Date().getTime());
// mqttclient.connect({onSuccess:onConnect});

// function onConnect() {
//     // Once a connection has been made, make a subscription and send a message.
//     console.log("Connected");
//   }
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
var plugID = "plugcards"
var sensors = JSON.parse(localStorage.getItem("SensorIDs"))
var sensorNames = JSON.parse(localStorage.getItem("Sensors"))
console.log(sensors)
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
                var chkd= ""
            }
            var btn = $('<div class="row">    <div class="col-sm-4">        <h5 style="text-align: left;">'+sensorNames[val]+'</h5>    </div>    <div class="col-sm-8" style="text-align: right;">        <label class="switch" style="text-align: right;">            <input  align =“right”  type="checkbox" id='+val+' '+chkd +'">            <div class="slider round">                <span class="on">Yes</span>                <span class="off">No</span>            </div>        </label>    </div></div>');
            $(btn).appendTo('#'+plugID);
        });
        
    }
}
var req1 = new postHttpClient();
var HouseID = localStorage.getItem("HouseID")
var deviceID = localStorage.getItem("deviceID")
req1.responseType = 'json';
reqURL = localStorage.getItem("statusAPI");
var btn = $('<div class="footer"><hr><div class="stats"><div class="legend"><i class="fa fa-circle text-success"></i> On<i class="fa fa-circle text-danger"></i> Off</div></div></div>');
$(btn).appendTo('#'+plugID);
$('#'+plugID).on('click', ':checkbox', function(event){
    if (this.checked){
        // message = new Paho.MQTT.Message(JSON.stringify({"Appliance_Name": sensorNames[event.target.id], "value": "On"}));
        // message.destinationName = 'house/' + HouseID + '/plugwise/' + event.target.id + '/action';
        // mqttclient.send(message);
        data = {"call": "updateSensorWeb","data": {"sensorID": event.target.id,"sensorName":sensorNames[event.target.id], "status":"On"}}
        // console.log(data)
        // console.log("chkd"+event.target.id)
        req1.post(reqURL,data, function(response) {
        
        jsonResponse = JSON.parse(response);
        
        });
    } else {
        // message = new Paho.MQTT.Message(JSON.stringify({"Appliance_Name": sensorNames[event.target.id], "value": "Off"}));
        // message.destinationName = 'house/' + HouseID + '/plugwise/' + event.target.id + '/action';
        // mqttclient.send(message);
        data = {"call": "updateSensorWeb","data": {"sensorID": event.target.id,"sensorName":sensorNames[event.target.id], "status":"Off"}}
        req1.post(reqURL,data, function(response) {
        // console.log(response)
        jsonResponse = JSON.parse(response);
        // console.log("unchkd"+event.target.id)
        });            
    } 
});


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