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
