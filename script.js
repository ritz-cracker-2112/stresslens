const burnoutPercent = 63;

const circle = document.querySelector(".circle span");

let count = 0;

const counter = setInterval(() => {

    count++;

    circle.textContent = count + "%";

    if(count >= burnoutPercent){
        clearInterval(counter);
    }

}, 20);
function showPage(pageId){

    document.querySelectorAll(".page").forEach(page => {
        page.classList.add("hidden");
    });

    document.getElementById(pageId).classList.remove("hidden");
}
const sidebar = document.getElementById("sidebar");
const menuBtn = document.getElementById("menuBtn");
const closeBtn = document.getElementById("closeBtn");

menuBtn.addEventListener("click", () => {
    sidebar.classList.add("open");
});

closeBtn.addEventListener("click", () => {
    sidebar.classList.remove("open");
});