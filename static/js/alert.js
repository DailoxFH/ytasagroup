/* 
https://www.codingnepalweb.com/custom-warning-alert-notification/ 
*/
function showAlert() {
    var alert = document.getElementsByClassName("alert")[0];
    alert.classList.add("show");
    alert.classList.remove("hide");
    alert.classList.add("showAlert");
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setTimeout(function () {
        alert.classList.remove("show");
        alert.classList.add("hide");
    }, 5000);
};

document.getElementsByClassName("close-btn")[0].addEventListener("click", function () {
    var alert = document.getElementsByClassName("alert")[0];
    alert.classList.remove("show");
    alert.classList.add("hide");
});
/**/ 