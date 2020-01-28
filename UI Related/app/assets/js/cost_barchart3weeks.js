 //bar

var ctxB = document.getElementById("costChart").getContext('2d');
var list1 = document.getElementById('dropdown-menu');
var strUser = list1.options[list1.selectedIndex].value;
const costvalues = []; 
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
 var req = new HttpClient();
 req.responseType = 'json';
 var rURL = localStorage.getItem("dataAPI")+"/getweekly?data=cost&type=Plugs&ID="+strUser;
 req.post(rURL, function(response) {
   jsonResponse = JSON.parse(response);
   console.log(jsonResponse.Output);  
   for (const val of jsonResponse.Output){
    costvalues.push(val);}
   });
  var myBarChart = new Chart(ctxB, {
    type: 'bar',
    data: {
      labels: [ "Week 1", "Week 2", "Week 3"],
      datasets: [{
        label: 'Cost',
        data: costvalues,
        backgroundColor: [
          'rgba(255, 99, 132, 0.2)',
          'rgba(255, 206, 86, 0.2)',
          'rgba(75, 192, 192, 0.2)'
        ],
        borderColor: [
          'rgba(255,99,132,1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          }
        }]
      }
    }
  });

  