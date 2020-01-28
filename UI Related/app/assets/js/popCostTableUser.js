var getHttpClient = function() { 
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

  
var rURL = localStorage.getItem("costAPI")+"feeds.json?api_key="+ localStorage.getItem("costKey") ;
var req = new getHttpClient();
req.responseType = 'json';

req.post(rURL, function(response) {
    jsonResponse = JSON.parse(response);
    var costph = jsonResponse.feeds
    var data = []
    costph.forEach(function (value, i) {
      data.push([]);
      data[i].push(value.field2.split("-")[0]);
      data[i].push(value.field2.split("-")[1]);
      data[i].push(value.field3);
    })
   
    
    //populating plugs datatable
    $('#costDataTableUser').DataTable({
        processing: true,
        responsive: true,
      paging: false,
      searching: false,
      data:data,
      
      "bAutoWidth": false,
      "bSort": false,
      "bInfo" : false,
        "columns":[
            {data:0},
            {data:1},
            {data:2}
        ]
    });    
});
