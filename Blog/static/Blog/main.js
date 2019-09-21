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
        createResponse('info', 'Link Copied Successfully');
    });
    $('.bookmark').on('click', function(event) {
        event.preventDefault();
        var post = $(this).data('post');
        url = 'post/bookmark';
        sendAjax(url, post);
    });
});

function sendAjax(link, data) {
    $.ajax({
        type: 'POST',
        headers: { 'X-CSRFToken': window.CSRF_TOKEN },
        url: link,
        contentType: 'application/json',
        // dataType: 'json',
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
            createResponse(state, msg);
        },
    });
}

function createResponse(status, msg) {
    let cls = 'alert alert-' + status;
    var response = $('#response');
    // var dummy = response.add('<div>');
    // let temp = `<div class="alert ${cls}"` + `>${msg}</div>`;
    var temp = $('<div/>')
        .addClass(cls)
        .html('<div>' + msg + '</div>');
    // console.log(temp);
    response.append(temp);
    setTimeout(function() {
        temp.remove();
    }, 5000);
}