'use strict';

$(document).ready(function(event) {
    if (window.matchMedia('(max-width: 600px)').matches) {
        onMobile();
    }
    $('.subForm').submit(subscribe);
    loadSidebar();
    addClassToAsideFeatured();
    $('.dropdown').on('click focus', function(event) {
        $('.dropdown-menu').toggleClass('visible');
        $('.dropdown').find('.dropdown-toggle').css('outline', 'none');
    });
    $('.copy').on('click', function(event) {
        event.preventDefault();
        //Check if the request if for a blog or the window
        if ($(this).data) {
            const text = $(this).data('text');
        } else {
            const text = window.location.href;
        }
        // console.log('link:', text);
        const dummy = document.createElement('input');
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
        const parent = event.currentTarget;
        event.preventDefault();
        // console.log(event.currentTarget);
        const post = $(this).data('post');
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
        sendAjax(url, { data: post });
    });
});
/**
 * Sends an AJAX request and fixes the response to the top and is faded after sometime.
 * @param {string} link - Link where the AJAX request is to be sent 
 * @param {object} args - The args object may contain the atttributes {type, data, responseType}
 * If not passed their default value will be :
 * type:POST
 * data:''
 * responseType:json  
 */
function sendAjax(link, args) {
    // const responseType = 'application/'
    if (typeof args.type === "undefined") {
        const type = 'POST';
    } else {
        const type = args.type;
    }
    if (typeof args.data === "undefined") {
        const data = '';
    } else {
        const data = args.data;
    }
    if (typeof args.responseType === "undefined") {
        const responseType = 'json';
    } else {
        const responseType = args.responseType;
    }
    // console.log(type, data, responseType, link)
    $.ajax({
        type: type,
        headers: { 'X-CSRFToken': window.CSRF_TOKEN },
        url: link,
        contentType: 'application/' + responseType,
        // dataType: 'json',
        data: JSON.stringify({ 'data': data }),
        error: function(jqXhr, textStatus, errorMessage) {
            // console.log('Error Message:' + errorMessage);
        },
        success: function(data, status, xhr) {
            // console.log('status:' + status + ', data:' + data);
            // return data;
        },
        complete: function(data) {
            try {
                // console.log(data.responseJSON['message']);
                // if (data.responseJSON['status'] === 0) {
                //     const state = 'success';
                // } else {
                //     const state = 'warning';
                // }
                const state = data.responseJSON['status'];
                const msg = data.responseJSON['message'];
                createResponse(state, msg);
            } catch (e) {
                top.location.href = '/login';
                // console.log(data);
                // console.log(e);
            }
        },
    });
}
/**
 * Create a temporary div, append it to the div'#response', fix it to the top and fade it.
 * @param {int} status - an integer based upon the response received for AJAX request.
 * (-1->'error'|0->'success'| 1->'warning')
 * @param {string} msg - a string depicting the message to be displayed in the response. 
 * @param {int} time - time after which the response fades away
 */
function createResponse(status, msg, time = 2000) {
    switch (status) {
        case -1:
            status = "danger";
            break;
        case 0:
            status = "success";
            break;
        case 1:
            status = "warning";
    }
    const cls = 'alert alert-' + status;
    const response = $('#response');
    const temp = $('<div/>')
        .addClass(cls)
        .html('<div>' + msg + '</div>');
    // console.log(temp);
    response.append(temp);
    fixToTop(temp);
    temp.fadeIn(time);
    temp.fadeOut(2 * time);
    setTimeout(function() {
        temp.remove();
    }, 2 * time + 10);
}
/**
 * Fixes an element to the top of the viewport.
 * @param {element} div - element that is to be fixed at the top of the viewport. 
 */
function fixToTop(div) {
    const isfixed = div.css('position') == 'fixed';
    if (div.scrollTop() > 200 && !isfixed)
        div.css({ 'position': 'fixed', 'top': '0px' });
    if (div.scrollTop < 200 && isfixed)
        div.css({ 'position': 'static', 'top': '0px' });
}

/**
 * Loads the side through different post requests.
 * On homepage trending posts will be added later.
 * top tags.
 * all tags.
 * On pages other than homepage, latest and featured posts will be added.
 */
function loadSidebar() {
    const latestPosts = { id: '#latest-posts', num: 5 };
    latestPosts.url = $(latestPosts.id).data('url');
    sendPost(latestPosts.url, latestPosts.id, { 'num': latestPosts.num });
    const topTagsEle = { id: '#top-tags', num: 5 };
    topTagsEle.url = $(topTagsEle.id).data('url');
    sendPost(topTagsEle.url, topTagsEle.id, { 'num': topTagsEle.num });
    const allTagsEle = { id: '#all-tags' };
    allTagsEle.url = $(allTagsEle.id).data('url');
    sendPost(allTagsEle.url, allTagsEle.id);
}

function sendPost(url, responseEle, data) {
    $.post(url, { data: JSON.stringify(data), 'csrfmiddlewaretoken': window.CSRF_TOKEN }, function(response) {
        $(responseEle).append(response);
    })
}
/**
 * Used for styling the featured articles aside of the latest one.
 * Add a div alongwith a class aside to the other two featured articles(apart from the latest).
 * The styling is done in CSS to place them alongside the latest one in small scale devices.
 */
function addClassToAsideFeatured() {
    const div = document.createElement('div');
    div.className = 'aside';
    $('.aside-featured').wrapAll(div);
}
/**
 * This function is used to make changes to the layout for small screen devices
 */
function onMobile() {
    const viewbutton = $('.view-more');
    viewbutton.each(function() { $(this).parent().next().after($(this)) });
}

/**
 * 
 * @param {event} event - The event that takes care 
 */
function subscribe(event) {
    const responseDiv = $('#sub-response');
    const email = $('#email').val();
    responseDiv.html('Registering ' + email + ' with HackAdda!');
    const url = $(this)[0].action;
    const data = $(this).serialize;
    $.ajax({
        url: url,
        type: 'POST',
        data: $(this).serialize(),
        dataType: 'json',
        // error: function(jqXhr, textStatus, errorMessage) {
        // console.log('Error Message:' + errorMessage);
        // },
        complete: function(data) {
            data = data.responseJSON;
            createResponse(data['status'], data['email'] + data['msg']);
            responseDiv.html('');
            if (data['status'] !== -1) {
                email.val('');
            }
        }
    });
    event.preventDefault();
}