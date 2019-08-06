function rgb2hex(rgb) {
  if (  rgb.search("rgb") == -1 ) {
       return rgb;
  } else {
       rgb = rgb.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+))?\)$/);
       function hex(x) {
            return ("0" + parseInt(x).toString(16)).slice(-2);
       }
       return hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]); 
  }
}

function currentNavbarBgColorFromStorage()
{
  if (navBgColorStorage != undefined)
  {
    //document.querySelector('body').style.backgroundColor = "#" + navBgColorStorage; // body for testing
    if (navbar != undefined)
    {
      navbar.style.backgroundColor="#"+navBgColorStorage;
    }
    if (navbarBgColorPicker != undefined)
    {
      navbarBgColorPicker.value = "#"+navBgColorStorage;
    }
  }
  else{
    if(navbar != undefined)
    {
      navBgColorStorage = rgb2hex(navbar.style.backgroundColor);
      localStorage.setItem('navBgColor',navBgColorStorage);
    }
  }
}


function addNavbarBgColorEventListener()
{
  if (navbarBgColorPicker != undefined && navbarBgColorPickerBtn != undefined)
  {
    navbarBgColorPickerBtn.addEventListener('click',function(e)
    {
      e.preventDefault();
      navBgColorStorage = navbarBgColorPicker.value;
      localStorage.setItem('navBgColor',navBgColorStorage);
      if(navbar != undefined)
      {
        navbar.style.backgroundColor = "#" + navBgColorStorage;
      }
      //document.querySelector('body').style.backgroundColor = "#" + navBgColorStorage; // body for testing
    });
  }
}

const navbar = document.querySelector('nav.navbar');
const navbarBgColorPickerBtn = document.querySelector('#navbar-bg-color-picker-btn');
const navbarBgColorPicker = document.querySelector('#navbar-bg-color-picker');
let navBgColorStorage = localStorage.getItem('navBgColor');

currentNavbarBgColorFromStorage();
addNavbarBgColorEventListener();