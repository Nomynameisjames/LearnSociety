let xhr;
let url = 'http://127.0.0.1:5001/api/v1/settings/'

// export function that triggers a flash message on the screen
export const flashMsg = function(msg, type) {
    let message = $("<div>");
    message.addClass("flash-message " + type);
    message.text(msg);
    $("body").append(message);
    setTimeout(function() {
        message.hide();
    }, 7000);
}

// export function that triggers a load button spinner on the screen
export const loader = function(btn) {
		  $(btn).html(
              '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Loading...'
     );
}


// export function that makes an ajax call to the server
export const RequestCall = function(type, url, data, btn, text, callback) {
     $.ajax({
        url: url,
        type: type,
        headers: {
            "Content-Type": "application/json",
        },
        data: JSON.stringify(data),
        beforeSend: function(xhr) {
            xhr.setRequestHeader('x-access-token', getCookie('access_token'));
        },
        success: function(response) {
                callback(response);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log('Error', textStatus, errorThrown);
            $(btn).html(text).find('span').remove();
            var errorMessage = jqXHR.responseText;
            //var jsonObject = JSON.parse(errorMessage);
            flashMsg(errorMessage + ' ' + errorThrown, 'fail');
        }
    });
}

// export function that gets the value of a cookie
export function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for(let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
 }    

// function updates a user's username via the api endpoint
$(document).ready(function () {
        const exampleModal = $('#exampleModal');
    exampleModal.on('show.bs.modal', function (event) {
            const button = $(event.relatedTarget)
            const recipient = button.data('bs-whatever');
            const modalBodyInput = exampleModal.find('#recipient-name');
            modalBodyInput.val(recipient);
        })
        $('#bi-modal').on('click', function() {
            exampleModal.modal('toggle');
            const recipientVal = exampleModal.find('#recipient-name').val();
            const key = exampleModal.find('#recipient-password').val();
            const data = {
                'Key': key,
                'Value': recipientVal,
                'option': 'username'
            };
            RequestCall('PUT', url, data, null, null, function(response) {
                location.reload();
            });
      });
    })

// function updates a user's email via the api endpoint 
$(document).ready(function () {
    let opt;
    $("#mail-reset").click(function() {
        opt =  $(this).val();
    });
    // function updates a user's email via the api endpoint sends a verification code to the user's email
    $('#send-confirm').on('click', function() {
        let btn = "#send-confirm";
        loader(btn);
        let text = "Send verification code"
        xhr = RequestCall('POST', url, {'option': 'email'}, btn, text, function(response) {
            $("#send-confirm").html(text).find('span').remove();
            $('#exampleModalToggle2').modal('show');
        });

    });
    // function updates a user's email via the api endpoint verifies confirmation code sent to the user's email
    $('#send-verifyCode').click(function() {
        const data = {}
        var code = $('#verify-code').val();
        data['code'] = code;
        data['option'] = 'confirmation';
        let btn = "#send-verifyCode";
        loader(btn);
        let text = "Next"
        RequestCall('POST', url, data, btn, text, function(response) {
            $(btn).html(text).find('span').remove();
            if (opt === 'email-reset') {
                $('#exampleModalToggle3').modal('show');
            } else {
                $('#exampleModalToggle4').modal('show');
            }
        });
        
    });
    // function updates a user's email via the api endpoint updates the user's email
        $('#send-verifyEmail').click(function() {
            const data = {}
            var email = $('#email-reset').val();
            var passkey = $('#password-reset').val();
            data['email'] = email;
            data['passkey'] = passkey;
            data['option'] = 'emailreset';
            let btn = "#send-verifyEmail";
            loader(btn);
            let text = "Sent"

            RequestCall('PUT', url, data, btn, text, function(response) {
                $("#send-verifyEmail").html(text).find('span').remove();
                flashMsg("Email Reset", "success");
                location.reload();
            });

        });
    // deletes a user's account via the api endpoint
    $('#account-removal').click(function() {
        const data = {}
        data['confirmDelete'] = true;
        data['option'] = 'deleteAccount';

        RequestCall('DELETE', url, data, null, null, function(response) {
            flashMsg(response.message, "success");
            window.location.replace('/login');
        });
    });

});

// function cancels an ajax request if the cancel button is clicked
$("#cancel-btn").click(function() {
  // Check if xhr object exists and is not in a completed state
  if (xhr && xhr.readyState !== 4) {
    // Abort the Ajax request and update button text
    xhr.abort();
  }
});


// function updates a user's phone number via the api endpoint
$(document).ready(function () {
    $("#Mycontact").click(function() {
        let data = {}
        let btn = "Mycontact"
        loader(btn);
        let phone_number = $('#phone-number').val();
        data['phone_number'] = phone_number;
        data['option'] = 'contact';
        let btn2 = "#phone-contact";
        xhr = RequestCall('PUT', url, data, btn2, null, function(response) {
            $(btn2).find('span').remove();
            flashMsg(response.message, 'success');
            location.reload();
        });
    }); 
});


// function updates a user's password via the api endpoint
$(document).ready(function() {
  $('#reset-form').submit(function(event) {
    event.preventDefault();
   // var form_data = $(this).serialize();
     // console.log(form_data)
      var data = {
          "old_password": $('#old-pass').val(),
          "new_password": $('#new-pass').val(),
          "confirm_password": $('#new-passC').val(),
          "option": "password"
        }

    $.ajax({
      type: "PUT",
      url: url,
        headers: {
            "Content-Type": "application/json",
        }, 
      data: JSON.stringify(data),
        beforeSend: function(xhr) {
            xhr.setRequestHeader('x-access-token', getCookie('access_token'));
        },
        success: function(response) {
            var status = response.status;
            var message = response.message
        if (status == "success") {
          // Display success message
            location.reload();
            flashMsg(message, 'success');
        } else {
          // Display error message
          $(".modal-body").prepend(
            '<div class="alert alert-danger" role="alert">' +
              message +
              "</div>"
          );
        }
          setTimeout(function() {
            $(".alert").remove();
          }, 1000);
      },
      error: function(xhr, status, error) {
          console.log("Error: " + error);
      }
    });
  });
});

// function clears a user's chat history via the api endpoint
$(document).ready(function() {
    $('#clear-chatHistory').click(function() {
        var id = $('#usr-id').val();
        RequestCall('DELETE', url, {'option': 'chatHistory', 'id': id}, null,
            null, function(response) {
            flashMsg(response.message, 'success');
        });
    });
});

// function disables a users converssation save history via the api endpoint
$(document).ready(function() {
    var checkBox = $('#flexSwitchCheckReverse').val()
      if (checkBox === 'False') {
         $('#flexSwitchCheckReverse').attr('checked', false);
      }
        if (checkBox === 'True'){
              $('#flexSwitchCheckReverse').attr('checked', true);
        }
$('#flexSwitchCheckReverse').change(function() {
         var isChecked = $(this).is(':checked');
        var data = {
            'isChecked': isChecked,
            'option': 'checkBox'
        }
        if (isChecked) {
            isChecked = 'true';
        } else {
            isChecked = 'false';
        }
        
        RequestCall('POST', url, data, null, null, function(response) {
            flashMsg(response.message, 'success');
        });
    });
 
 });

// function deletes a user's automated courses via the api endpoint
$(document).ready(function() {
  $('#delete-course').click(function() {
    var course = $('input[name="listGroupRadio"]:checked').val();
    let data = {
        'course': course,
        'option': 'deleteCourse'
    }
      RequestCall('DELETE', url, data, null, null, function(response) {
            flashMsg(response.message, 'success');
        });
});
});

// function that updates a user's learning pace via the api endpoint
$(document).ready(function() {
    var course;
     var tempo = 0;
     $("#decrease-btn").click(function() {
         tempo--;
         $('#Icon-btn').css('color', '#29990a');
         $("#learning-pace").text(tempo + " Days");
         if (tempo < 0) {
             tempo=0
             $('#icon-btn').css('color', 'red');
            $("#learning-pace").text(tempo + " Days");
         }
     });
     $("#increase-btn").click(function() {
         tempo++;
         $('#icon-btn').css('color', '#29990a');
         $("#learning-pace").text(tempo + " Days");
         if (tempo >= 7) {
             tempo=7
             $('#Icon-btn').css('color', 'red');
            $("#learning-pace").text(tempo + " Days");
         }
     });

    $(".dropdown-item").click(function() {

            course = $(this).text();
    });
    $('#save-pace').click(function() {
        data = {
            "course": course,
            "tempo" : tempo,
            "option": "course_tempo"
        }
        if (tempo !== 0 && course !== ' '){
            RequestCall('PUT', url, data, null, null, function(response) {
            flashMsg(response.message, 'success');
        });
        }
        else {
            console.log('date can\'t be zero')
        };
    });
});

// function that activates the search bar and displays the search results 
$(document).ready(function() {
    let RandomSearchBtn = "#btnNavbarSearch";
    let RandomSearchCourseBtn = ".CourseSearch";
    let hiddenBtn = ".hidden-search-send";
    let btnClicked = ''
    let data;
    var Topic;
    var url;
    $(RandomSearchBtn + ', ' + RandomSearchCourseBtn + ', ' + hiddenBtn).click(function(event) {
        event.preventDefault();
        Topic = $(this).val();
        let text = $('.search-bar').val();
        if ($(this).is(RandomSearchBtn) || $(this).is(hiddenBtn)) {
            url = 'http://127.0.0.1:5001/api/v1/search';
            btnClicked = 'RandomSearchBtn'
        } else {
            url = 'http://127.0.0.1:5001/api/v1/search/' + Topic;
        }
        data = {
            'text': text,
            'option': 'search'
        }
    
        if (text.length < 3) {
            return;
        }
        if (btnClicked !== 'RandomSearchBtn') {
            RequestCall('POST', url, data, null, null, function(response) {
                $("#staticBackdrop8").modal('show');
                let lastElement = '';
                var file = response.Document;
                $.each(file, function(index, item) {
                    $("#staticBackdropLabel8").append('Search result for..', item['title']);
                    $.each(item['content'], function(index, content_item) {
                        if (content_item['type'] == 'heading') {
                            lastElement = 'h2';
                            $('<h2>').appendTo('.modal-body').append(content_item['text']);
                        } else if (content_item['type'] == 'paragraph') {
                            if (lastElement == 'code') {
                                $('.modal-body').append($('<p>').text(content_item['text']));
                            } else {
                                lastElement = 'p';
                                $('.modal-body').append($('<p>').text(content_item['text']));
                            }
                        } else if (content_item['type'] == 'code') {
                            lastElement = 'code';
                            $('.modal-body').append($('<code>').text(content_item['text']));
                        }
                    });
                });
            });
        } else {
            RequestCall('POST', url, data, null, null, function(response) {
                $("#staticBackdrop8").modal('show');
                var file = response;
                $("#staticBackdropLabel8").append('Search result for..', text);
                $('.modal-body').append($('<p>').text(file));
                });
            }
    });
});

$(document).ready(function() {
    let room_id = $("#hiddenId").val();
    let room_code = $("#invite-code").text();
    let addr = 'http://127.0.0.1:5001/api/v1/community/';
    $('#clear-group-history').click(function() {
        if (room_id === '' || room_code === '') {
            return;
        }
        console.log(`${room_id} ${room_code}`);
        let data = {
            'room_id': room_id,
            'room_code': room_code,
        }
        RequestCall('DELETE', addr, data, null, null, function(response) {
            flashMsg(response.message, 'success');
        }
        );
    });

    $('#edit-group-info').click(function() {
        if (room_id === '' || room_code === '') {
            return;
        }
        let description = $('#message-text').val();
        let new_name = $('#group-name').val();
        let data = {
            'room_id': room_id,
            'room_code': room_code,
            'description': description,
            'new_name': new_name
        }
        RequestCall('PUT', addr, data, null, null, function(response) {
            flashMsg(response.message, 'success');
        }
        );
    });   
});
