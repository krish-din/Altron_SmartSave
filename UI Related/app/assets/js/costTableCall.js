var postHttpClient = function() { 
  this.post = function(url, data,callback) {
    var httpRequest = new XMLHttpRequest();
    httpRequest.open("POST", url, false);
    httpRequest.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    httpRequest.onreadystatechange = function() {
      if (httpRequest.readyState == 4 && httpRequest.status == 202){
        callback(httpRequest.responseText);
        console.log("success")
      }
      else{
        console.log(httpRequest.responseText)
        document.getElementById("updateError").style.color = "red";
        document.getElementById("updateError").style.display= "inline";
      }
    };     
    console.log(url);
    httpRequest.send(JSON.stringify(data));
  };
};

var deleteHttpClient = function() { 
    this.post = function(url,callback) {
      var httpRequest = new XMLHttpRequest();
      httpRequest.open("DELETE", url, false);
      httpRequest.onreadystatechange = function() {
        if (httpRequest.readyState == 4 && httpRequest.status == 200){
            console.log("succes")
          callback(httpRequest.responseText);
        }
        else{
            console.log("failed")
          document.getElementById("updateError").style.color = "red";
          document.getElementById("updateError").style.display= "inline";
        }
      };     
      httpRequest.send();
    };
  };

// $('#costDataTable > tbody').on('click', '#costedit_button3', function(){
//         var rowindex = $(this).closest('tr');
//         console.debug('Index', rowindex,rowindex.index());
//     });

function costedit_row(no)
{
  document.getElementById("costfieldempty").style.display= "none";
  
  var table1 = $('#costDataTable').DataTable();
  var rowindex = $(no).closest('tr');
  var rows = table1.row(rowindex.index()).data();
  
    console.debug('Index',rowindex.index());
//   console.log(table1.row( $(no).closest('tr') ))
//   console.log(data);
  $(':input:visible').attr('disabled', true);
  
  document.getElementById("from").value = rows[0];
  document.getElementById("to").value = rows[1];
  document.getElementById("cost").value = rows[2];
  document.getElementById("rownum").value = rowindex.index();
  
  document.getElementById("costEditForm").style.display = "block";

  

}

function updateCost()
{  
    var table = $('#costDataTable').DataTable();
 
    var data = table
        .rows()
        .data();
    var chckData=[]
    updateData={"write_api_key": "8P2YSDNH5JQEHUI3",
    "updates": []}
    // var m = new Date();
    //     var dateString =
    //     m.getUTCFullYear() + "-" +
    //     ("0" + (m.getUTCMonth()+1)).slice(-2) + "-" +
    //     ("0" + m.getUTCDate()).slice(-2) + " " +
    //     ("0" + m.getUTCHours()).slice(-2) + ":" +
    //     Math.floor(Math.random() * 50) + ":" +
    //     ("0" + m.getUTCSeconds()).slice(-2) + ":" +
    //     Math.floor(Math.random() * 50);

    for (i=0;i<data.length;i++){
        
        curData = {
                "delta_t": i,
                "field1": "Torino",
                "field2": data[i][0]+"-"+data[i][1],
                "field3": data[i][2]
            }
        updateData.updates.push(curData)        
        
    }
    console.log(updateData)
    var req = new deleteHttpClient();
    req.responseType = 'json';
    
    var rURL = sessionStorage.getItem("tsURL")+"feeds.json?api_key="+ sessionStorage.getItem("tsDeleteKey") ;
    // rURL = "https://api.thingspeak.com/channels/919852/feeds.json?api_key=Y20HZ6ZVPKSKSOR7";
    var postreq = new postHttpClient();
    // reqURL= "https://api.thingspeak.com/channels/919852/bulk_update.json"
    reqURL = sessionStorage.getItem("tsURL")+"bulk_update.json"

    req.post(rURL, function(response) {    
        postreq.post(reqURL,updateData, function(response) {  
            $("#costsuccess-alert").fadeTo(2000, 500).slideUp(500, function() {
                $("#costsuccess-alert").slideUp(500);});
        });  
        
    });    
}

window.addEventListener('load', function() {
  var houseCount = document.getElementById("altronCount");  
  houseCount.innerHTML = sessionStorage.getItem("HouseCount");
  var costbtn = document.getElementById("costUpdatebutton");
  costbtn.onclick = function(){
    document.getElementById("costfieldempty").style.display= "none";
    var editData = []
    editData.push(document.getElementById("from").value)
    editData.push(document.getElementById("to").value);
    editData.push(document.getElementById("cost").value);
    if (editData.includes("")||editData.includes(undefined)){
      document.getElementById("costfieldempty").style.display= "inline";
      document.getElementById("costfieldempty").style.color = "red";
      return false;
    }
    var table1 = $('#costDataTable').DataTable();
    rw = parseInt(document.getElementById("rownum").value)
    console.log(rw)
    table1.row( rw ).data( editData ).draw();
    var btn = $('<tr id="addNewRow" ><td id="new_from_td"><input type="number" class="form-control" style="width:80px;" min="0" max="23" id="new_from"></td>    <td id="new_to_td"><input type="number" class="form-control" min="0" max="23" style="width:15;" id="new_to" required ></td>    <td id="new_cost_td"><input type="number" min="0" class="form-control" style="width:15;" id="new_cost" required ></td><td><input type="button" id="addnewcostbutton" class="add btn btn-success btn-round btn-sm my-0 btn-fill" onclick="add_newcostrow();" value="Add new Row" ></td></tr>');
    $(btn).appendTo('#costDataTable > tbody');
    $(':input:visible').attr('disabled', false);
    document.getElementById("costEditForm").style.display = "none";  
  }
});

function costdelete_row(no)
{
  
  if (confirm("Do you want to delete?")) {
    txt = "Delete it!";
    var table1 = $('#costDataTable').DataTable();
    var rowindex = $(no).closest('tr');    
    table1.row(rowindex).remove().draw();  
    var btn = $('<tr id="addNewRow" ><td id="new_from_td"><input type="number" class="form-control" style="width:80px;" min="0" max="23" id="new_from"></td>    <td id="new_to_td"><input type="number" class="form-control" min="0" max="23" style="width:15;" id="new_to" required ></td>    <td id="new_cost_td"><input type="number" min="0" class="form-control" style="width:15;" id="new_cost" required ></td><td><input type="button" id="addnewcostbutton" class="add btn btn-success btn-round btn-sm my-0 btn-fill" onclick="add_newcostrow();" value="Add new Row" ></td></tr>');
    $(btn).appendTo('#costDataTable > tbody');
  } else {
    txt = "None";
  }
	
}

function add_newcostrow()
{
  // var tr = $('#addDevice').find('.new_name_td').text();
  // $("#plugs_data_table #addDevice").each(function() {
  //   var value = $(this).text();
  //   console.log(value);
  // })
  // var r = $("#plugs_data_table #new_name").text();
  var new_from=  $("#costDataTable #new_from_td").find("input[type='number']").val();
    var new_to= $("#costDataTable #new_to_td").find("input[type='number']").val();
	var new_cost=$("#costDataTable #new_cost_td").find("input[type='number']").val();
	
  newdata = [new_from,new_to,new_cost];
  if (newdata.includes("")||newdata.includes(undefined)){
    document.getElementById('updateError').innerHTML = "Fill all the columns to add a device"
    document.getElementById("updateError").style.display= "inline";
    document.getElementById("updateError").style.color = "red"; 
  }
  else{
    var t = $('#costDataTable').DataTable();
    t.row.add(newdata).draw();
    var table = document.getElementById("costDataTable");
    var i = table.tBodies[0].rows.length -1 ;
    
    var btns= $('<td><input id="costedit_button'+i+'" value="Edit" class="edit btn btn-info btn-round btn-sm my-0 btn-fill" onclick="costedit_row(this)" style="width: 8%;"/> <input type="" value="Delete" class="delete btn btn-danger btn-round btn-sm my-0 btn-fill" onclick="costdelete_row(this)" style="width: 10%;"/></td>');
    
    $(btns).appendTo('#costDataTable > tbody > tr:eq('+i+')');
    var btn = $('<tr id="addNewRow" ><td id="new_from_td"><input type="number" class="form-control" style="width:80px;" min="0" max="23" id="new_from"></td>    <td id="new_to_td"><input type="number" class="form-control" min="0" max="23" style="width:15;" id="new_to" required ></td>    <td id="new_cost_td"><input type="number" min="0" class="form-control" style="width:15;" id="new_cost" required ></td><td><input type="button" id="addnewcostbutton" class="add btn btn-success btn-round btn-sm my-0 btn-fill" onclick="add_newcostrow();" value="Add new Row" ></td></tr>');
    $(btn).appendTo('#costDataTable > tbody');
  } 
  
}
