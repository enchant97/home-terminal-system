"use strict";

const active_events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];

function gen_datetime() {
  var date = new Date();
  var h = date.getHours();
  var m = date.getMinutes();
  var dd = date.getDate();
  var mm = date.getMonth();
  if (h < 10) { h = '0' + h }
  if (m < 10) { m = '0' + m }
  if (dd < 10) { dd = '0' + dd }
  if (mm < 10) { mm = '0' + mm }
  document.getElementById("timebox").innerHTML = `${h}:${m}`;
  document.getElementById("datebox").innerHTML = `${dd}-${mm}-${date.getFullYear()}`;
}

function createAlert(message, category) {
  var box = document.createElement("div");
  box.innerText = message;
  box.classList.add("alert");
  box.classList.add(category);
  var bnt = document.createElement("span");
  bnt.classList.add("closebtn");
  bnt.onclick = function () { this.parentElement.style.display = 'none'; };
  bnt.innerText = "×";
  var mess = document.createElement("strong");
  mess.innerText = category;
  box.appendChild(bnt);
  box.appendChild(mess);
  document.body.insertBefore(box, document.body.childNodes[0]);
}

function togg_element_onclick(checkbox_id, ...elements) {
  const checkbox = document.getElementById(checkbox_id);
  if (checkbox.checked == false) {
    for (let i = 0; i < elements.length; i++) {
      const selected_element = document.getElementById(elements[i]);
      selected_element.disabled = false;
    }
  } else {
    for (let i = 0; i < elements.length; i++) {
      const selected_element = document.getElementById(elements[i]);
      selected_element.disabled = true;
    }
  }
}

function password_char_check(password) {
  // at least one number, one lowercase and one uppercase letter
  // at least 8 characters
  var re = /(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}/;
  return re.test(password);
}

function validate_password(pass_1_id, pass_2_id, username_id) {
  pass_1_id = document.getElementById(pass_1_id).value;
  pass_2_id = document.getElementById(pass_2_id).value;
  username_id = document.getElementById(username_id).value;
  if (pass_1_id != pass_2_id) {
    createAlert("Passwords do not match!", "warning");
    return false;
  } else if (pass_1_id == username_id) {
    createAlert("Password cannot be username", "warning");
    return false;
  } else if (password_char_check(pass_1_id) == false) {
    createAlert(
      "Password must have more than 8 characters, upper and lowercase, a number and symbol!",
      "warning"
    );
    return false;
  }
  return true;
}

function new_task() {
  var task_content = window.prompt("Whats the task content?");
  if (task_content != null) {
    var task_elem = document.createElement("input");
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
  var the_option = document.createElement("option");
  the_option.value = option_val;
  the_option.innerText = option_val;
  select_elem.appendChild(the_option);
}

function start_load_options_to_select(select_id, url, main_loc, first_option_inner = 'Show All') {
  /**
   * To load options into a select element using fetch
   *
   * @param {String} select_id - the id of the select element
   * @param {String} url - the url for the request
   * @param {String} main_loc - the main location (photo database)
   * @param {String} first_option_inner - what the inner text of the first option should be
  */
  if (main_loc == '') { return }
  var select_elem = document.getElementById(select_id);
  url = url + "?mainloc=" + main_loc
  fetch(url)
    .then((response) => {
      return response.json();
    })
    .then((conv_json) => {
      remove_elem_children(select_elem);
      const show_all_option = document.createElement("option");
      show_all_option.value = "";
      show_all_option.innerText = first_option_inner;
      select_elem.append(show_all_option);
      for (const i in conv_json.sublocs) {
        create_option_into_select(select_elem, conv_json.sublocs[i].name);
      }
    })
    .catch((error) => {
      console.error("Error", error);
    });
}

function add_active_events(func, useCapture = true, triggers = active_events) {
  // adds move and button listeners to a function
  active_events.forEach(function (name) {
    document.addEventListener(name, func, useCapture);
  });
}

function custom_expire_onclick() {
  // allows for the custom expire or pre set dates to be picked, used on fm/edit
  const custom_expire = document.getElementById("custom_expire");
  const expire_3 = document.getElementById("expire_3");
  const expire_6 = document.getElementById("expire_6");
  const expire_12 = document.getElementById("expire_12");
  const expire_date = document.getElementById("expire_date");
  if (custom_expire.checked == false) {
    expire_3.disabled = false;
    expire_6.disabled = false;
    expire_12.disabled = false;
    expire_date.disabled = true;
  }
  else if (custom_expire.checked == true) {
    expire_3.disabled = true;
    expire_6.disabled = true;
    expire_12.disabled = true;
    expire_date.disabled = false;
  }
}
