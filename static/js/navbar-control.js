let temp_navbar = `
<i class="mobile-nav-toggle mobile-nav-show bi bi-list"></i>
      <i class="mobile-nav-toggle mobile-nav-hide d-none bi bi-x"></i>
      <nav id="navbar" class="navbar">
        <ul>
          <li><a href="/" class="active">Home</a></li>
          <li><a href="/content">Content</a></li>
          <li><a href="/media">Media</a></li>
          <li><a href="/about">About Us</a></li>
          <li><a href="/login">Login</a></li>
        </ul>
      </nav>
`;

$('#navbar-container').append(temp_navbar);