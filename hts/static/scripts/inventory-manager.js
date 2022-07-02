"use strict";

let typingTimer;

function mark_typing(input, datalist_id, url){
    clearTimeout(typingTimer);
    if (input.value)
    typingTimer = setTimeout(() => {
        liveSearch(input, datalist_id, url);
    },500);
}

function liveSearch(input, datalist_id, url) {
    const data_list = document.getElementById(datalist_id);
    fetch(url, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ itemname: input.value }),
    })
        .then(data => data.json(data))
        .then(data => {
            data_list.textContent = '';
            data.item_names.forEach(elem => {
                const new_option = document.createElement("option");
                new_option.value = elem;
                new_option.innerText = elem;
                data_list.append(new_option);
            });
        })
        .catch(console.error);
}
