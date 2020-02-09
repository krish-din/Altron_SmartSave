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


var rURL = localStorage.getItem("DC")  + localStorage.getItem("HouseID")+'/' + localStorage.getItem("deviceID") +"/all";

var req = new getHttpClient();
req.responseType = 'json';
var plugID = "plugcards"
var brandName={"PW":"Plugwise","DL":"DLink"}
req.post(rURL, function(response) {
    console.log(response)
    
    jsonResponse = JSON.parse(response);
    var plugs = jsonResponse.Output["Plugs"]["installedPlugs"]

    console.log(plugs)
    var motion = jsonResponse.Output["M-Sensors"]["installedM-Sensors"]
    var temp = jsonResponse.Output["T-Sensors"]["installedT-Sensors"]
    var data = []
    plugs.forEach(function (value, i) {
      data.push([]);
      data[i].push(value.ID);
      data[i].push(value.Name);
      data[i].push(value.Presence);
      data[i].push(value.Control);
      data[i].push(value.Restart);
      data[i].push(value.Room);
      data[i].push(value.Mac);
      data[i].push(brandName[value.brand]);
    });
    console.log(data)
    tempData=[]
    temp.forEach(function (value, i) {
      tempData.push([]);
      var idx = parseInt(+tempData.length -1)  
      tempData[idx].push(value.ID);
      tempData[idx].push(value.Name);
      tempData[idx].push(value.Room);   
      tempData[idx].push(value.GPIO);
    });

    PIRData=[]
    motion.forEach(function (value, i) {
      PIRData.push([]);
      var idx = parseInt(+PIRData.length -1)  
      PIRData[idx].push(value.ID);
      PIRData[idx].push(value.Name);
      PIRData[idx].push(value.Room);  
      PIRData[idx].push(value.GPIO);   
    });

    //populating plugs datatable
    $('#plugs_data_table').DataTable({
      paging: false,
      searching: false,
      data:data,
      "bAutoWidth": false,
      "bSort": false,
      "bInfo" : false,
        "columns":[
            // {data: null,
            //   defaultContent: '',
            //   className: 'select-checkbox',
            //   orderable: false},
            {data:0},
            {data:1},
            {data:2},
            {data:3},
            {data:4},
            {data:5},
            {data:6},
            {data:7}
        ]
    });
    var table = document.getElementById("plugs_data_table");
    var tbodyRowCount = table.tBodies[0].rows.length;
    // console.log(tbodyRowCount)
    for (i = 0; i < tbodyRowCount; i++) { 
      var btns= $('<td align="left"><table><tr class="spaceUnder"><td><input id="edit_button'+i+'" value="Edit" class="edit btn btn-info btn-round btn-sm my-0 btn-fill" onclick="edit_row('+i+')" style="width: 75%;"/></td></tr><tr><td > <input type="" value="Delete" class="delete btn btn-danger btn-round btn-sm my-0 btn-fill" onclick="delete_row('+i+')" style="width: 75%;"/></td></tr></table> </td>');
      // var btns= $('<td><input type="checkbox" id="checkbox'+i+'"> </td>');
      $(btns).appendTo('#plugs_data_table > tbody > tr:eq('+i+')');
    }
    var table = $('#plugs_data_table').DataTable();
    var lastIdx = table.column( 0 ).data().length - 1
    var newPlugNum = +parseInt(table.row(lastIdx).data()[0].split("_")[1])+ +1
    var newPlugID = table.row(lastIdx).data()[0].split("_")[0]+ "_"+ newPlugNum
    
    var btn = $('<tr id="addDevice" ><td id="new_id_td"><input type="text" disabled class="form-control" style="width:80px;" name="new_plugID" id="new_id" value="'+newPlugID+'"></td>    <td id="new_name_td"><input type="text" class="form-control" style="width:15;" id="new_name" required ></td>    <td id="new_presence_td"><input type="number" min="0" max="1" class="form-control" style="width:15;" id="new_presence" required ></td>    <td id="new_control_td"><input type="number" min="0" max="1" class="form-control" style="width:15;" id="new_control" required ></td>    <td id="new_restart_td"><input type="number" min="0" max="1" class="form-control" style="width:15;" id="new_restart" required ></td>    <td id="new_room_td"><input type="number" min="0" class="form-control" style="width:15;" id="new_room" required ></td>    <td id="new_mac_td"><input type="text" class="form-control" style="width:15;" id="new_mac" required ></td> <td id="new_brand_td"><fieldset class="dropdown"><select class="custom-select custom-select-sm" id="addbranddropdown"><option value = "DL">DLink</option><option value = "PW">Plugwise</option></select></fieldset></td>    <td><input type="button" id="addnewplugbutton" class="add btn btn-success btn-round btn-sm my-0 btn-fill" onclick="add_row();" value="Add new device" ></td></tr>');
    $(btn).appendTo('#plugs_data_table > tbody');

    //populating temperature Table
    $('#temp_data_table').DataTable({
      paging: false,
      searching: false,
      data:tempData,
      "bAutoWidth": false,
      "bSort": false,
      "bInfo" : false,
        "columns":[
            // {data: null,
            //   defaultContent: '',
            //   className: 'select-checkbox',
            //   orderable: false},
            {data:0},
            {data:1},
            {data:2},
            {data:3}
        ]
    });
    var table = document.getElementById("temp_data_table");
    var tbodyRowCount = table.tBodies[0].rows.length;
    
    for (i = 0; i < tbodyRowCount; i++) { 
      var btns= $('<td align="left"><table><tr class="spaceUnder"><td><input id="temp_edit_button'+i+'" value="Edit" class="edit btn btn-info btn-round btn-sm my-0 btn-fill" onclick="tempedit_row('+i+')" style="width: 35%;"/></td></tr><tr><td > <input type="" value="Delete" class="delete btn btn-danger btn-round btn-sm my-0 btn-fill" onclick="tempdelete_row('+i+')" style="width: 35%;"/></td></tr></table> </td>');
      // var btns= $('<td><input type="checkbox" id="checkbox'+i+'"> </td>');
      $(btns).appendTo('#temp_data_table > tbody > tr:eq('+i+')');
    }
    var table = $('#temp_data_table').DataTable();
    var lastIdx = table.column( 0 ).data().length - 1
    var newTempNum = +parseInt(table.row(lastIdx).data()[0].split("_")[1])+ +1
    var newTempID = table.row(lastIdx).data()[0].split("_")[0]+ "_"+ newTempNum
    
    var btn = $('<tr id="temp_addDevice" ><td id="new_tempid_td"><input type="text" disabled class="form-control" style="width:80px;" id="new_tempid" name="new_tempID" value="'+newTempID+'"></td>    <td id="new_tempname_td"><input type="text" class="form-control" style="width:15;" id="new_tempname" required ></td><td id="new_temproom_td"><input type="number" min="0" class="form-control" style="width:15;" id="new_temproom" required ></td><td id="new_tempGPIO_td"><input type="number" min="0" class="form-control" style="width:15;" id="new_tempGPIO" required ></td><td><input type="button" id="addnewtempbutton" class="add btn btn-success btn-round btn-sm my-0 btn-fill" onclick="tempadd_row();" value="Add new device" ></td></tr>');
    $(btn).appendTo('#temp_data_table > tbody');

    //populating PIR sensor Data
    $('#pir_data_table').DataTable({
      paging: false,
      searching: false,
      data:PIRData,
      "bAutoWidth": false,
      "bSort": false,
      "bInfo" : false,
        "columns":[
            // {data: null,
            //   defaultContent: '',
            //   className: 'select-checkbox',
            //   orderable: false},
            {data:0},
            {data:1},
            {data:2},
            {data:3}
        ]
    });
    var table = document.getElementById("pir_data_table");
    var tbodyRowCount = table.tBodies[0].rows.length;
    
    for (i = 0; i < tbodyRowCount; i++) { 
      var btns= $('<td align="left"><table><tr class="spaceUnder"><td><input id="pir_edit_button'+i+'" value="Edit" class="edit btn btn-info btn-round btn-sm my-0 btn-fill" onclick="piredit_row('+i+')" style="width: 35%;"/></td></tr><tr><td > <input type="" value="Delete" class="delete btn btn-danger btn-round btn-sm my-0 btn-fill" onclick="pirdelete_row('+i+')" style="width: 35%;"/></td></tr></table> </td>');
      // var btns= $('<td><input type="checkbox" id="checkbox'+i+'"> </td>');
      $(btns).appendTo('#pir_data_table > tbody > tr:eq('+i+')');
    }
    var table = $('#pir_data_table').DataTable();
    var lastIdx = table.column( 0 ).data().length - 1
    var newpirNum = +parseInt(table.row(lastIdx).data()[0].split("_")[1])+ +1
    var newpirID = table.row(lastIdx).data()[0].split("_")[0]+ "_"+ newpirNum
    
    var btn = $('<tr id="pir_addDevice" ><td id="new_pirid_td"><input type="text" disabled class="form-control" style="width:80px;" id="new_pirid" name="new_pirID" value="'+newpirID+'"></td>    <td id="new_pirname_td"><input type="text" class="form-control" style="width:15;" id="new_pirname" required ></td><td id="new_pirroom_td"><input type="number" min="0" class="form-control" style="width:15;" id="new_pirroom" required ></td><td id="new_pirGPIO_td"><input type="number" min="0" class="form-control" style="width:15;" id="new_pirGPIO" required ></td><td><input type="button" id="addnewpirbutton" class="add btn btn-success btn-round btn-sm my-0 btn-fill" onclick="piradd_row();" value="Add new device" ></td></tr>');
    $(btn).appendTo('#pir_data_table > tbody');
    
    
    console.log($('*[id*=button]:visible'))
});
