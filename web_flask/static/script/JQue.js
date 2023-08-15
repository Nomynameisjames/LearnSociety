// loader icon logic 
import { flashMsg, RequestCall, getCookie } from './settings.js';
import { scrollToBottom } from './socketio.js';


// function that animates the chatbot header div 
function ShowBox() {
    $("#nav-id").css("background-color", "black")
                .css("color", "white");

    $("#nav-id").slideUp(2000, function() {
        $("#nav-id").slideDown(5000);
    });
}

// function that toggles the chatbot animated div to show and hide
$(document).ready(function() {
    var textarea = $("#my-chat-input");
    textarea.on("focus", function() {
        // Slide up the nav element
        $("#nav-id").slideUp();
    }).on("blur", function() {
        // Slide down the nav element
        $("#nav-id").slideDown();
    });

    // Attach the click event to the send button
    $("#chat-submit").on("click", function() {
        // Call the ShowBox function
        ShowBox();
    });
});


// function makes a call to the openai api for the chatbot functionality 
$(document).ready(function() {
    scrollToBottom();
 $('#chat-submit').click(function() {
  // Get user value from the input field
    var inputMsg = $("#my-chat-input").val();
    var postData = { "text": inputMsg };
    $("#my-chat-input").val("");
    let username = $("#Hidden-user").val();
    let picture = $("#Picture").val();
    let time = moment().format('Do MMM YYYY h:mm:ssa');
    $("#chat-bot-card").append(`
        <div class="received mb-3" style="margin-left: auto;">
            <div class="d-flex justify-content-end">
                <p class="small mb-1" style="color: #fff;">${username}</p>
            </div>
            <div class="d-flex flex-row justify-content-end mb-2 pt-1">
                <div>
                    <p class="small p-2 me-3 mb-3 text-white rounded-3 bg-primary round">${inputMsg}</p>
                </div>
                <img id="friend-img" src=${picture} alt="avatar 1">
            </div>
            <div class="d-flex justify-content-end">
                <p class="small mb-1" id="time-display">${time}</p>
            </div>
        </div>
    `);
    scrollToBottom();

    let url = 'http://127.0.0.1:5001/api/v1/chatbot/';
    RequestCall('POST', url, postData, null, null, function(response) {
        let outputMsg = response.text;
        let msg = JSON.stringify(outputMsg).replace(/\n|\[|\]/g, '');
        let time = response.time
        let username = "text-davinci-003";
        let profile_pic = response.picture;
         $("#chat-bot-card").append(`<div class="sent mb-3" style="margin-right: auto;">
            <div class="d-flex justify-content-between">
                <p class="small mb-1" style="color: #fff;">${username}</p>
            </div>
            <div class="d-flex flex-row justify-content-start mb-2 pt-1">
                <img id="friend-img" src="${profile_pic}" alt="avatar 1">
                <div>
                    <p class="small p-2 ms-3 mb-3 rounded-3 bg-success round" style="color: #fff;">${msg}</p>
                </div>
            </div>
            <div class="d-flex justify-content-start">
                <p class="small mb-1 " id="time-display">${time}</p>
            </div>
        </div>`);
        $('#nav-id').css('border', '.2em solid #39FF14');
        scrollToBottom();
    });
    });
});


// function makes a call to the RESTFul api to create a new schedule 
$(document).ready(function() {
  $('#add').click(function() {
    var myDay = $('.Day').val();
    var myCourse = $('.Course').val();
    var myTopic = $('.Topic').val();
    var myReminder = $('.Reminder').val();
    if (myDay && myCourse && myTopic && myReminder) {
        var postDate = {
            "Day": myDay,
            "Course": myCourse,
            "Topic": myTopic,
            "Reminder": myReminder
        };
        $('.Day').val('');
        $('.Course').val('');
        $('.Topic').val('');
        $('.Reminder').val('');
        let url = 'http://127.0.0.1:5001/api/v1/tasks/';
        RequestCall('POST', url, postDate, null, null, function(response) {
            console.log(response);
            flashMsg('Table data created successfully!', 'success');
            });
        } else {
            flashMsg('Please fill all fields!', 'fail');
        }
  });
});
