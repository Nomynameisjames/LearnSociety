import { flashMsg } from './settings.js';
import { displayFriendRequests } from './scripts.js';
// file implements all socketio connection logic

export function scrollToBottom() {
  var chatContainer = $('#friends-chat-container');
  chatContainer.scrollTop(chatContainer.prop('scrollHeight'));
}

export function appendMessage(response, recipient_id, current_user, element) {
    //let current_user = $("#hidden-id").text();
    let message = response.text;
    let filtered = message.replace(/</g, "&lt;").replace(/>/g, "&gt;");

    if (response.sender_id !== current_user || !recipient_id) {
        $(element).append(`<div class="sent mb-3">
            <div class="d-flex justify-content-between">
                <p class="small mb-1" style="color: #fff;">${response.name}</p>
            </div>
            <div class="d-flex flex-row justify-content-start mb-3 pt-1">
                <img id="friend-img" src="${response.profile_pic}" alt="avatar 1">
                <div>
                    <p class="small p-2 ms-3 mb-3 rounded-3 bg-success round" style="color: #fff;">${filtered}</p>
                </div>
            </div>
            <div class="d-flex justify-content-start">
                <p class="small mb-1 " id="time-display">${response.time}</p>
            </div>
        </div>`);
    } else {
        $(element).append(`<div class="recieved mb-3">
            <div class="d-flex justify-content-end">
                <p class="small mb-1" style="color: #fff;">${response.name}</p>
            </div>
            <div class="d-flex flex-row justify-content-end mb-3 pt-1">
                <div>
                    <p class="small p-2 me-3 mb-3 text-white rounded-3 bg-primary round">${filtered}</p>
                </div>
                <img id="friend-img" src="${response.profile_pic}" alt="avatar 1">
            </div>
            <div class="d-flex justify-content-end">
                <p class="small mb-1" id="time-display">${response.time}</p>
            </div>
        </div>`);
    }
    scrollToBottom();
}

$(document).ready(function() {
    var socketio = io.connect();

    socketio.on('connected', function(response) {
        socketio.send('I\'m connected!');
        $("#online-status").removeClass("bg-primary").addClass("bg-success").text(response.data);
     //   console.log(`Connected to server: ${response.data}`);
    });

    $("#send-RoomCode-btn").on("click", function() {
        let code = $("#room-code").val().trim();
        if (code === "") {
            return;
        }
        socketio.emit('join', code);
        $("#room-code").val("");
    });

    socketio.on('JoinRoom', function(response) {
        if ('username' in response) {
            $("#group-notification").text(response.username + " has joined the group");

            flashMsg("Welcome aboard", 'success');
            var url = "http://127.0.0.1:5000/ChatRoom/" + response.id;
            setTimeout(function() {
                window.location.href = url;
            }, 500);
        } else if ('message' in response) {
            // Error message
            console.log('in JoinRoom false');
            var errorMessage = response.message;
            flashMsg(errorMessage, 'fail');
        }
    });

    
    $("#send-groupMsg").on("click", function() {
        var currentUrl = window.location.href;
        var roomId = currentUrl.split("/").pop();
        let msg = $("#groupMsg").val().trim();
        if (msg === "") {
                return;
        }
        let data = {"message": msg, "id": roomId};
        socketio.emit('send_message', data);
        $("#groupMsg").val("");
    });

    socketio.on('MsgFeedBack', function(response) {
        var id = $("#hiddenId").val().trim();
        var sender = response.sender_id;
        let card = ".group-chat-conversation";
        appendMessage(response, sender, id, card);
    });

    $("#exit-group").on("click", function() {
        var roomCode = $("#invite-code").text();
        socketio.emit('leave', roomCode);
    });
    socketio.on('LeaveRoom', function(response) {
        $("#group-notification").css("display", "flex")
                                .css("color", "red")
                                .text(response.username + " has left the room");
        setTimeout(function() {
            location.reload();
        }, 500);

    });
});


/*
 * private socket feature to enable the user to chat with other users
 * creating a namespace for private chat
 */
$(document).ready(function() {
    let socketio = io('/private');
    let online_friends = [];
    $('#friends-message-input').focus(function() {
            $(this).css('border', '2px solid blue');
    });
    $('#friends-message-input').blur(function() {
         $(this).css('border', 'none');
    });
    scrollToBottom();

    socketio.on('Private_connection', function(response) {
        socketio.emit('live', response.data);
        if (response.data.length !== online_friends.length) {
                online_friends = response.data;
        }
    });
    console.log(online_friends);
       $("#All-Online, #all-Online").on("click", function() { 
            if (Array.isArray(online_friends) && online_friends.length === 0) {
            $(".friends-search-section").css("display", "none");
            $("#main-friends-section").css("display", "none");
            $(".None-Online").css("display", "flex");
            $(".no-friend").css("background-image", "url('https://ucarecdn.com/ecbe3d12-aca2-4305-bd22-73487120468b/')");
            $(".friends-txt").text("No friends online");
            $("#Add-Friends-btn").css("display", "none");
        } else {
            $(".None-Online").css("display", "none");
            $(".friends-search-section").css("display", "none");
            $("#main-friends-section").empty(); 
            displayFriendRequests(online_friends, false);
        }
    });
    let recipient_id = ""
    $("#button-addon3").on("click", function() {
        let currentURL = window.location.href;
         recipient_id = currentURL.substring(currentURL.lastIndexOf('/') + 1);
        let message = $("#friends-message-input").val();
        socketio.emit('Private_message', {"message": message, "recipient_id": recipient_id});
        $("#friends-message-input").val("");
    });

    socketio.on('Private_message', function(response) {
        let card = ".main-chat-section";
        let current_user = $("#hidden-id").text()
        appendMessage(response, recipient_id, current_user, card);
    });
});

