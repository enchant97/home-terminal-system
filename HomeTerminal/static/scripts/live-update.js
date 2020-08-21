"use strict";

const TYPES = {
    "TRANSPORT": {
        "JSON": 1,
        "MSGPACK": 2
    },
    "MESSAGE": {
        "NOTIFICATION": 1,
        "DB_UPDATE": 2
    },
    "NOTIFICATION": {
        "MESSAGE": 1
    },
    "DB_UPDATE": {
        "ADD": 1,
        "MODIFY": 2,
        "DELETE": 3
    }
};

/**
 * handles a live-update WebSocket connection
 * @param {Array} notify_apps - array of app names to listen to
 * @param {Number} transport_type - the type of transport method to use
 */
class LiveUpdateWS {
    constructor(notify_apps = [], transport_type = TYPES.TRANSPORT.JSON) {
        this._notify_apps = notify_apps;
        this._transport_type = transport_type;
        if ("WebSocket" in window) {
            this._websocket = new WebSocket(this.get_ws_url());
            this._websocket.onopen = () => {
                this._websocket.send(this.get_open_msg());
            }
            this._websocket.onmessage = (event) => { this.process_event(event) };
        }
        else {
            console.error("WebSocket is not supported by your browser so live update will not work");
        }
    }
    /**
     * returns the opening message when connecting to the WebSocket
     */
    get_open_msg() {
        return JSON.stringify({ "transport_type": this._transport_type, "notify_apps": this._notify_apps });
    }
    /**
     * returns the correct url to connect to the WebSocket
     */
    get_ws_url() {
        const url = window.location.host + "/live-update/listen";
        if (window.location.protocol == "https:") {
            return "wss://" + url;
        }
        return "ws://" + url;
    }
    /**
     * creates a Custom event and dispatches them
     * @param {Object} payload - the payload to send
     */
    create_event(type, payload){
        const event = new CustomEvent(type, { detail: payload });
        return window.dispatchEvent(event);
    }
    /**
     * converts the onmessage data into javascript friendly format
     */
    parse_msg(msg) {
        if (this._transport_type == TYPES.TRANSPORT.JSON) {
            return JSON.parse(msg);
        }
        else {
            //TODO: add MsgPack support for smaller data transfers
            throw "Unsupported transport_type";
        }
    }
    /**
     * process the message sent through WebSocket
     */
    process_event(event) {
        const data = this.parse_msg(event.data);
        if (data.m_type == TYPES.MESSAGE.DB_UPDATE) {
            this.process_db_update(data.payload);
        }
        else if (data.m_type == TYPES.MESSAGE.NOTIFICATION) {
            this.process_notification(data.payload);
        }
        else {
            console.error("Unknown message type");
        }
    }
    /**
     * dispaches a CustomEvent 'ws_update'
     * @param {Object} payload - the payload to send as detail
     */
    process_db_update(payload) {
        var type = `ws_update_${payload.where}`;
        this.create_event(type, payload);
    }
    /**
     * dispaches a CustomEvent 'ws_notif'
     * @param {Object} payload - the payload to send as detail
     */
    process_notification(payload) {
        if (payload.type_id == TYPES.NOTIFICATION.MESSAGE){
            this.create_event("ws_notif_mess", payload);
        }
    }
    /**
     * dispaches a CustomEvent 'ws_progress'
     * @param {Object} payload - the payload to send as detail
     */
    process_progress(_payload){
        //TODO: implement progress processing in V4
        throw "Progress update not implemented!";
    }
}
