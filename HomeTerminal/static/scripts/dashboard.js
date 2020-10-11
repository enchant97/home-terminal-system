"use strict";

// source: https://stackoverflow.com/a/10126042/8075455
const inactivityTime = () => {
    var time;
    window.addEventListener('load', resetTimer, true);
    add_active_events(resetTimer);

    function inactive() {
        location.replace("/idle-display");
    }

    function resetTimer() {
        clearTimeout(time);
        time = setTimeout(inactive, 45000);
    }
}

/**
 * shows the widget editmode controls
 */
function show_widgets_editmode() {
    const editmode_bnt = document.getElementById("widgeteditmode-bnt");
    editmode_bnt.onclick = hide_widgets_editmode;
    editmode_bnt.innerText = "Stop Editing Widgets";
    const widgets_elem = document.getElementById("widgets");
    widgets_elem.childNodes.forEach(widget => {
        const edit_bar = document.createElement("div");
        edit_bar.classList.add("settings-bar");
        const add_widget_bnt = document.createElement("button");
        add_widget_bnt.innerText = "✚";
        add_widget_bnt.addEventListener("click", _event => { add_widget_menu(widget) })
        const move_up_bnt = document.createElement("button");
        move_up_bnt.innerText = "⬆";
        move_up_bnt.addEventListener("click", _event => { move_widget_posistion(widget, "up") });
        //TODO: allow for adding below(after) other widgets not just above(before)
        // const move_down_bnt = document.createElement("button");
        // move_down_bnt.innerText = "⬇";
        // move_down_bnt.addEventListener("click", _event => { move_widget_posistion(widget, "down") });
        const settings_img = document.createElement("img");
        settings_img.setAttribute("src", "/static/settings-cog.svg");
        settings_img.setAttribute("width", "15px")
        const settings_bnt = document.createElement("button");
        settings_bnt.addEventListener("click", _event => { get_widget_edit_url(widget.id.split("-").pop()) })
        settings_bnt.appendChild(settings_img);
        const delete_widget_bnt = document.createElement("button");
        delete_widget_bnt.innerText = "✖";
        delete_widget_bnt.addEventListener("click", _event => { delete_widget(widget) })
        edit_bar.appendChild(add_widget_bnt);
        edit_bar.appendChild(move_up_bnt);
        // edit_bar.appendChild(move_down_bnt);
        edit_bar.appendChild(settings_bnt);
        edit_bar.appendChild(delete_widget_bnt);
        widget.insertBefore(edit_bar, widget.firstChild);
    });
}

/**
 * gets then redirects the widget
 * settings page, if it has one
 * @param {number} widget_id - the id of the widget
 */
function get_widget_edit_url(widget_id) {
    fetch("/home/dashboard/widgets/get-setting-url/" + widget_id,
        {
            method: "GET"
        })
        .then(response => response.json())
        .then(response_json => {
            if (response_json.settings_url === null) {
                alert("Widget has no settings, at least from here...");
            }
            else {
                window.location.href = response_json.settings_url;
            }
        })
        .catch(console.error);
}

/**
 * removes a widget
 * @param {Element} widget_elem - the widget to remove
 */
function delete_widget(widget_elem) {
    fetch("/home/dashboard/widgets/remove",
        {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: parseInt(widget_elem.id.split("-").pop()) })
        })
        .catch(console.error);
    widget_elem.remove();
}

/**
 * moves a widget
 * @param {Element} widget_elem - the widget to move
 * @param {String} direction - the direction of movement
 */
function move_widget_posistion(widget_elem, direction) {
    const widget_id = widget_elem.id.split("-").pop();
    var widget_pos = get_child_pos(widget_elem.parentElement.children, widget_elem);
    if (direction === "up") {
        if (widget_elem.previousSibling) {
            widget_pos -= 1;
            api_move_widget_pos(widget_id, widget_elem.previousSibling.id.split("-").pop());
            widget_elem.parentElement.insertBefore(widget_elem, widget_elem.previousSibling);
        }
    }
    //TODO: allow for adding below(after) other widgets not just above(before)
    // else if (direction === "down"){
    //     if (widget_elem.nextSibling){
    //         widget_pos += 1;
    //         widget_elem.parentElement.insertBefore(widget_elem, widget_elem.nextSibling.nextSibling);
    //     }
    // }
}

/**
 * show the add-widget popup so user can pick and add a widget
 * @param {Element} widget_elem_to_replace - the element to replace/move
 */
function add_widget_menu(widget_elem_to_replace) {
    const popup_elem = document.createElement("div");
    popup_elem.classList.add("popup");
    const title = document.createElement("h2");
    title.innerText = "Add Widget";
    const popup_inner = document.createElement("form");
    popup_inner.setAttribute("onsubmit", "return false;");
    popup_inner.classList.add("two-col");
    const select_lab = document.createElement("label");
    select_lab.innerText = "Widget Name";
    const select_elem = document.createElement("select");
    select_elem.setAttribute("disabled", true);
    const loading_elem = document.createElement("div");
    loading_elem.classList.add("spinload", "fillboth");
    const ok_elem = document.createElement("button");
    ok_elem.setAttribute("type", "submit");
    ok_elem.classList.add("fillboth", "ok");
    ok_elem.innerText = "Ok";
    ok_elem.setAttribute("disabled", true);
    ok_elem.addEventListener("click", _event => {
        // add a new widget
        select_elem.setAttribute("disabled", true);
        ok_elem.setAttribute("disabled", true);
        loading_elem.style.removeProperty("display");
        fetch(
            "/home/dashboard/widgets/add",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(
                    {
                        "id-to-replace": parseInt(widget_elem_to_replace.id.split("-").pop()),
                        "widget-uuid": select_elem.options[select_elem.selectedIndex].value
                    })
            })
            .then(response => response.text())
            .then(result => {
                // handle success
                const new_widget = document.createRange().createContextualFragment(result);
                const widgets_elem = document.getElementById("widgets");
                //TODO allow for adding below(after) other widgets not just above(before)
                widgets_elem.insertBefore(new_widget, widget_elem_to_replace);
                popup_elem.remove();
                hide_widgets_editmode();
            })
            .catch(error => {
                console.error(error);
                alert("Could not add new widget.\n\n" + error);
                popup_elem.remove();
            });
    });
    const cancel_elem = document.createElement("button");
    cancel_elem.classList.add("fillboth");
    cancel_elem.innerText = "Cancel";
    cancel_elem.addEventListener("click", _event => { popup_elem.remove() });
    // get all widget that are available to add for this user
    fetch("/home/dashboard/widgets/get-names", { method: "GET" })
        .then(response => response.json())
        .then(result => {
            for (let i = 0; i < result.length; i++) {
                // add each widget as a option for the select element
                let widget = result[i];
                let option = document.createElement("option");
                option.innerText = widget.name;
                option.value = widget.uuid;
                select_elem.append(option);
            }
            loading_elem.style.setProperty("display", "none");
            select_elem.removeAttribute("disabled");
            ok_elem.removeAttribute("disabled");
        })
        .catch(error => {
            console.error(error);
            alert("Could not get widgets.\n\n" + error);
            popup_elem.remove();
        });
    popup_elem.append(title);
    popup_inner.append(select_lab);
    popup_inner.append(select_elem);
    popup_inner.append(loading_elem);
    popup_inner.append(ok_elem);
    popup_inner.append(cancel_elem);
    popup_elem.append(popup_inner);
    document.body.append(popup_elem);
}

/**
 * hide the widgets editmode controls
 */
function hide_widgets_editmode() {
    const editmode_bnt = document.getElementById("widgeteditmode-bnt");
    editmode_bnt.onclick = show_widgets_editmode;
    editmode_bnt.innerText = "Start Editing Widgets";
    const widgets_elem = document.getElementById("widgets");
    widgets_elem.childNodes.forEach(widget => {
        // remove the edit-bar
        if (widget.childNodes.length > 1){
            // only remove if there is a edit-bar
            widget.childNodes[0].remove();
        }
    });
}

/**
 * load the widgets onto the page
 */
function load_widgets_element() {
    fetch("/home/dashboard/widgets/get-all", { method: "GET" })
        .then(response => response.text())
        .then(result => {
            const widgets = document.createRange().createContextualFragment(result);
            const widgets_elem = document.getElementById("widgets");
            widgets_elem.removeChild(widgets_elem.childNodes[0]);
            widgets_elem.appendChild(widgets);
        })
        .catch(console.error);
}

window.addEventListener("load", _event => {
    inactivityTime();
    load_widgets_element();
});
