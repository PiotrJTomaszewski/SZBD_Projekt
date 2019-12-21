function enter_exit_edit_mode() {
    let edit_mode_elements = document.getElementsByClassName('edit_mode_element');
    if (document.getElementById("edit_mode_box").checked === true) {
        for (let i = 0; i < edit_mode_elements.length; ++i) {
            edit_mode_elements[i].style.display = 'block';
        }
    }
    else {
        for (let i = 0; i < edit_mode_elements.length; ++i) {
            edit_mode_elements[i].style.display = 'none';

        }
    }
}
document.getElementById("edit_mode_box").onclick = function () {
    enter_exit_edit_mode();
};