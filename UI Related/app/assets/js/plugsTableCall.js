var postHttpClient = function() { 
  this.post = function(url, data,callback) {
    var httpRequest = new XMLHttpRequest();
    httpRequest.open("POST", url, false);
    httpRequest.onreadystatechange = function() {
      if (httpRequest.readyState == 4 && httpRequest.status == 200){
        callback(httpRequest.responseText);
      }
      else{
        document.getElementById("updateError").style.color = "red";
        document.getElementById("updateError").style.display= "inline";
      }
    };     
    httpRequest.send(JSON.stringify(data));
  };
};

function edit_row(no)
{
  document.getElementById("empty").style.display= "none";
  console.log(no)
  var table1 = $('#plugs_data_table').DataTable();
  var rows = table1.row(no).data();
  $(':input:visible').attr('disabled', true);
  console.log(table1.row(no).data()[7]);
  var lst = document.getElementById("branddropdown");
  console.log(lst)
  document.getElementById("plugdevID").value = rows[0];
  document.getElementById("plugdevName").value = rows[1];
  document.getElementById("plugpresence").value = rows[2];
  document.getElementById("plugcontrol").value = rows[3];
  document.getElementById("plugrestart").value = rows[4];
  document.getElementById("plugroom").value = rows[5];
  document.getElementById("plugmac").value = rows[6];
  if (rows[7]=="Plugwise"){
  lst.options[1].selected = true;}
  else{
    lst.options[0].selected = true;}
  document.getElementById("plugEditForm").style.display = "block";

  

}

function update_row(editeddata)
{  
  updatePostCall = {
    "call":"updateDevices",
    "houseID":localStorage.getItem("HouseID"),
    "deviceID":localStorage.getItem("deviceID"),
    "catalogURL":localStorage.getItem("catalogURL"),
    "data":{"sensor":"Plugs","sensorID":editeddata[0],"properties":{"Name":editeddata[1],"Presence":editeddata[2],"Control":editeddata[3],"Restart":editeddata[4],"Room":editeddata[5],"Mac":editeddata[6],"brand":editeddata[7]}}
    
  }
  var req = new postHttpClient();
  req.responseType = 'json';
  rURL = localStorage.getItem("DC");
  req.post(rURL,updatePostCall, function(response) {    
    jsonResponse = JSON.parse(response);
    console.log(jsonResponse.Output)
      if (jsonResponse.Result === "success"){
        document.getElementById("updateError").style.display= "none";
        document.getElementById("plugEditForm").style.display = "none";        
        location.reload();
      }
      else{        
        $(':input:visible').attr('disabled', false);
        document.getElementById('updateError').innerHTML = jsonResponse.Output
        document.getElementById("updateError").style.display= "inline";
        document.getElementById("updateError").style.color = "red";
        document.getElementById("plugEditForm").style.display = "none";  
      }
    
    });
  console.log(editeddata);
}

window.addEventListener('load', function() {
  
  var plugsbtn = document.getElementById("plugUpdatebutton");
  plugsbtn.onclick = function(){
    document.getElementById("empty").style.display= "none";
    var editData = []
    var list1 = document.getElementById("branddropdown");
    editData.push(document.getElementById("plugdevID").value)
    editData.push(document.getElementById("plugdevName").value);
    editData.push(parseInt(document.getElementById("plugpresence").value));
    editData.push(parseInt(document.getElementById("plugcontrol").value));
    editData.push(parseInt(document.getElementById("plugrestart").value));
    editData.push(parseInt(document.getElementById("plugroom").value));
    editData.push(document.getElementById("plugmac").value);
    editData.push(list1.options[list1.selectedIndex].value);
    if (editData.includes("")||editData.includes(undefined)){
      document.getElementById("empty").innerHTML="* Enter all values"
      document.getElementById("empty").style.display= "inline";
      document.getElementById("empty").style.color = "red";
      return false;
    }
    else if ((editData[7]==="DL")&& (editData[6].split(":").length === 1)){
      document.getElementById("empty").innerHTML="Dlink plug Address should be in IP:Password format"
      document.getElementById("empty").style.display= "inline";
      document.getElementById("empty").style.color = "red";
      return false;
    }
    else if ((editData[7]==="PW")&& (editData[6].split(":").length === 2)){
      document.getElementById("empty").innerHTML="Plugwise plugs Address should be a MAC"
      document.getElementById("empty").style.display= "inline";
      document.getElementById("empty").style.color = "red";
      return false;
    }
    // for(var i=0;i<editData.length;i++){
    //   if(editData[i] === "")   {
    //      document.getElementById("empty").style.display= "inline";
    //      return false;}
    // }
    
   update_row(editData);
   
  }
});

function delete_row(no)
{
  
  if (confirm("Do you want to delete?")) {
    txt = "Delete it!";
    var table1 = $('#plugs_data_table').DataTable();
    deleteDevice = {
      "call":"removeDevice",
      "houseID":localStorage.getItem("HouseID"),
      "deviceID":localStorage.getItem("deviceID"),
      "catalogURL":localStorage.getItem("catalogURL"),
      "statusURL":localStorage.getItem("statusAPI"),
      "data":{"sensor":"Plugs","sensorID":table1.row(no).data()[0]}      
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
          $(':input:visible').attr('disabled', false);    
          document.getElementById('updateError').innerHTML = jsonResponse.Output
          document.getElementById("updateError").style.display= "inline";
          document.getElementById("updateError").style.color = "red";          
        }
      
      });
   
  } else {
    txt = "None";
  }
	
}

function add_row()
{
  // var tr = $('#addDevice').find('.new_name_td').text();
  // $("#plugs_data_table #addDevice").each(function() {
  //   var value = $(this).text();
  //   console.log(value);
  // })
  // var r = $("#plugs_data_table #new_name").text();
  var new_id=  $("#plugs_data_table #new_id_td").find("input[type='text']").val();
	var new_name= $("#plugs_data_table #new_name_td").find("input[type='text']").val();
	var new_presence=$("#plugs_data_table #new_presence_td").find("input[type='number']").val();
	var new_control=$("#plugs_data_table #new_control_td").find("input[type='number']").val();
	var new_restart=$("#plugs_data_table #new_restart_td").find("input[type='number']").val();
	var new_room=$("#plugs_data_table #new_room_td").find("input[type='number']").val();
  var new_mac=$("#plugs_data_table #new_mac_td").find("input[type='text']").val();
  var new_brand=$('#addbranddropdown').val();
  
  var addDevice = {
    "call":"addDevice",
    "houseID":localStorage.getItem("HouseID"),
    "deviceID":localStorage.getItem("deviceID"),
    "catalogURL":localStorage.getItem("catalogURL"),
    "statusURL":localStorage.getItem("statusAPI"),
    "data":{"sensor":"Plugs","properties":{"Control": parseInt(new_control),
              "Name":new_name,
              "Presence": parseInt(new_presence),
              "Mac": new_mac,
              "brand":new_brand,
              "active": 1,
              "ID": new_id,
              "Restart":parseInt(new_restart),
              "Room": parseInt(new_room)}}
    
    }
  newdata = [new_id,new_name,new_presence,new_control,new_restart,new_room,new_mac];
  if (newdata.includes("")||newdata.includes(undefined)){
    document.getElementById('updateError').innerHTML = "Fill all the columns to add a device"
    document.getElementById("updateError").style.display= "inline";
    document.getElementById("updateError").style.color = "red"; 
  }
  else if ((new_brand==="DL")&& (new_mac.split(":").length === 1)){
    document.getElementById("updateError").innerHTML="Dlink plug Address should be in IP:Password format"
    document.getElementById("updateError").style.display= "inline";
    document.getElementById("updateError").style.color = "red";
    return false;
  }
  else if ((new_brand==="PW")&& (new_mac.split(":").length === 2)){
    document.getElementById("updateError").innerHTML="Plugwise plugs Address should be a MAC"
    document.getElementById("updateError").style.display= "inline";
    document.getElementById("updateError").style.color = "red";
    return false;
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
          $(':input:visible').attr('disabled', false);       
          document.getElementById('updateError').innerHTML = jsonResponse.Output
          document.getElementById("updateError").style.display= "inline";
          document.getElementById("updateError").style.color = "red";          
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
