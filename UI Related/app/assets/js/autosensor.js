/*document.getElementById("sensorMode").disabled = true;
document.getElementById("sensorMode").disabled = false;*/

/*function ifServerOnline(ifOnline, ifOffline)
{
    var img = document.body.appendChild(document.createElement("img"));
    img.onload = function()
    {
        ifOnline && ifOnline.constructor == Function && ifOnline();
    };
    img.onerror = function()
    {
        ifOffline && ifOffline.constructor == Function && ifOffline();
    };
    img.src = "http://myserver.com/ping.gif";  //sensor status give status and call img to show on page      
}

ifServerOnline(function()
{
    //  server online code here --> Our sensor
},
function ()
{
    //  server offline code here --> Our sensor
});*/
/*
function statusMode(mySwitch) {
    switch (mySwitch)
    {
    case "On":
        alert("Sensor is ON");
        break
    case "Off":
        alert("Sensor is OFF");
        break
    default:
        alert("Suit yourself then...");
    }
}

function doStuff() {
    console.log("Hello World!")
}
function toggle(button) {
    if(button.value=="OFF") {
        button.value="ON"
        button.innerHTML="ON"
        this.interval = setInterval(doStuff, 1000);
    } else if(button.value=="ON") {
        button.value="OFF"
        button.innerHTML="OFF"
        clearInterval(this.interval)
    }
}*/
