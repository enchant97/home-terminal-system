"use strict";

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

function new_messages(messages) {
    // adds new messages to the messages box on dashboard
    const mesage_table = document.getElementById("loadedmessages");
    mesage_table.innerHTML = "";//TODO: remove when the lastupdated date is implemented
    for (const message of messages.loaded_data) {
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

/**
 * sends a delete request to the api server and
 * then deletes the table row in the HTML table element,
 * uses a DELETE method
 * @param {string} api_url - the api url to send the request to
 * @param {string} tr_id - the id of the table row
 */
function delete_tr_api(api_url, tr_id) {
    const tr_elem = document.getElementById(tr_id);
    tr_elem
    fetch(api_url, {
        method: "DELETE"
    })
        .then(() => {
            tr_elem.remove();
        })
        .catch((error) => {
            console.error("Error", error);
        });
}

function delete_message(mess_id) {
    //TODO: use delete_tr_api instead
    //sends a xhr DELETE request to remove a message
    //source: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
    fetch("/messages/remove/" + mess_id, {
        method: "DELETE"
    })
        .then(() => {
            document.getElementById("message_" + mess_id).remove();
        })
        .catch((error) => {
            console.error("Error", error);
        });
}

function do_messages_refresh() {
    fetch("/messages/asjson")
        .then((response) => {
            return response.json();
        })
        .then((conv_json) => {
            new_messages(conv_json);
        })
        .catch((error) => {
            console.error("Error", error);
        });
}

function api_move_widget_pos(widget_id, id_to_replace) {
    //TODO this is not part of the api move it!
    const body = JSON.stringify({ "id": parseInt(widget_id), "id-to-replace": parseInt(id_to_replace) });
    fetch("/home/dashboard/widgets/move",
        {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: body
        })
        .catch(console.error);
}
