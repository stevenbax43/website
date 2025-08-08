function toggleNavbar() {
    const navbarList = document.getElementById('navbarList');
    navbarList.classList.toggle('active');
}

// common.js — loaded on every page
document.addEventListener('DOMContentLoaded', () => {
// If we’re *not* on the Mollier page, clear the flag
if (location.pathname !== '/tools/mollierdiagram') {
    sessionStorage.removeItem('mollierInitialized');
}
});