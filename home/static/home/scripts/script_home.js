function adjustSizeHeaderFooter() {
    // to get it normal from 100% (1245) to +/- 25% --> 75% (1660) to 125 %(996)
    // for smaller screen sizes <996 , like mobile phones, make @media in CSS 
    var screenWidth = window.innerWidth;
    var footerBanner = document.getElementById('FooterBanner');
    var listItems = document.getElementById('navbarList').getElementsByTagName('li');
    var navbarImage = document.getElementById('navbarImage')
    var images = footerBanner.getElementsByClassName('footer-image');
    var baseFontSize = 8; // Base font size <p> on navbar
    var baseImageSizeHeader = 50; // Base image size in pixels
    var baseImageSizeFooter = 30; // Base image size in pixels

    // Calculate steps based on screen width 
    var steps = Math.floor((screenWidth - 700) / 75); // Adjust step size as needed
    var stepsImage = Math.floor((screenWidth - 700) / 5); // Adjust step size as needed

    // Set the font size <p> 
    var fontSize = baseFontSize + steps;
    footerBanner.style.fontSize = fontSize + 'px';
    // Set the font size of all items li in list ul
    for (var i = 0; i < listItems.length; i++) {
        listItems[i].style.fontSize = fontSize + 'px';
    }
    // Set the image size header
    var ImageSizeHeader = baseImageSizeHeader + stepsImage;
    navbarImage.style.width = ImageSizeHeader + 'px';
    // Set the images sizes in footer
   var ImageSizeFooter = baseImageSizeFooter + steps;
   for (var i = 0; i < images.length; i++) {
       images[i].style.width = ImageSizeFooter + 'px';
   }
}
function adjustSizeTopBanner() {
    // to get it normal from 100% (1245) to +/- 25% --> 75% (1660) to 125 %(996)
    // for smaller screen sizes <996 , like mobile phones, make @media in CSS 
    var screenWidth = window.innerWidth;
    var topBanner = document.getElementsByClassName('topBannertext');
    //var topImage = document.getElementById('navbarImage');
    var basetopBanner = 40; // Base font size in pixels
    //var basetopImage = 12; //Base image size 

    // Calculate steps based on screen width 
    var fontsteps = Math.floor((screenWidth - 700) / 5); // Adjust step size as needed
    //var stepsImage = Math.floor((screenWidth - 700) / 5); // Adjust step size as needed

    // Set the font size <p> 
    var fontSize = basetopBanner + fontsteps;
    topBanner.style.fontSize = fontSize + 'px';
    
}


// Call the function on page load and resize
window.onload = adjustSizeHeaderFooter; // Header and footer 
window.onresize = adjustSizeHeaderFooter; // Header and footer
//window.onload = adjustSizeTopBanner; // Top banner --> hier gaat het fout 
//window.onresize = adjustSizeTopBanner; // Top banner 