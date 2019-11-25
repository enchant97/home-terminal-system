// https://tutorials.technology/tutorials/61-Create-an-application-with-websockets-and-flask.html
// https://stackoverflow.com/questions/6599470/node-js-socket-io-with-ssl
var mesage_table = document.getElementById("loadedmessages");
var socket = io.connect('//' + document.domain + ':' + location.port);

function delete_message(message_id) {
    document.getElementById("message_" + message_id).remove();
    socket.emit("removemessage", { "id": message_id })
}
socket.on('new_message', function (data) {
    var row = document.createElement("tr");
    var col1 = document.createElement("td");
    var col2 = document.createElement("td");
    var closebnt = document.createElement("button");

    row.setAttribute("id", "message_" + data.id);
    col1.innerText = data.content;
    closebnt.setAttribute("onclick", `delete_message(${data.id})`)
    closebnt.innerText = "Close";

    col2.append(closebnt);
    row.append(col1);
    row.append(col2);

    mesage_table.append(row);
});

socket.on("timeralert", function (data) {
    document.getElementById('timeralarm').play();
    createAlert("Timer Finished!", "message");
});

socket.on("new_notification", function(data){
    createAlert(data.content, data.category);
});

/*
if (window.location.protocol == "https"){
    var ws_scheme = "wss://"
}
else{
    var ws_scheme = "ws://"
}
var websocket = new WebSocket(ws_scheme + document.domain + ':' + location.port);

websocket.addEventListener('new_message', function (data) {
    var row = document.createElement("tr");
    var col1 = document.createElement("td");
    var col2 = document.createElement("td");
    var closebnt = document.createElement("button");

    row.setAttribute("id", "message_" + data.id);
    col1.innerText = data.content;
    closebnt.setAttribute("onclick", `delete_message(${data.id})`)
    closebnt.innerText = "Close";

    col2.append(closebnt);
    row.append(col1);
    row.append(col2);

    mesage_table.append(row);
});
*/
