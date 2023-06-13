window.onload = function () {
    let showChangePasswordCheckbox = document.getElementById('show_password_change');
    if (showChangePasswordCheckbox !== null) {
        showPasswordChange();
    }

    let showRegisterPasswordCheckbox = document.getElementById('show_password_register');
    if (showRegisterPasswordCheckbox !== null) {
        showPasswordRegister();
    }

}

function showPasswordChange() {
    let password1 = document.getElementById('id_new_password1');
    let password2 = document.getElementById('id_new_password2');
    let showChangePasswordCheckbox = document.getElementById('show_password_change');

    showChangePasswordCheckbox.addEventListener('change', function () {
      if (showChangePasswordCheckbox.checked) {
          password1.type = 'text';
          password2.type = 'text';
      }  else {
          password1.type = 'password';
          password2.type = 'password';
      }
    })
}


function showPasswordRegister() {
    let password1 = document.getElementById('id_password1');
    let password2 = document.getElementById('id_password2');
    let showChangePasswordCheckbox = document.getElementById('show_password_register');

    showChangePasswordCheckbox.addEventListener('change', function () {
      if (showChangePasswordCheckbox.checked) {
          password1.type = 'text';
          password2.type = 'text';
      }  else {
          password1.type = 'password';
          password2.type = 'password';
      }
    })
}
