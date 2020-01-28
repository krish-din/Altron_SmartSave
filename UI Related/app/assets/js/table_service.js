function edit_row_service(no)
{
  document.getElementById("edit_button_service"+no).style.display="none";
  document.getElementById("save_button_service"+no).style.display="block";
  
  var name=document.getElementById("name_row_service"+no);
  var presence=document.getElementById("presence_row_service"+no);
  var control=document.getElementById("control_row_service"+no);
  var restart=document.getElementById("restart_row_service"+no);
  var room=document.getElementById("room_row_service"+no);
  var mac=document.getElementById("mac_row_service"+no);

  var name_data_service=name.innerHTML;
  var presence_data_service=presence.innerHTML;
  var control_data_service=control.innerHTML;
  var restart_data_service=restart.innerHTML;
  var room_data_service=room.innerHTML;
  var mac_data_service=mac.innerHTML;

  name.innerHTML="<input type='text' class='form-control' id='name_text_service"+no+"' value='"+name_data_service+"'>";
  presence.innerHTML="<input type='text' class='form-control' id='presence_text_service"+no+"' value='"+presence_data_service+"'>";
  control.innerHTML="<input type='text' class='form-control' id='control_text_service"+no+"' value='"+control_data_service+"'>";
  restart.innerHTML="<input type='text' class='form-control' id='restart_text_service"+no+"' value='"+restart_data_service+"'>";
  room.innerHTML="<input type='text' class='form-control' id='room_text_service"+no+"' value='"+room_data_service+"'>";
  mac.innerHTML="<input type='text' class='form-control' id='mac_text_service"+no+"' value='"+mac_data_service+"'>";

}

function save_row_service(no)
{

	var name_val=document.getElementById("name_text_service"+no).value;
	var presence_val=document.getElementById("presence_text_service"+no).value;
	var control_val=document.getElementById("control_text_service"+no).value;
  var restart_val=document.getElementById("restart_text_service"+no).value;
  var room_val=document.getElementById("room_text_service"+no).value;
  var mac_val=document.getElementById("mac_text_service"+no).value;

  document.getElementById("name_row_service"+no).innerHTML=name_val;
  document.getElementById("presence_row_service"+no).innerHTML=presence_val;
  document.getElementById("control_row_service"+no).innerHTML=control_val;
  document.getElementById("restart_row_service"+no).innerHTML=restart_val;
  document.getElementById("room_row_service"+no).innerHTML=room_val;
  document.getElementById("mac_row_service"+no).innerHTML=mac_val;

  document.getElementById("edit_button_service"+no).style.display="block";
  document.getElementById("save_button_service"+no).style.display="none";
}

function delete_row_service(no)
{
  var txt;
  if (confirm("Do you want to delete?")) {
    txt = "Delete it!";
  } else {
    txt = "None";
  }
  document.getElementById("row_service"+no+"").outerHTML="";
}

function add_row_service()
{

	var new_name=document.getElementById("new_name_service").value;
	var new_presence=document.getElementById("new_presence_service").value;
	var new_control=document.getElementById("new_control_service").value;
	var new_restart=document.getElementById("new_restart_service").value;
	var new_room=document.getElementById("new_room_service").value;
	var new_mac=document.getElementById("new_mac_service").value;
	
	var table=document.getElementById("service_table");
	var table_len=(table.rows.length)-1;
	var row_service = table.insertRow(table_len).outerHTML="<tr id='row_service"+table_len+"'><td id='name_row_service"+table_len+"'>"+new_name+"</td><td id='presence_row_service"+table_len+"'>"+new_presence+"</td><td id='control_row_service"+table_len+"'>"+new_control+"</td><td id='restart_row_service"+table_len+"'>"+new_restart+"</td><td id='room_row_service"+table_len+"'>"+new_room+"</td><td id='mac_row_service"+table_len+"'>"+new_mac+"</td><td><input type='button' id='edit_button_service"+table_len+"' value='Edit' class='edit btn btn-info btn-round btn-sm my-0 btn-fill' style='width: 18%;' onclick='edit_row_service("+table_len+")'> <input type='button' class='save btn btn-primary btn-round btn-sm my-0 btn-fill' style='width: 18%;' id='save_button_service"+table_len+"' value='Save' onclick='save_row_service("+table_len+")'> <input type='button' value='Delete' class='delete btn btn-danger btn-round btn-sm my-0 btn-fill' style='width: 18%;' onclick='delete_row_service("+table_len+")'></td></tr>";

	document.getElementById("new_name_service").value="";
	document.getElementById("new_presence_service").value="";
	document.getElementById("new_control_service").value="";
	document.getElementById("new_restart_service").value="";
	document.getElementById("new_room_service").value="";
	document.getElementById("new_mac_service").value="";
}

function add_user(){
  //telegram
}
