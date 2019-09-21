$(document).ready(function() {
    $('.copy').on('click', function(event) {
        event.preventDefault();
        //Check if the request if for a blog or the window
        if ($(this).data) {
            var text = $(this).data('text');
        } else {
            var text = window.location.href;
        }
        // console.log('link:', text);
        var dummy = document.createElement('input');
        $('body').append(dummy);
        dummy.value = text;
        dummy.select();
        //For IE
        if (window.clipboardData) {
            window.clipboardData.setData('Text', text);
        } else {
            document.execCommand('copy');
        }
        $(dummy).remove();
        createResponse($(this), 'success', 'Link Copied Successfully');
    });
    $('.bookmark').on('click', function(event) {
        event.preventDefault();
        var post = $(this).data('post');
        url = 'post/bookmark';
        sendAjax($(this), url, post);
    });
});

function sendAjax(obj, link, data) {
    $.ajax({
        type: 'POST',
        headers: { 'X-CSRFToken': window.CSRF_TOKEN },
        url: link,
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify({ 'data': data }),
        error: function(jqXhr, textStatus, errorMessage) {
            // console.log('Error Message:' + errorMessage);
        },
        success: function(data, status, xhr) {
            // console.log('status:' + status + ', data:' + data);
        },
        complete: function(data) {
            // console.log(data.responseJSON['message']);
            if (data.responseJSON['status'] === 0)
                var state = 'success';
            else
                var state = 'warning';
            var msg = data.responseJSON['message'];
            createResponse(obj, state, msg);
        },
    });
}

function createResponse(obj, status, msg) {
    var response = $('<div>').attr('id', 'response')
        .addClass('alert alert-' + status)
        .html('<div>' + msg + '</div')
    obj.append(response);
    setTimeout(function() {
        $('#response').remove()
    }, 5000);
}