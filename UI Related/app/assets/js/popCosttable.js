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

  
var rURL = sessionStorage.getItem("tsURL")+"feeds.json?api_key="+ sessionStorage.getItem("tsReadKey") ;

var req = new getHttpClient();
req.responseType = 'json';
var plugID = "plugcards"

req.post(rURL, function(response) {
    console.log(response)
    
    jsonResponse = JSON.parse(response);
    console.log(jsonResponse.feeds)
    var costph = jsonResponse.feeds
    var data = []
    costph.forEach(function (value, i) {
      data.push([]);
      data[i].push(value.field2.split("-")[0]);
      data[i].push(value.field2.split("-")[1]);
      data[i].push(value.field3);
    })
   
    
    //populating plugs datatable
    $('#costDataTable').DataTable({
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
    
    var table = document.getElementById("costDataTable");
    var tbodyRowCount = table.tBodies[0].rows.length;
    // console.log(tbodyRowCount)
    for (i = 0; i < tbodyRowCount; i++) { 
        var btns= $('<td><input id="costedit_button'+i+'" value="Edit" class="edit btn btn-info btn-round btn-sm my-0 btn-fill" onclick="costedit_row(this)" style="width: 8%;"/> <input type="" value="Delete" class="delete btn btn-danger btn-round btn-sm my-0 btn-fill" onclick="costdelete_row(this)" style="width: 10%;"/></td>');
        
      // var btns= $('<td><input type="checkbox" id="checkbox'+i+'"> </td>');onclick="costedit_row(this)"
      $(btns).appendTo('#costDataTable > tbody > tr:eq('+i+')');
    }
    
    // $('#costDataTable > tbody').on('click', '#costedit_button3', function(){
    //     var rowindex = $(this).closest('tr');
    //     console.debug('Index', rowindex,rowindex.index());
    // });
    var table = $('#costDataTable').DataTable();
    
    var btn = $('<tr id="addNewRow" ><td id="new_from_td"><input type="number" class="form-control" style="width:80px;" min="0" max="23" id="new_from"></td>    <td id="new_to_td"><input type="number" class="form-control" min="0" max="23" style="width:15;" id="new_to" required ></td>    <td id="new_cost_td"><input type="number" min="0" class="form-control" style="width:15;" id="new_cost" required ></td><td><input type="button" id="addnewcostbutton" class="add btn btn-success btn-round btn-sm my-0 btn-fill" onclick="add_newcostrow();" value="Add new Row" ></td></tr>');
    $(btn).appendTo('#costDataTable > tbody');

    
    
    // console.log($('*[id*=button]:visible'))
});
