document.addEventListener('DOMContentLoaded', function () {
    let state = false;
    let button = document.querySelector('#select_button');

    button.addEventListener('click', function (event) {
        let checkboxes = document.querySelectorAll('.checkbox');
        state = !state;
        button.innerText = state ? 'Unselect all' : 'Select all';
        for (let checkbox of checkboxes) {
            checkbox.checked = state;
        }
    })
})
