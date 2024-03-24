const menu = document.querySelector(".fa-bars")
const closeX = document.querySelector(".fa-times")
const items = document.querySelector(".menu-items")

const image = document.querySelector(".image");
const price = document.querySelector(".price");
const desc = document.querySelector(".desc");

// all event listener
menu.addEventListener('click',openMenu);
closeX.addEventListener('click',closeMenu)

// function to open the menu
function openMenu(){
    items.classList.add('show')
    menu.style.display = "none"
}

// function to close the menu
function closeMenu(){
    items.classList.remove('show')
    menu.style.display = "block"
    
}