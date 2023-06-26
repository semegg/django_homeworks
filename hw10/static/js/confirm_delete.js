document.addEventListener('DOMContentLoaded', function () {
    const deleteBtn = document.getElementById('deleteBtn');
    const closeBtn = document.getElementById('closeBtn');
    const confirmDeleteBtn = document.getElementById('confirmDelete');

    const modalElement = document.getElementById('exampleModal');
    const modal = new bootstrap.Modal(modalElement);

    deleteBtn.addEventListener('click', function (event) {
        event.preventDefault();
        modal.show();
    });

    confirmDeleteBtn.addEventListener('click', function (){
       const deleteUrl = deleteBtn.getAttribute('data-url');
       window.location.href = deleteUrl;
    });

    closeBtn.addEventListener('click', function () {
        modal.hide()
    })
})
