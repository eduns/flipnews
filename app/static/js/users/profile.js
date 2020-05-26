$(document).ready(function() {
    var passwd = $('#password');
    $('#show_password').click(function() {
        if(passwd.prop('type') == 'password') {
            passwd.prop('type', 'text');
        } else {
            passwd.prop('type', 'password');
        }
    });
});