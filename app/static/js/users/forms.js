$(document).ready(function() {
    var alertBtns = document.querySelectorAll('.alert button');

    alertBtns.forEach(function(e) {
        e.addEventListener('click', function(evt) {
            evt.preventDefault();
            e.parentNode.style.display = 'none';
        })
    });
});