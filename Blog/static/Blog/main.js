$(document).ready(function() {
    $('.copy').on('click', function(event) {
        //Check if the request if for a blog or the window
        if ($(this).data) {
            var text = $(this).data('text');
        } else {
            var text = window.location.href;
        }
        console.log('link:', text);
        var dummy = document.createElement('input');
        $('body').append(dummy);
        dummy.value = text;
        dummy.select();
        //For IE
        if (window.clipboardData) {
            window.clipboardData.setData('Text', text);
        } else {
            document.execCommand('copy');
            event.preventDefault();
        }
        // dummy.value = 'Link copied successfully'
        // dummy.dialog();
        alert('Link copied successfully');
        $('body').remove(dummy);
    });
    $('.bookmark').on('click', function(event) {
        console.log('Bookmark button pressed');
        var slug = $(this).data('post');
        console.log(slug);
        event.preventDefault();
    });
});