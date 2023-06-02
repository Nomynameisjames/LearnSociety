// loader icon logic 
import { flashMsg, RequestCall, getCookie } from './settings.js';

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
    // Get the textarea element
    var textarea = $("#my-chat-input");
    var container = $('.chat-container');
    container.scrollTop(container.prop("scrollHeight"));
    $('#my-chat-input').on('input', function() {
          $(this).css('height', 'auto');
          $(this).css('height', $(this)[0].scrollHeight + 'px');
        });
    // Attach the focus and blur events
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
 $('#chat-submit').click(function() {
  // Get user value from the input field
  var inputMsg = $("#my-chat-input").val();
  var postData = { "text": inputMsg };
  $("#my-chat-input").val("");
  // Make a GET request to get conversation history and append to the chatbot div
      $.ajax({
        url: 'http://127.0.0.1:5001/api/v1/help/',
        type: 'POST',
        headers: {
          "Content-Type": "application/json",
        },
        data: JSON.stringify(postData),
        beforeSend: function(xhr) {
          xhr.setRequestHeader('x-access-token', getCookie('access_token'));
        },
        success: function(response) {
          // upon success get response from request and append response to the chatbot div
          var outputMsg = Object.values(response);
          var msg = JSON.stringify(outputMsg).replace(/\n|\[|\]/g, '');
          $('#nav-id').css('border', '.2em solid #39FF14');
          var chatLog = "<div class='sent-message'><p id='sent'>" + inputMsg + "</p></div><div class='replied-message'><p id='received'>" + msg + "</p></div>";
          $(".chat-conversation").append(chatLog);
          outputMsg = {};
        },
        error: function(jqXHR, textStatus, errorThrown) {
          // upon error log error message and output a flash message on the chatbot div
          console.log('Error', textStatus, errorThrown);
          $('#nav-id').css('border', '.2em solid #FF5349');
          flashMsg("Bot Server down please help report issue!", 'fail');
        }
      })
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
      // Add save button
      $('<button/>', {
        text: 'Save',
        class: 'add',
        click: function() {
          // Save the data and remove the save button
          $(this).fadeOut('fast', function() {
            $(this).remove();
          });
        }
      }).appendTo('#card-header');

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
    }
  });
});
