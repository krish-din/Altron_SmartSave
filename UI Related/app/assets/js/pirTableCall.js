var postHttpClient = function() { 
  this.post = function(url, data,callback) {
    var httpRequest = new XMLHttpRequest();
    httpRequest.open("POST", url, false);
    httpRequest.onreadystatechange = function() {
      if (httpRequest.readyState == 4 && httpRequest.status == 200){
        callback(httpRequest.responseText);
      }
      else{
        document.getElementById("pirupdateError").style.color = "red";
        document.getElementById("pirupdateError").style.display= "inline";
      }
    };     
    httpRequest.send(JSON.stringify(data));
  };
};

function piredit_row(no)
{
  document.getElementById("pirempty").style.display= "none";
  console.log(no)
  var table1 = $('#pir_data_table').DataTable();
  var rows = table1.row(no).data();
  $(':input:visible').attr('disabled', true);
  document.getElementById("pirdevID").value = rows[0];
  document.getElementById("pirdevName").value = rows[1];
  document.getElementById("pirroom").value = rows[2];
  document.getElementById("pirGPIO").value = rows[3];
  
  document.getElementById("pirEditForm").style.display = "block";

  

}

function pirupdate_row(editeddata)
{  
    
  updatePostCall = {
    "call":"updateDevices",
    "houseID":localStorage.getItem("HouseID"),
    "deviceID":localStorage.getItem("deviceID"),
    "catalogURL":localStorage.getItem("catalogURL"),
    "data":{"sensor":"M-Sensors","sensorID":editeddata[0],"properties":{"Name":editeddata[1],"Room":editeddata[2]}}
    
  }
  var req = new postHttpClient();
  req.responseType = 'json';
  rURL = localStorage.getItem("DC");
  req.post(rURL,updatePostCall, function(response) {    
    jsonResponse = JSON.parse(response);
    console.log(jsonResponse.Output)
      if (jsonResponse.Result === "success"){
        document.getElementById("pirupdateError").style.display= "none";
        document.getElementById("pirEditForm").style.display = "none";        
        location.reload();
      }
      else{        
        document.getElementById('pirupdateError').innerHTML = jsonResponse.Output
        document.getElementById("pirupdateError").style.display= "inline";
        document.getElementById("pirupdateError").style.color = "red";
        document.getElementById("pirEditForm").style.display = "none";  
      }
    
    });
  console.log(editeddata);
}

window.addEventListener('load', function() {
  
  var btn = document.getElementById("pirUpdatebutton");
  btn.onclick = function(){
    

    document.getElementById("pirempty").style.display= "none";
    var editData = []
    editData.push(document.getElementById("pirdevID").value)
    editData.push(document.getElementById("pirdevName").value);
    editData.push(parseInt(document.getElementById("pirroom").value));
    editData.push(parseInt(document.getElementById("pirGPIO").value));
    if (editData.includes("")||editData.includes(undefined)){
      document.getElementById("pirempty").style.display= "inline";
      document.getElementById("pirempty").style.color = "red";
      return false;
    }
    // for(var i=0;i<editData.length;i++){
    //   if(editData[i] === "")   {
    //      document.getElementById("empty").style.display= "inline";
    //      return false;}
    // }
    
    pirupdate_row(editData);
   
  }
});

function pirdelete_row(no)
{
  
  if (confirm("Do you want to delete?")) {
    txt = "Delete it!";
    var table1 = $('#pir_data_table').DataTable();
    deleteDevice = {
      "call":"removeDevice",
      "houseID":localStorage.getItem("HouseID"),
      "deviceID":localStorage.getItem("deviceID"),
      "catalogURL":localStorage.getItem("catalogURL"),
      "statusURL":localStorage.getItem("statusAPI"),
      "data":{"sensor":"M-Sensors","sensorID":table1.row(no).data()[0]}      
    }
    var req = new postHttpClient();
    req.responseType = 'json';
    rURL = localStorage.getItem("DC");
    req.post(rURL,deleteDevice, function(response) {    
      jsonResponse = JSON.parse(response);
      console.log(jsonResponse.Output)
        if (jsonResponse.Result === "success"){
          var selectRows = table1.row(no).remove().draw();  
          location.reload();
        }
        else{        
          document.getElementById('pirupdateError').innerHTML = jsonResponse.Output
          document.getElementById("pirupdateError").style.display= "inline";
          document.getElementById("pirupdateError").style.color = "red";          
        }
      
      });
   
  } else {
    txt = "None";
  }
	
}

function piradd_row()
{
  // var tr = $('#addDevice').find('.new_name_td').text();
  // $("#plugs_data_table #addDevice").each(function() {
  //   var value = $(this).text();
  //   console.log(value);
  // })
  // var r = $("#plugs_data_table #new_name").text();
  var new_id=  $("#pir_data_table #new_pirid_td").find("input[type='text']").val();
  var new_name= $("#pir_data_table #new_pirname_td").find("input[type='text']").val();
  var new_room=$("#pir_data_table #new_pirroom_td").find("input[type='number']").val();
  var new_gpio=$("#pir_data_table #new_pirGPIO_td").find("input[type='number']").val();

  var addDevice = {
    "call":"addDevice",
    "houseID":localStorage.getItem("HouseID"),
    "deviceID":localStorage.getItem("deviceID"),
    "catalogURL":localStorage.getItem("catalogURL"),
    "statusURL":localStorage.getItem("statusAPI"),
    "data":{"sensor":"M-Sensors","properties":{
              "Name":new_name,          
              "active": 1,
              "ID": new_id,
              "Room": parseInt(new_room),
              "GPIO": parseInt(new_gpio)}}
    
    }
  newdata = [new_id,new_name,new_presence,new_control,new_restart,new_room,new_mac];
  if (newdata.includes("")||newdata.includes(undefined)){
    document.getElementById('pirupdateError').innerHTML = "Fill all the columns to add a device"
    document.getElementById("pirupdateError").style.display= "inline";
    document.getElementById("pirupdateError").style.color = "red"; 
  }
  else{
    var req = new postHttpClient();
    req.responseType = 'json';
    rURL = localStorage.getItem("DC");
    req.post(rURL,addDevice, function(response) {    
      jsonResponse = JSON.parse(response);
      console.log(jsonResponse.Output)
        if (jsonResponse.Result === "success"){
          
          location.reload();
        }
        else{        
          document.getElementById('pirupdateError').innerHTML = jsonResponse.Output
          document.getElementById("pirupdateError").style.display= "inline";
          document.getElementById("pirupdateError").style.color = "red";          
        }      
      
      });
  }
  
  
   
  // console.log(table.tBodies[0].rows.length)
  // table.row( 0 ).data( newData ).draw();
  // table.cell({row: rowindex, column: colindex}).data(msg[coldata]) 
  // table
  //   .row( 0 )
  //   .invalidate()
  //   .draw()
  // // var table_len=document.getElementById('plugs_data_table').rows[0].cells.length;
 
  
  // var t = $('#plugs_data_table').DataTable();
        // t.row.add( [new_id,new_name,new_presence,new_control,new_restart,new_room,new_mac]).draw();
      
        // var btns= $('<td align="center" ><input id="edit_button'+i+'" value="Edit" class="edit btn btn-info btn-round btn-sm my-0 btn-fill" onclick="edit_row('+i+')" style="width: 15%;"/>    <input type="" id="save_button'+i+'" value="Save" class="save btn btn-primary btn-round btn-sm my-0 btn-fill" onclick="save_row('+i+')" style="width: 15%;"/>    <input type="" value="Delete" class="delete btn btn-danger btn-round btn-sm my-0 btn-fill" onclick="delete_row('+i+')" style="width: 18%;"/> </td>');
        //     // var btns= $('<td><input type="checkbox" id="checkbox'+i+'"> </td>');
        // $(btns).appendTo('#plugs_data_table > tbody > tr:eq('+i+')');
        // // // var row = table.insertRow(table_len).outerHTML="<tr id='row"+table_len+"'><td id='name_row"+table_len+"'>"+new_name+"</td><td id='presence_row"+table_len+"'>"+new_presence+"</td><td id='control_row"+table_len+"'>"+new_control+"</td><td id='restart_row"+table_len+"'>"+new_restart+"</td><td id='room_row"+table_len+"'>"+new_room+"</td><td id='mac_row"+table_len+"'>"+new_mac+"</td><td><input type='button' id='edit_button"+table_len+"' value='Edit' class='edit btn btn-info btn-round btn-sm my-0 btn-fill' style='width: 18%;' onclick='edit_row("+table_len+")'> <input type='button' class='save btn btn-primary btn-round btn-sm my-0 btn-fill' style='width: 18%;' id='save_button"+table_len+"' value='Save' onclick='save_row("+table_len+")'> <input type='button' value='Delete' class='delete btn btn-danger btn-round btn-sm my-0 btn-fill' style='width: 18%;' onclick='delete_row("+table_len+")'></td></tr>";
        // var btn = $('<tr id="addDevice" ><td id="new_id_td"><input type="text" class="form-control" style="width:15;" id="new_id"></td>    <td id="new_name_td"><input type="text" class="form-control" style="width:15;" id="new_name"></td>    <td id="new_presence_td"><input type="text" class="form-control" style="width:15;" id="new_presence"></td>    <td id="new_control_td"><input type="text" class="form-control" style="width:15;" id="new_control"></td>    <td id="new_restart_td"><input type="text" class="form-control" style="width:15;" id="new_restart"></td>    <td id="new_room_td"><input type="text" class="form-control" style="width:15;" id="new_room"></td>    <td id="new_mac_td"><input type="text" class="form-control" style="width:15;" id="new_mac"></td>    <td><input type="button" class="add btn btn-success btn-round btn-sm my-0 btn-fill" onclick="add_row();" value="Add new device"></td></tr>');
        // $(btn).appendTo('#plugs_data_table > tbody');
  // $("#plugs_data_table #new_id_td").find("input[type='text']").val("");
	// $("#plugs_data_table #new_name_td").find("input[type='text']").val("");
	// $("#plugs_data_table #new_presence_td").find("input[type='text']").val("");
	// $("#plugs_data_table #new_control_td").find("input[type='text']").val("");
	// $("#plugs_data_table #new_restart_td").find("input[type='text']").val("");
	// $("#plugs_data_table #new_room_td").find("input[type='text']").val("");
  // $("#plugs_data_table #new_mac_td").find("input[type='text']").val("");
  // // document.getElementById("new_id").value="";
	// document.getElementById("new_name").value="";
	// document.getElementById("new_presence").value="";
	// document.getElementById("new_control").value="";
	// document.getElementById("new_restart").value="";
	// document.getElementById("new_room").value="";
	// document.getElementById("new_mac").value="";
}
