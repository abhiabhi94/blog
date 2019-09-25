$(document).ready(function(event) {
    // $('.dropdown').on('click', function(event) {
    //         console.log('Yipee!');
    //         $('.dropdown-content').css('display', 'block');
    //         // $('dropdown').dropdown('toggle');
    //     });
    //     // return false;);
    //     // $('.dropdown').on('mouseout', function(event) {
    //     //     $('.dropdown-content').css('display', 'none');
    //     // });
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
        var parent = event.currentTarget;
        event.preventDefault();
        // console.log(event.currentTarget);
        var post = $(this).data('post');
        url = $(this).data('url');
        if (parent.id === 'unbookmark') {
            // console.log('Removing');
            parent.children[0].style.color = 'darkgrey';
            parent.id = 'bookmark';
            parent.title = 'Bookmark this post';
        } else {
            // console.log('Bookmarking');
            parent.children[0].style.color = 'steelblue';
            parent.id = 'unbookmark';
            parent.title = 'Remove bookmark';
        }
        // $('#unbookmark').css('color', 'white');
        sendAjax(url, post);
    });
});

function sendAjax(link, data) {
    // console.log(link);
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
            try {
                // console.log(data.responseJSON['message']);
                if (data.responseJSON['status'] === 0) {
                    var state = 'success';
                } else {
                    var state = 'warning';
                }
                var msg = data.responseJSON['message'];
                createResponse(state, msg);
            } catch (e) {
                top.location.href = '/login';
                // console.log(data);
                // console.log(e);
            }
        },
    });
}

function createResponse(status, msg) {
    let cls = 'alert alert-' + status;
    var response = $('#response');
    var temp = $('<div/>')
        .addClass(cls)
        .html('<div>' + msg + '</div>');
    // console.log(temp);
    response.append(temp);
    var time = 2000;
    fixToTop(temp);
    temp.fadeIn(time);
    temp.fadeOut(2 * time);
    setTimeout(function() {
        temp.remove();
    }, 2 * time + 10);
}

function fixToTop(div) {
    var isfixed = div.css('position') == 'fixed';
    if (div.scrollTop() > 200 && !isfixed)
        div.css({ 'position': 'fixed', 'top': '0px' });
    if (div.scrollTop < 200 && isfixed)
        div.css({ 'position': 'static', 'top': '0px' });
}