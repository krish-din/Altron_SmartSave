
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
var list1 = document.getElementById('dropdown-menu');
list1.options[0] = new Option('All', 'all');

var sensors = JSON.parse(localStorage.getItem("SensorIDs"))
var sensorNames = JSON.parse(localStorage.getItem("Sensors"))

for (const val of sensors){
  if (val.indexOf("plug") >= 0){
      list1.options[list1.options.length] = new Option(sensorNames[val], val);}
  }

var sel = sessionStorage.getItem("selected");
if (sel){
  list1.options[sel].selected = true;
}

