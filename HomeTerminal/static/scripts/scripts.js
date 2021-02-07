"use strict";

const THEME_KEYNAME = "theme";
const THEMES = {
    OS_PREF: "os-pref",
    LIGHT: "light",
    DARK: "dark",
    SOLARIZED_DARK: "solarized-dark"
}
const active_events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];

function gen_datetime() {
    const date = new Date();
    var h = date.getHours();
    var m = date.getMinutes();
    var dd = date.getDate();
    var mm = date.getMonth() + 1;
    if (h < 10) { h = '0' + h }
    if (m < 10) { m = '0' + m }
    if (dd < 10) { dd = '0' + dd }
    if (mm < 10) { mm = '0' + mm }
    document.getElementById("timebox").innerHTML = `${h}:${m}`;
    document.getElementById("datebox").innerHTML = `${dd}-${mm}-${date.getFullYear()}`;
}

/**
 * used to create a notification element
 * @param {String} message - the message
 * @param {String} category - the category of the message e.g. message, warning
 */
function createAlert(message, category) {
    const box = document.createElement("div");
    box.innerText = message;
    box.classList.add("alert");
    box.classList.add(category);
    const bnt = document.createElement("span");
    bnt.classList.add("closebtn");
    bnt.onclick = () => { this.parentElement.style.display = 'none'; };
    bnt.innerText = "×";
    const mess = document.createElement("strong");
    mess.innerText = category;
    box.appendChild(bnt);
    box.appendChild(mess);
    const notif_elem = document.getElementById("notifications");
    notif_elem.appendChild(box);
}

function togg_element_onclick(checkbox_id, ...elements) {
    const checkbox = document.getElementById(checkbox_id);
    if (checkbox.checked == false) {
        for (let i = 0; i < elements.length; i++) {
            const selected_element = document.getElementById(elements[i]);
            selected_element.disabled = false;
        }
    }
    else {
        for (let i = 0; i < elements.length; i++) {
            const selected_element = document.getElementById(elements[i]);
            selected_element.disabled = true;
        }
    }
}

/**
 * checks whether the password has at least 8 characters,
 * one number, lowercase and upper case letter
 * @param {String} password - the password to check against
 */
function password_char_check(password) {
    // at least one number, one lowercase and one uppercase letter
    // at least 8 characters
    const re = /(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}/;
    return re.test(password);
}

/**
 * validates the password to check it
 * @param {String} pass_1_id - the password element id
 * @param {*String} pass_2_id - the password confirm element id
 * @param {String} username_id - the username element id
 */
function validate_password(pass_1_id, pass_2_id, username_id) {
    pass_1_id = document.getElementById(pass_1_id).value;
    pass_2_id = document.getElementById(pass_2_id).value;
    username_id = document.getElementById(username_id).value;
    if (pass_1_id != pass_2_id) {
        createAlert("Passwords do not match!", "warning");
        return false;
    }
    else if (pass_1_id == username_id) {
        createAlert("Password cannot be username", "warning");
        return false;
    }
    else if (password_char_check(pass_1_id) == false) {
        createAlert(
            "Password must have more than 8 characters, upper and lowercase, a number and symbol!",
            "warning");
        return false;
    }
    return true;
}

function new_task() {
    const task_content = window.prompt("Whats the task content?");
    if (task_content != null) {
        const task_elem = document.createElement("input");
        task_elem.setAttribute("type", "text");
        task_elem.setAttribute("name", "atask");
        task_elem.setAttribute("value", task_content);
        document.getElementById("created_tasks").append(task_elem);
    }
}

function remove_elem_children(elem) {
    // removes a given elements children
    while (elem.hasChildNodes()) {
        elem.removeChild(elem.lastChild);
    }
}

function create_option_into_select(select_elem, option_val) {
    // appends a new child the the select element given
    const the_option = document.createElement("option");
    the_option.value = option_val;
    the_option.innerText = option_val;
    select_elem.appendChild(the_option);
}

/**
 * To load options into a select element using fetch
 *
 * @param {String} select_id - the id of the select element
 * @param {String} url - the url for the request
 * @param {String} main_loc - the main location (photo database)
 * @param {String} first_option_inner - what the inner text of the first option should be
*/
function start_load_options_to_select(select_id, url, main_loc, first_option_inner = '**Show All**') {
    //TODO split into API func
    const select_elem = document.getElementById(select_id);
    // disable select box while loading
    select_elem.setAttribute("disabled", true);
    // remove prev items from select box
    remove_elem_children(select_elem);
    if (main_loc === '') { return }
    url = url + "?mainloc=" + main_loc
    fetch(url)
        .then((response) => { return response.json() })
        .then((conv_json) => {
            remove_elem_children(select_elem);
            const show_all_option = document.createElement("option");
            show_all_option.value = "";
            show_all_option.innerText = first_option_inner;
            select_elem.append(show_all_option);
            for (const i in conv_json.sublocs) {
                create_option_into_select(select_elem, conv_json.sublocs[i].name);
            }
            select_elem.removeAttribute("disabled");
        })
        .catch((error) => { console.error("Error", error) });
}

function add_active_events(func, useCapture = true, triggers = active_events) {
    // adds move and button listeners to a function
    active_events.forEach(function (name) {
        document.addEventListener(name, func, useCapture);
    });
}

/**
 * allows for the custom expire or pre set dates to be picked, used on fm/edit
 */
function custom_expire_onclick() {
    const custom_expire = document.getElementById("custom_expire");
    const expire_select_label = document.getElementById("expire_select_label");
    const expire_select = document.getElementById("expire_select");
    const expire_date_label = document.getElementById("expire_date_label");
    const expire_date = document.getElementById("expire_date");
    if (custom_expire.checked == false) {
        expire_select.removeAttribute("disabled");
        expire_date.setAttribute("disabled", true);
        expire_select.style.removeProperty("display");
        expire_select_label.style.removeProperty("display");
        expire_date_label.style.setProperty("display", "none");
        expire_date.style.setProperty("display", "none");
    }
    else if (custom_expire.checked == true) {
        expire_select.setAttribute("disabled", true);
        expire_date.removeAttribute("disabled");
        expire_select.style.setProperty("display", "none");
        expire_date.style.removeProperty("display");
        expire_select_label.style.setProperty("display", "none");
        expire_date_label.style.removeProperty("display");
    }
}

function get_child_pos(children, child) {
    return Array.prototype.indexOf.call(children, child);
}

/**
 * copy a elements value to clipboard
 * @param {string} elem_id - the input element id to copy from
 */
function copy_elem_clipboard(elem_id) {
    navigator.permissions.query({ name: "clipboard-write" }).then(result => {
        if (result.state == "granted" || result.state == "prompt") {
            const value = document.getElementById(elem_id).value;
            navigator.clipboard.writeText(value);
        }
    });
}

/**
 * change an input from password type and text
 * @param {string} input_id - the element id to toggle
 */
function pass_show_hide(input_id) {
    const input_elem = document.getElementById(input_id);
    if (input_elem.type === "password") {
        input_elem.type = "text";
    }
    else {
        input_elem.type = "password";
    }
}

/**
 * opens a new browser tab with a print friendly version of the table given,
 * and opens the print menu ready for printing
 * @param {string} table_id - the table id to copy from
 * @param {string} title - a optional title for the page
 * @param {boolean} skip_last_col - the table last column needs removing
 */
function print_friendly_table(table_id, title = null, skip_last_col = false) {
    const table_elem = document.getElementById(table_id).cloneNode(true);
    table_elem.style.setProperty("border-spacing", "8px");
    const w = window.open();
    const hts_title = w.document.createElement("h2");
    hts_title.innerText = "Home Terminal System";
    w.document.body.append(hts_title);
    if (title) {
        const title_elem = w.document.createElement("h3");
        title_elem.innerText = title;
        w.document.body.append(title_elem);
    }
    w.document.body.append(table_elem);
    if (skip_last_col) {
        const rows = table_elem.querySelectorAll("tr");
        rows.forEach(row => {
            row.lastElementChild.remove();
        });
    }
    w.print();
}

/**
 *
 * @param {string} theme_name - the name of the theme
 * @param {string} bnt_text - the text for the button
 * @param {string} curr_selected - what the current theme is
 * @returns {Element} the created button element
 */
function create_theme_picker_button(theme_name, bnt_text, curr_selected) {
    const elem = document.createElement('button');
    elem.addEventListener('click', _event => { change_theme(theme_name) });
    elem.innerText = bnt_text;
    if (curr_selected === theme_name) {
        elem.classList.add('ok');
    }
    return elem;
}

/**
 * opens(creates) or closes(removes) the site theme picker
 */
function toggle_theme_picker() {
    var curr_theme = window.localStorage.getItem(THEME_KEYNAME);
    if (curr_theme === null) { curr_theme = THEMES.OS_PREF }
    var the_box = document.getElementById('theme-selection');
    if (the_box) {
        the_box.remove();
    }
    else {
        const header = document.getElementsByTagName('header')[0];
        const navbar = document.getElementsByTagName('nav')[0];
        the_box = document.createElement('div');
        the_box.id = 'theme-selection';

        the_box.appendChild(create_theme_picker_button(THEMES.LIGHT, "Light", curr_theme));
        the_box.appendChild(create_theme_picker_button(THEMES.DARK, "Dark", curr_theme));
        the_box.appendChild(create_theme_picker_button(THEMES.SOLARIZED_DARK, "Solarized Dark", curr_theme));
        the_box.appendChild(create_theme_picker_button(THEMES.OS_PREF, "OS Theme", curr_theme));

        header.insertBefore(the_box, navbar.nextSibling);
    }
}

/**
 * change page theme cookie and load the theme
 * @param {string} new_theme - the theme name
 */
function change_theme(new_theme) {
    window.localStorage.setItem(THEME_KEYNAME, new_theme);
    if (new_theme === THEMES.OS_PREF) {
        location.reload();
    }
    load_theme();
    toggle_theme_picker();
}

/**
 * loads the theme currently selected in local storage
 */
function load_theme() {
    var curr_theme = window.localStorage.getItem(THEME_KEYNAME);
    if (curr_theme === null) { curr_theme = THEMES.OS_PREF }
    if (curr_theme === THEMES.LIGHT){
        document.documentElement.style.setProperty("--green", "#007800");
        document.documentElement.style.setProperty("--orange", "#ff9900");
        document.documentElement.style.setProperty("--blue", "#2195f3");
        document.documentElement.style.setProperty("--red", "#f44437");
        document.documentElement.style.setProperty("--main-background", "#e6e6e6");
        document.documentElement.style.setProperty("--content-background", "#c4c4c4");
        document.documentElement.style.setProperty("--border-col", "#797979");
        document.documentElement.style.setProperty("--dark-text", "#000000");
        document.documentElement.style.setProperty("--light-text", "#ffffff");
        document.documentElement.style.setProperty("--bnt-col", "#a7a7a7");
    }
    else if (curr_theme === THEMES.DARK || curr_theme === THEMES.SOLARIZED_DARK){
        document.documentElement.style.setProperty("--green", "#015801");
        document.documentElement.style.setProperty("--orange", "#c27400");
        document.documentElement.style.setProperty("--blue", "#1e76be");
        document.documentElement.style.setProperty("--red", "#b4281e");
        if (curr_theme === THEMES.DARK){
            document.documentElement.style.setProperty("--main-background", "#152020");
            document.documentElement.style.setProperty("--content-background", "#1a1a1a");
            document.documentElement.style.setProperty("--border-col", "#303030");
            document.documentElement.style.setProperty("--dark-text", "#e9e9e9");
            document.documentElement.style.setProperty("--light-text", "#e9e9e9");
            document.documentElement.style.setProperty("--bnt-col", "#3b3b3b");
        }
        else{
            // solarized dark theme
            document.documentElement.style.setProperty("--main-background", "#002b36");
            document.documentElement.style.setProperty("--content-background", "#073540");
            document.documentElement.style.setProperty("--border-col", "#334348");
            document.documentElement.style.setProperty("--dark-text", "#bcbcbc");
            document.documentElement.style.setProperty("--light-text", "#bcbcbc");
            document.documentElement.style.setProperty("--bnt-col", "#013d4b");
        }
    }
    // OS theme does not need changing as it OS defines it
}

// handles showing WebSocket notifications
window.addEventListener("ws_notif_mess", (event) => {
    if (event.detail.type_id == TYPES.NOTIFICATION.MESSAGE) {
        createAlert(event.detail.message, event.detail.category);
    }
});

window.addEventListener("ws_update_messages", (_event) => {
    do_messages_refresh();
});

window.addEventListener("load", _event => { load_theme() }, { once:true });
