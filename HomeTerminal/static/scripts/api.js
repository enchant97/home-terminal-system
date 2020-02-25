function pad_zero(str_to_pad) {
    // pads a string/int e.g. 1 becomes 01
    str_to_pad = str_to_pad.toString()
    if (str_to_pad.length == 1) {
        return "0" + str_to_pad;
    }
    else {
        return str_to_pad
    }
}
function datetime_for_api() {
    // returns the utc time in string format of: YYYY/MM/DD H:M:S.MS
    const curr_dt = new Date();
    return `${curr_dt.getUTCFullYear()}/${pad_zero(curr_dt.getUTCMonth())}/${pad_zero(curr_dt.getUTCDay())} ${pad_zero(curr_dt.getUTCHours())}:${pad_zero(curr_dt.getUTCMinutes())}:${pad_zero(curr_dt.getUTCSeconds())}.${curr_dt.getUTCMilliseconds()}`;
}

function httpGetAsyncJSON(theUrl, callback, ...callback_args) {
    // will pass callback json
    // source: https://stackoverflow.com/questions/247483/http-get-request-in-javascript
    const xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            const raw = xmlHttp.responseText;
            callback(JSON.parse(raw), ...callback_args);
        }
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous
    xmlHttp.send(null);
}

function httpPOSTAsyncJSON(){
    //TODO: implement
}

function refresh_notifications_count(){
    // loads a new count of notifications
    // into notification icon
    //TODO: implement later after 2.0
}

function new_messages(messages){
    // adds new messages to the messages box on dashboard
    const mesage_table = document.getElementById("loadedmessages");
    mesage_table.innerHTML = "";//TODO: remove when the lastupdated date is implemented
    for (const message of messages.loaded_data){
        const row = document.createElement("tr");
        const col1 = document.createElement("td");
        const col2 = document.createElement("td");
        const closebnt = document.createElement("button");

        row.setAttribute("id", "message_" + message.id);
        col1.innerText = message.message;
        closebnt.setAttribute("onclick", `delete_message(${message.id})`)
        closebnt.innerText = "Close";

        col2.append(closebnt);
        row.append(col1);
        row.append(col2);

        mesage_table.append(row);
    }
}

function delete_message(mess_id){
    //TODO: implement with xhr
}

function do_messages_refresh(){
    httpGetAsyncJSON("/api/messages", new_messages);
}
