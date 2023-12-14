function login_auth (){
  $.ajax({
    type: "GET",
    url: "/auth_login",
    data: {},
    success: function (response) {
      if (response["result"] == "success") {
        if(response.data.level == "1"){
          let temp_navbar = `
          <ul>
            <li><a href="/" id="navhome">Home</a></li>
            <li><a href="/content" id="navcontent">Content</a></li>
            <li><a href="/dashboard" id="navmedia">Dashboard</a></li>
            <li><a href="/about" id="navabout">About Us</a></li>
            <li><a class="" onclick="sign_out()" style="cursor: pointer" id="navlogout">Logout</a></li>
          </ul>
  `;
  $('#navbar').append(temp_navbar);

        }else if(response.data.level == "2"){
        let temp_navbar = `
        <ul>
          <li><a href="/" id="navhome">Home</a></li>
          <li><a href="/content" id="navcontent">Content</a></li>
          <li><a href="/media" id="navmedia">Media</a></li>
          <li><a href="/about" id="navabout">About Us</a></li>
          <li><a class="" onclick="sign_out()" style="cursor: pointer" id="navlogout">Logout</a></li>
        </ul>
`;
$('#navbar').append(temp_navbar);
        }

      } else {
        let temp_navbar = `
          <ul>
            <li><a href="/" id="navhome">Home</a></li>
            <li><a href="/content" id="navcontent">Content</a></li>
            <li><a href="/media" id="navmedia">Media</a></li>
            <li><a href="/about" id="navabout">About Us</a></li>
            <li><a href="/login" id="navlogin">Login</a></li>
          </ul>
  `;
  
  $('#navbar').append(temp_navbar);
      }
    },
  });
}

login_auth();

function sign_out() {
  $.removeCookie("mytoken", { path: "/" });
  alert("Signed out!");
  window.location.href = "/login";
}

