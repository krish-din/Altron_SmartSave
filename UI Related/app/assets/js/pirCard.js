
var plugID = "pircards"
var sensors = JSON.parse(localStorage.getItem("SensorIDs"))
var sensorNames = JSON.parse(localStorage.getItem("Sensors"))


for (const val of sensors)
{
    if (val.indexOf("PIR") >= 0){
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
            var btn = $('<div class="row">    <div class="col-sm-4">        <h5 style="text-align: left;">'+sensorNames[val]+'</h5>    </div>    <div class="col-sm-8" style="text-align: right;">        <label class="switch">            <input type="checkbox" disabled="disabled" id='+val+' '+chkd +'">            <div class="slider round">                <span class="on">Yes</span>                <span class="off">No</span>            </div>        </label>    </div></div>');
            $(btn).appendTo('#'+plugID);
        });
        
    }
}
var btn = $('<div class="footer"><hr><div class="stats"><div class="legend"><i class="fa fa-circle text-success"></i> Presence<i class="fa fa-circle text-danger"></i> No presence</div></div></div>');
$(btn).appendTo('#'+plugID);
    
  