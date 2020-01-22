'use strict';

$(document).ready(function(event) {
    if (window.matchMedia('(max-width: 600px)').matches) {
        onMobile();
    } else {
        const pos = '1';
        loadAccessibityMenu(pos);
    }
    $('.subForm').submit(subscribe);
    marginFirstHeading();
    loadSidebar();
    addClassToAsideFeatured();
    $('.dropdown').on('click focus', function(event) {
        $('.dropdown-menu').toggleClass('visible');
        $('.dropdown').find('.dropdown-toggle').css('outline', 'none');
    });
    $('.copy').on('click', function(event) {
        event.preventDefault();
        //Check if the request if for a blog or the window
        let text;
        if ($(this).data) {
            text = $(this).data('text');
        } else {
            text = window.location.href;
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
        const url = $(this).data('url');
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
    // const responseType = 'application/
    let type, data, responseType;
    if (typeof args.type === "undefined") {
        type = 'POST';
    } else {
        type = args.type;
    }
    if (typeof args.data === "undefined") {
        data = '';
    } else {
        data = args.data;
    }
    if (typeof args.responseType === "undefined") {
        responseType = 'json';
    } else {
        responseType = args.responseType;
    }
    // console.log(type, data, responseType, link);
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
    const latestPosts = { id: '#latest-posts', top_n: 5 };
    latestPosts.url = $(latestPosts.id).data('url');
    sendPost(latestPosts.url, latestPosts.id, { 'top_n': latestPosts.top_n });

    const trendingPosts = { id: '#trending-posts', top_n: 5 };
    trendingPosts.url = $(trendingPosts.id).data('url');
    sendPost(trendingPosts.url, trendingPosts.id, { 'top_n': trendingPosts.top_n });

    const popTagsEle = { id: '#popular-tags', top_n: 5 };
    popTagsEle.url = $(popTagsEle.id).data('url');
    sendPost(popTagsEle.url, popTagsEle.id, { 'top_n': popTagsEle.top_n });

    const popCategoriesEle = { id: '#popular-categories', top_n: 3 };
    popCategoriesEle.url = $(popCategoriesEle.id).data('url');
    sendPost(popCategoriesEle.url, popCategoriesEle.id, { 'top_n': popCategoriesEle.top_n });
}

function sendPost(url, responseEle, data) {
    $.post(url, { data: JSON.stringify(data), 'csrfmiddlewaretoken': window.CSRF_TOKEN }, function(response) {
        $(responseEle).append(response);
    });
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
    //move view more button to the bottom for home pages
    const viewbutton = $('.view-more');
    viewbutton.each(function() { $(this).parent().next().after($(this)) });

    // load the accessibility menu
    const pos = '8';
    loadAccessibityMenu(pos);
}

/**
 * 
 * @param {event} event - The event that takes place 
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

/**
 * Reduces the margin-top for the first class of heading.
 */
function marginFirstHeading() {
    try {
        const ele = $('.heading')[0]
        ele.style.setProperty('margin-top', 0.1 + 'rem', 'important');
    } catch (TypeError) {
        return;
    }
}
/**
 * Load the accessibility menu with the avatar at a specific position
 * @param {string} pos - The position for the accessibility avatar
 */
function loadAccessibityMenu(pos = '1') {
    window._userway_config = {
        /* uncomment the following line to override default position*/
        position: pos,
        /* uncomment the following line to override default size (values: small, large)*/
        /* size: 'small', */
        /* uncomment the following line to override default language (e.g., fr, de, es, he, nl, etc.)*/
        /* language: 'null', */
        /* uncomment the following line to override color set via widget (e.g., #053f67)*/
        /* color: '#1b1b1b', */
        /* uncomment the following line to override type set via widget (1=person, 2=chair, 3=eye, 4=text)*/
        /* type: '1', */
        /* uncomment the following lines to override the accessibility statement*/
        /* statement_text: "Our Accessibility Statement", */
        /* statement_url: "hackadda.com/accessibility", */
        /* uncomment the following line to override support on mobile devices*/
        // mobile: true,
        account: 'xj0VXatzMz'
    };
    $.getScript("https://cdn.userway.org/widget.js");
}