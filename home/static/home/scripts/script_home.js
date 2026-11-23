// function toggleNavbar() {
//     const navbarList = document.getElementById('navbarList');
//     navbarList.classList.toggle('active');
// }

// common.js — loaded on every page
document.addEventListener('DOMContentLoaded', () => {
    const isMollierPage = location.pathname.includes('mollier');

    if (!isMollierPage) {
        sessionStorage.removeItem('mollierInitialized');
    }
});