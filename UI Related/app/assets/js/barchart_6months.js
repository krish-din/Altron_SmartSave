 //bars
var ctxB = document.getElementById("barChart").getContext('2d');
var list1 = document.getElementById('dropdown-menu');
var strUser = list1.options[list1.selectedIndex].value;
const values = []; 
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
 var rURL = localStorage.getItem("dataAPI")+"/getmonthly?data=sensor&type=Plugs&ID="+strUser;
 req.post(rURL, function(response) {
   jsonResponse = JSON.parse(response);
   console.log(jsonResponse.Output);  
   for (const val of jsonResponse.Output){
     values.push(val);}
   });
  var myBarChart = new Chart(ctxB, {
    type: 'bar',
    data: {
      labels: [ "Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6"],
      datasets: [{
        label: 'Power Usage',
        data: values,
        backgroundColor: [
          'rgba(255, 99, 132, 0.2)',
          'rgba(255, 206, 86, 0.2)',
          'rgba(75, 192, 192, 0.2)',
          'rgba(75, 192, 192, 0.2)',
          'rgba(255, 159, 64, 0.2)',
          'rgba(54, 162, 235, 0.2)'
        ],
        borderColor: [
          'rgba(255,99,132,1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(255, 159, 64, 1)',
          'rgba(54, 162, 235, 1)'
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

