
// file implements all socketio connection logic

$(document).ready(function() {
    const socketio = io();

    socketio.on('connected', function(response) {
        socketio.send('I\'m connected!');
        console.log(`Connected to server: ${response.data}`);
    });

    $("#send-RoomCode-btn").on("click", function() {
        let code = $("#room-code").val().trim();
        socketio.emit('join', code);
        $("#room-code").val("");
        console.log('sent');
    });

    socketio.on('JoinRoom', function(data) {
        console.log(data);
    });

    socketio.connect();
});

