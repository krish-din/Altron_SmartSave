var postHttpClient = function() { 
  this.post = function(url, data,callback) {
    var httpRequest = new XMLHttpRequest();
    httpRequest.open("POST", url, false);
    httpRequest.onreadystatechange = function() {
      if (httpRequest.readyState == 4 && httpRequest.status == 200){
        callback(httpRequest.responseText);
      }
      else{
        document.getElementById("tempupdateError").style.color = "red";
        document.getElementById("tempupdateError").style.display= "inline";
      }
    };     
    httpRequest.send(JSON.stringify(data));
  };
};

function tempedit_row(no)
{
  document.getElementById("tempempty").style.display= "none";
  console.log(no)
  var table1 = $('#temp_data_table').DataTable();
  var rows = table1.row(no).data();
  $(':input:visible').attr('disabled', true);
  console.log(table1.row(no).data()[0]);
  document.getElementById("tempdevID").value = rows[0];
  document.getElementById("tempdevName").value = rows[1];
  document.getElementById("temproom").value = rows[2];
  document.getElementById("tempGPIO").value = rows[3];
  
  document.getElementById("tempEditForm").style.display = "block";

  

}

function tempupdate_row(editeddata)
{  
  updatePostCall = {
    "call":"updateDevices",
    "houseID":localStorage.getItem("HouseID"),
    "deviceID":localStorage.getItem("deviceID"),
    "catalogURL":localStorage.getItem("catalogURL"),
    "data":{"sensor":"T-Sensors","sensorID":editeddata[0],"properties":{"Name":editeddata[1],"Room":parseInt(editeddata[2])}}
    
  }
  var req = new postHttpClient();
  req.responseType = 'json';
  rURL = localStorage.getItem("DC");
  req.post(rURL,updatePostCall, function(response) {    
    jsonResponse = JSON.parse(response);
    console.log(jsonResponse.Output)
      if (jsonResponse.Result === "success"){
        document.getElementById("tempupdateError").style.display= "none";
        document.getElementById("tempEditForm").style.display = "none";        
        location.reload();
      }
      else{        
        document.getElementById('tempupdateError').innerHTML = jsonResponse.Output
        document.getElementById("tempupdateError").style.display= "inline";
        document.getElementById("tempupdateError").style.color = "red";
        document.getElementById("tempEditForm").style.display = "none";  
      }
    
    });
  console.log(editeddata);
}

window.addEventListener('load', function() {
  
  var btn = document.getElementById("tempUpdatebutton");
  btn.onclick = function(){
    document.getElementById("tempempty").style.display= "none";
    var editData = []
    editData.push(document.getElementById("tempdevID").value)
    editData.push(document.getElementById("tempdevName").value);
    editData.push(parseInt(document.getElementById("temproom").value));
    editData.push(parseInt(document.getElementById("tempGPIO").value));
    if (editData.includes("")||editData.includes(undefined)){
      document.getElementById("tempempty").style.display= "inline";
      document.getElementById("tempempty").style.color = "red";
      return false;
    }
    // for(var i=0;i<editData.length;i++){
    //   if(editData[i] === "")   {
    //      document.getElementById("empty").style.display= "inline";
    //      return false;}
    // }
    
    tempupdate_row(editData);
   
  }
});

function tempdelete_row(no)
{
  
  if (confirm("Do you want to delete?")) {
    txt = "Delete it!";
    var table1 = $('#temp_data_table').DataTable();
    deleteDevice = {
      "call":"removeDevice",
      "houseID":localStorage.getItem("HouseID"),
      "deviceID":localStorage.getItem("deviceID"),
      "catalogURL":localStorage.getItem("catalogURL"),
      "statusURL":localStorage.getItem("statusAPI"),
      "data":{"sensor":"T-Sensors","sensorID":table1.row(no).data()[0]}      
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
          document.getElementById('tempupdateError').innerHTML = jsonResponse.Output
          document.getElementById("tempupdateError").style.display= "inline";
          document.getElementById("tempupdateError").style.color = "red";          
        }
      
      });
   
  } else {
    txt = "None";
  }
	
}

function tempadd_row()
{
  // var tr = $('#addDevice').find('.new_name_td').text();
  // $("#plugs_data_table #addDevice").each(function() {
  //   var value = $(this).text();
  //   console.log(value);
  // })
  // var r = $("#plugs_data_table #new_name").text();
  var new_id=  $("#temp_data_table #new_tempid_td").find("input[type='text']").val();
  var new_name= $("#temp_data_table #new_tempname_td").find("input[type='text']").val();
  var new_room=$("#temp_data_table #new_temproom_td").find("input[type='number']").val();
  var new_gpio=$("#temp_data_table #new_tempGPIO_td").find("input[type='number']").val();
  
  var addDevice = {
    "call":"addDevice",
    "houseID":localStorage.getItem("HouseID"),
    "deviceID":localStorage.getItem("deviceID"),
    "catalogURL":localStorage.getItem("catalogURL"),
    "statusURL":localStorage.getItem("statusAPI"),
    "data":{"sensor":"T-Sensors","properties":{
              "Name":new_name,          
              "active": 1,
              "ID": new_id,
              "Room": parseInt(new_room),
              "GPIO": parseInt(new_gpio)}}
    
    }
  newdata = [new_id,new_name,new_presence,new_control,new_restart,new_room,new_mac];
  if (newdata.includes("")||newdata.includes(undefined)){
    document.getElementById('tempupdateError').innerHTML = "Fill all the columns to add a device"
    document.getElementById("tempupdateError").style.display= "inline";
    document.getElementById("tempupdateError").style.color = "red"; 
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
          document.getElementById('tempupdateError').innerHTML = jsonResponse.Output
          document.getElementById("tempupdateError").style.display= "inline";
          document.getElementById("tempupdateError").style.color = "red";          
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
