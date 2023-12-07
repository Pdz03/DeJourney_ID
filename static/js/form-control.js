function openregister(){
    $('#regform').toggleClass("visually-hidden");
    $('#add-regform').toggleClass("visually-hidden");
    $('#add-logform').addClass("visually-hidden");
    $('#title-login').addClass("visually-hidden");
}

function openlogin(){
    $('#regform').addClass("visually-hidden");
    $('#add-regform').addClass("visually-hidden");
    $('#add-logform').toggleClass("visually-hidden");
    $('#title-login').toggleClass("visually-hidden");
}

function showpassword(){
    let password = $('#form-password')
    password.setAttribute("type", "text");
}

const togglePassword = document.querySelector("#togglePassword");
const password = document.querySelector("#form-password");

togglePassword.addEventListener("click", function () {
    // toggle the type attribute
    const type = password.getAttribute("type") === "password" ? "text" : "password";
    password.setAttribute("type", type);
    
    // toggle the icon
    this.classList.toggle("bi-eye");
});

const togglePassword2 = document.querySelector("#togglePassword2");
const password2 = document.querySelector("#form-password2");

togglePassword2.addEventListener("click", function () {
    // toggle the type attribute
    const type = password2.getAttribute("type") === "password" ? "text" : "password";
    password2.setAttribute("type", type);
    
    // toggle the icon
    this.classList.toggle("bi-eye");
});

function is_password(asValue) {
    var regExp = /^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,20}$/;
    return regExp.test(asValue);
}

function is_email(asValue) {
    var regExp = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
    return regExp.test(asValue);
}

function login(){
    let email = $('#form-email').val();
    let password = $('#form-password').val();

    console.log(email, password)
}

function resetform_login(){
    $('#form-email').val('');
    $('#form-password').val('');
}

function check_dup(){
    let inputUsername = $('#form-username');
    let username = inputUsername.val();
    let helpUsername = $('#help-username')

    if (username === "") {
        $('#fg-username')
            .removeClass('mb-3')
            .addClass('mb-1')
        helpUsername
          .text("Mohon masukkan username!")
          .addClass("text-danger");
        inputUsername.focus();
        return;
      }

      $.ajax({
        type: "POST",
        url: "/register/check_dup",
        data: {
          username_give: username,
        },
        success: function (response) {
          if (response["exists"]) {
            helpUsername
              .text("Username sudah digunakan!")
              .removeClass("text-dark")
              .addClass("text-danger");
            $("#input-username").focus();
          } else {
            $('#fg-username')
            .removeClass('mb-3')
            .addClass('mb-1')
            helpUsername
              .text("Username dapat digunakan!")
              .removeClass("text-danger")
              .addClass("text-success");
          }
        },
      });
}

function register(){
    let inputUsername = $('#form-username');
    let inputEmail = $('#form-email');
    let inputPassword = $('#form-password');
    let inputPassword2 = $('#form-password2');
    
    let username = inputUsername.val();
    let email = inputEmail.val();
    let password = inputPassword.val();
    let password2 = inputPassword2.val();

    let helpUsername = $('#help-username');
    let helpEmail = $('#help-email');
    let helpPassword = $('#help-password');
    let helpPassword2 = $('#help-password2');


    if (helpUsername.hasClass("text-danger")) {
      alert("Mohon cek username anda!");
      return;
    } else if (!helpUsername.hasClass("text-success")) {
      alert("Mohon cek ulang username anda!");
      return;
    }

    if (email === "") {
        $('#fg-email')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpEmail
          .text("Mohon masukkan email!")
          .removeClass("text-dark")
          .addClass("text-danger");
        inputEmail.focus();
        return;
      } else if (!is_email(email)) {
        $('#fg-email')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpEmail
          .text(
            "Masukkan email dengan benar (example@example.com)"
          )
          .removeClass("text-dark")
          .addClass("taxt-danger");
        inputEmail.focus();
      } else {
        $('#fg-email')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpEmail
          .text("Email dapat digunakan!")
          .removeClass("text-danger")
          .removeClass("text-dark")
          .addClass("text-success");
      }

    if (password === "") {
        helpPassword
          .text("Mohon masukkan password!")
          .removeClass("text-dark")
          .addClass("text-danger");
        inputPassword.focus();
        return;
      } else if (!is_password(password)) {
        helpPassword
          .text(
            "Masukkan password dengan 8-10 karakter, angka, atau spesial karakter (!@#$%^&*)"
          )
          .removeClass("text-dark")
          .addClass("taxt-danger");
        inputPassword.focus();
      } else {
        helpPassword
          .text("Password dapat digunakan!")
          .removeClass("text-danger")
          .removeClass("text-dark")
          .addClass("text-success");
      }

    if (password2 === ""){
        $('#fg-password2')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpPassword2
        .text(
          "Masukkan ulang password!"
        )
        .removeClass("text-dark")
        .addClass("taxt-danger");
      inputPassword2.focus();
      } else if (password2 !== password){
        $('#fg-password2')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpPassword2
        .text(
          "Masukkan password yang sama dengan sebelumnya!"
        )
        .addClass("taxt-danger");
      inputPassword2.focus();
    } else {
        helpPassword2
        .text("Password sesuai!")
        .removeClass("text-danger")
        .addClass("text-success");
    }

    $.ajax({
      type: "POST",
      url: "/register",
      data: {
        username_give: username,
        email_give: email,
        password_give: password,
      },
      success: function (response) {
        console.log(response.data);
        alert("Akun anda telah terdaftar!");
        window.location.replace("/login?email="+response.data);
      },
    });
}

function resetform_register(){
    $('#form-email').val('');
    $('#form-password').val('');
}