 import { flashMsg } from './settings.js';
// file implements all socketio connection logic

$(document).ready(function() {
    var socketio = io.connect();

    socketio.on('connected', function(response) {
        socketio.send('I\'m connected!');
        console.log(`Connected to server: ${response.data}`);
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
        if ('room' in response && 'username' in response) {
            console.log('in JoinRoom true');
            //var roomId = response.id;
            var message = response.username + ' joined the group';
            $('.joinMessage').text(message);
            flashMsg("Welcome aboard", 'success');
            //window.location.href = 'http://127.0.0.1:5000/ChatRoom/' + roomId;
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
        var msg = response.message;
        var username = response.username;
        var sender = response.id;
        var date = response.date;
        //var msg = JSON.stringify(outputMsg).replace(/\n|\[|\]/g, '');
        if (id === sender) {
            var chatLog = "<div class='sent-group-message d-flex flex-column mb-3'><h6 class='sent-group-chat-username'  style='color: #d6d6d6;'>" + username + "</h6><p class='sent-group'>" + msg + "</p><div class='grp-sent-time'>" + date + "</div></div>";
    $(".group-chat-conversation").append(chatLog);
        } else {
                let RecieveLog = "<div class='replied-group-message  d-flex flex-column mb-3'><h6 class='replied-group-chat-username'  style='color: #d6d6d6;'>" + username + "</h6><p class='received-group-message'>" + msg + "</p><div class='replied-grp-sent-time'>" + date + "</div></div>";
            $(".group-chat-conversation").append(RecieveLog);
        }
        //outputMsg = {};
        console.log('you have a feedback');
        console.log(`user: ${response}`);
    });
});

