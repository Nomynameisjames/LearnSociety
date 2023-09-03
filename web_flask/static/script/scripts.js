import { Swiper } from 'https://cdn.jsdelivr.net/npm/swiper@10/swiper-bundle.min.mjs'
import { flashMsg, RequestCall, getCookie } from './settings.js';

// global variable keeps track of user request
let request_num = 0;
let No_profile_picture = "https://ucarecdn.com/163efe7c-bcc5-4545-a795-128b261d6a45/";
let unblock = null
/*
 * Function to display the user's friends list on the friends page
 * @param {array} friendsList - list of friends
 * @param {boolean} includeButtons - whether or not to include buttons
 * @return {void}
 */

let friend_card = (modal, Status, value = {}) => {
  if (typeof value !== 'object' || value === null) {
    return;
  }

  if (Status && Status === "blocked") {
    value.Status = "Blocked";
    value.profile_picture = No_profile_picture;
  }

  let friendCard = $("<div>", {
    class: "card mb-3",
    style: "max-width: 540px; background-color: rgba(0,0,0,0);",
    id: "main-chat-interface"
  });

  let rowDiv = $("<div>", {
    class: "row",
    id: "friends-sec",
  });

  // Check if modal is provided
  if (modal) {
    rowDiv.attr("data-bs-toggle", "modal");
    rowDiv.attr("data-bs-target", modal);
  }

  let imgDiv = $("<div>", {
    class: "col-3",
  });

  let img = $("<img>", {
    src: value.profile_picture,
    class: "img-fluid",
    id: "friends-img",
  });

  let colDiv = $("<div>", {
    class: "col p-0",
  });

  let cardBodyDiv = $("<div>", {
    class: "card-body",
      id: "friends-card-body",
  });

  let hiddenField = $("<input>", {
    type: "hidden",
    name: "hiddenField",
    id: "hidden-modal-id",
    value: value.id,
  });

  let cardTitle = $("<h5>", {
    class: "card-title",
    style: "color: #fff; text-shadow: 1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue;",
    text: value.username,
  });

  let cardText = $("<p>", {
    class: "card-text",
    style: "color: #fff;",
    text: value.Status,
  });

  // Append elements to the corresponding parent elements
  cardBodyDiv.append(hiddenField, cardTitle, cardText);
  colDiv.append(cardBodyDiv);
  imgDiv.append(img);
  rowDiv.append(imgDiv, colDiv);
  friendCard.append(rowDiv);

  return friendCard;
};

/*
 * function to display the user's friends list on the friends page
 * @param {array} friendsList - list of friends
 * @param {boolean} includeButtons - whether or not to include buttons
 * status - status of the friend
 * @return {void}
 * if status is blocked, then the friend card will be displayed with the status blocked
 * else if  status is not blocked, then the friend card will be displayed with the status friends
 */
export function displayFriendRequests(friendRequestList, includeButtons, Status) {
    let user_id = null;
    $.each(friendRequestList, function(index, value) {
        $("#main-friends-section").css("display", "flex");

        if (value.profile_picture === "") {
            value.profile_picture = No_profile_picture;
        } 
        if (value.Status === "") {
            value.Status = "No status";
        }
        if (!Status) {
            let modal = "#staticBackdrop10"
            let friendCard = friend_card(modal, Status, value);
            if (includeButtons) {
                friendCard.find("#friends-sec").append(`
                    <div class="gap-2 d-md-flex justify-content-md-end" id="friends-sec-btn">
                        <button class="btn btn-sm me-md-2 decline-request" type="button">
                            <iconify-icon icon="mdi:cancel-bold" width="15" height="15" style="color: red;"></iconify-icon>
                        </button>
                        <button class="btn btn-sm accept-request" type="button">
                            <iconify-icon icon="mdi:check-bold" width="15" height="15" style="color: green;">
                            </iconify-icon>
                        </button>
                    </div>
                `);

                friendCard.find(".decline-request").on("click", function() {
                // Find the associated username within the same parent element
                //let username = $(this).closest(".card").find(".card-title").text().trim();
                // Call the function to handle the "Decline" button click
                let url = 'http://127.0.0.1:5001/api/v1/friends/request/' + value.id;
                RequestCall('DELETE', url, null, null, null, function(data) {
                        flashMsg(data.message, 'success');
                    });
                });
        
                friendCard.find(".accept-request").on("click", function() {
                // Find the associated username within the same parent element
                //let username = $(this).closest(".card").find(".card-title").text().trim();
                // Call the function to handle the "Accept" button click
                let url = 'http://127.0.0.1:5001/api/v1/friends/request/' + value.id;
                RequestCall('PUT', url, null, null, null, function(data) {
                        flashMsg(data.message, 'success');
                    });
                });
            }
            $(friendCard).on("click", function() {
                // Find the associated username within the same parent element
                $(".friends-modal-dp img").attr("src", value.profile_picture);
                $(".modal-username").text(value.username);
                $(".modal-status").text(value.Status);
                $(".modal-joined").text(value.Created);
                $(".modal-active-courses").empty();
                $(".modal-communities").empty();
                unblock = value.id;
                if (value.Active_courses.length == 0) {
                    $(".modal-active-courses").append(`
                        <li>None</li>
                    `);
                } else {
                    $.each(value.Active_courses, function(key, val) {
                        $(".modal-active-courses").append(`
                            <li>${val}</li>
                        `);
                    });
                }
                if (value.Communities.length == 0) {
                    $(".modal-communities").append(`
                        <li>None</li>
                    `);
                } else {
                    $.each(value.Communities, function(key, val) {
                        $(".modal-communities").append(`
                            <li>${val}</li>
                        `);
                    });
                }
            });
            $("#main-friends-section").append(friendCard);
        }
        else {
            let friendCard = friend_card(null, Status, value);
            if (includeButtons) {
                friendCard.find("#friends-sec").append(`
                    <div class="gap-2 justify-content-md-start" id="friends-sec-btn">
                        <button class="btn unblock-btn" type="button" data-bs-toggle="tooltip" data-bs-placement="top" data-bs-title="Unblock">
                            <iconify-icon icon="fluent-mdl2:block-contact" id="unblock" height="20" width="20"></iconify-icon>
                        </button>
                    </div>
                `);
                friendCard.find(".unblock-btn").on("click", function() {
                    // Find the associated username within the same parent element
                    let option = "unblock";
                    user_id = value.id;
                    let url = 'http://127.0.0.1:5001/api/v1/friends/' + option;
                    let payload = {"user_id": user_id};
                    RequestCall('PUT', url, payload, null, null, function(data) {
                        flashMsg(data.message, 'success');
                    });
                });
            }
            $("#main-friends-section").append(friendCard);
        }
    });
     $('[data-bs-toggle="tooltip"]').each(function() {
        new bootstrap.Tooltip(this);
    });
}

/*
 * toggles the side navigation bar on and off
 * @param {void}
 * @return {void}
 * @source https://startbootstrap.com/docs/javascript/scrollspy/#via-javascript
 */
window.addEventListener('DOMContentLoaded', event => {

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }
     //friendNav.style.width = defaultFriendNavWidth;
});

// function deletes a users Schedule from the database via the API endpoint
$(document).ready(function() {
    $('#my-btn').click(function() {
        var id = prompt("Enter item ID:");
        let url = 'http://127.0.0.1:5001/api/v1/tasks/' + id;
        if (id != null && id.trim() != '') {
            RequestCall('DELETE', url, null, null, null, function(data) {
                flashMsg('data Deleted successfully!', 'success');
            });
        }
    });
});

/*
 * funtion to toggle the swiper.js cards
 * @param {void}
 * @return {void}
 * @source https://swiperjs.com/swiper-api
 */
$(document).ready(function() {
     var swiper = new Swiper(".mySwiper", {
      slidesPerView: 3,
      spaceBetween: 30,
      freeMode: true,
      pagination: {
        el: ".swiper-pagination",
        clickable: true,
        renderBullet: function (index, className) {
          return '<span class="' + className + '">' + (index + 1) + "</span>";
        },
      },
        breakpoints: {
        360: {
            slidesPerView: 1.2,
            spaceBetween: 15,
        },
        640: {
          slidesPerView: 2.3,
          spaceBetween: 25,
        },
        768: {
          slidesPerView: 2.3,
          spaceBetween: 25,
        },
        1024: {
          slidesPerView: 3.3,
          spaceBetween: 30,
        },
      },
    });
});


// function aUpdates a users Schedule in the database via the API endpoint
$(document).ready(function() {
  // Add event listener to update button
  var topicValue, courseValue, reminderValue;

  $(".edit-btn").click(function() {
    // Get table rows and loop through them to add radio buttons
    if ($("#datatablesSimple tbody tr").find("input[name='row-radio']").length > 0) {
      return;
    }

    $("#datatablesSimple tbody tr").each(function() {
      var rowId = $(this).find("td:eq(1)").text();
      var radioButton = $("<input  class='form-check-input mt-0' type='radio' name='row-radio'>");
      radioButton.val(rowId);
      $(this).find("td:first").prepend(radioButton);
    });
    // Add event listener to radio buttons
    $("input[name='row-radio']").click(function() {
      // Remove any existing text areas

    $('.datatable-bottom').append("<td><button class='send-btn'>Save</button></td>");	
    var rowId = $(this).val();
    var columnIndex = $(this).closest("td:eq(1)").index();
    var textAreaExists = $("tr[data-id='" + rowId + "'] td:nth-child(" + (columnIndex + 1) + ") textarea").length > 0;

      $("textarea").each(function() {
        var currentValue = $(this).val();
        $(this).closest("td").html(currentValue);
      });
    if (!textAreaExists) {
        $("textarea").remove();
        //$(".send-btn").remove();
    } else {
        $("tr[data-id='" + rowId + "'] td:nth-child(" + (columnIndex + 1) + ") textarea").remove();
  }

      // If a radio button is selected, create a textarea in the corresponding row
      $(this)
        .closest("tr")
        .find("td:not(:lt(2))")
        .each(function(index) {
          if (!$(this).hasClass("Dont")) {
            var currentValue = $(this).text();
            $(this).html("<textarea class='update-text form-control'>" + currentValue + "</textarea>");
          }
        });
    
      // Add event listener to send button
      $(document).on("click", ".send-btn", function() {
        var rows = $('#datatablesSimple tbody tr');
        rows.each(function() {
          var $thisRow = $(this);

          // Get the value of the textarea in the each column
          if ($thisRow.find('td:nth-child(5) textarea').length > 0) {
            topicValue = $(this).find("td:nth-child(5) textarea").val();
          }

          if ($thisRow.find('td:nth-child(4) textarea').length > 0) {
            courseValue = $thisRow.find('td:nth-child(4) textarea').val();
          }

          // Get the value of the textarea in the fifth column
            if ($thisRow.find('td:nth-child(8) textarea').length > 0) {
                reminderValue = $(this).find("td:nth-child(8) textarea").val();
            }
        });
      

        var postData = {
          "Topic": topicValue,
          "Course": courseValue,
          "Reminder": reminderValue
        };
        let url = 'http://127.0.0.1:5001/api/v1/tasks/' + rowId.trim();
        // makes call to API endpoint to update data
        RequestCall('PUT', url, postData, null, null, function(data) {
            flashMsg('data Updated successfully!', 'success');
        });
         $('.send-btn').remove();
          //location.reload()
        });
      });
    });
  });

$(document).ready(function() {
  // Get the buttons that trigger the modal
  var buttons = $('.btn-trigger-modal');

  // Handle button click event
  buttons.on('click', function() {
    // Get the data for the clicked button
    var pdfUrl = $(this).data('pdf-url');
    var pdfredirect = $(this).data('pdf-redirect');
    var pdfTitle = $(this).data('pdf-title');

    // Set the modal
    //content dynamically
    $('#pdf-object').attr('src', pdfUrl);
    $('#pdf-download-link').attr('href', pdfredirect);
    $('#staticBackdropLabel').text(pdfTitle);

    // Show the modal
    $('#staticBackdrop').modal('show');
  });
});


$(document).ready(function() {
  // Store the state of the input field
  var isInputVisible = false;

  $('#hidden-search').click(function() {
    
    // Toggle the visibility of the input field
    if (isInputVisible) {
      hideInputField();
    } else {
      showInputField();
    }
    
    // Toggle the state
    isInputVisible = !isInputVisible;
  });

  function showInputField() {
    $('#hidden-search-input')
      .css('transition', 'transform 0.5s ease-in-out')
      //.css('max-width', '100%')
      .css('display', 'flex')
      .css('transform', 'translateX(0)');
    $('#hidden-search-input input[type="search"]').focus();
  }
  
  function hideInputField() {
    $('#hidden-search-input')
      .css('transition', 'transform 0.5s ease-in-out')
      //.css('max-width', '0')
      .css('transform', 'translateX(100%)')
      .css('display', 'none');
    $('#hidden-search-input input[type="search"]').blur();
  }
});

$(document).ready(function() {
    $("#Edit-Status").click(function() {
        let New_Status = $("#status-text").val();
        let data = {
            "status": New_Status,
            "option": "status"
        }
        let url = 'http://127.0.0.1:5001/api/v1/settings';
        RequestCall('PUT', url, data, null, null, function(data) {
            flashMsg('data Updated successfully!', 'success');
        });
    });
});

$(document).ready(function() {
    $("#All-Friends, #all-Friends").click(function() {
        let option = "All";
        let url = 'http://127.0.0.1:5001/api/v1/friends/' + option;

        RequestCall('GET', url, null, null, null, function(data) {
            if (data.message === "you have no friends") {
                $(".friends-search-section").css("display", "none");
                $("#main-friends-section").css("display", "none");
                $(".None-Online").css("display", "flex");
                $(".no-friend").css("background-image", "url('https://ucarecdn.com/8499d7ae-1d47-4aee-a157-fe4beb4e79d5/')");
                $("#Add-Friends-btn").css("display", "block");
                $(".friends-txt").text("You have no friends");

            } else {
                $(".None-Online").css("display", "none");
                $(".friends-search-section").css("display", "none");
                $("#main-friends-section").empty();
                displayFriendRequests(data.message, false)
            }
        });
    });
    $("#All-Pending, #all-Pending").click(function () {
        let option = "Pending";
        let url = "http://127.0.0.1:5001/api/v1/friends/" + option;

        RequestCall("GET", url, null, null, null, function (data) {
            if (data.message === "you have no pending requests") {
                $(".friends-search-section").css("display", "none");
                $("#main-friends-section").css("display", "none");
                $(".None-Online").css("display", "flex");
                $(".no-friend").css("background-image", "url('https://ucarecdn.com/15127733-e9c5-4e82-bdf3-e4b4e982aeb8/')");
                $(".friends-txt").text("You have no pending requests");
                $("#Add-Friends-btn").css("display", "none");
            } else {
                let friend_request = data.message;
                request_num = friend_request.length;
                $("#request_list").text(request_num);
                $(".None-Online").css("display", "none");
                $(".friends-search-section").css("display", "none");
                $("#main-friends-section").empty(); // Clear the existing content before appending new elements

                // Loop through friend_request and update the friend cards
                displayFriendRequests(friend_request, true);
            }
        });
    });
    $("#All-Blocked, #all-Blocked").click(function() {
        let option = "Blocked";
        let url = "http://127.0.0.1:5001/api/v1/friends/" + option;
        RequestCall("GET", url, null, null, null, function (data) {
            if (data.message === "you have no blocked users") {
                $(".friends-search-section").css("display", "none");
                $("#main-friends-section").css("display", "none");
                $(".None-Online").css("display", "flex");
                $(".no-friend").css("background-image", "url('https://ucarecdn.com/cf71c226-172f-45d0-bc68-cdc7b922e8d0/')");
                $(".friends-txt").text("You have no blocked users");
                $("#Add-Friends-btn").css("display", "none");
            } else {
                let blocked_users = data.message;
                $(".None-Online").css("display", "none");
                $(".friends-search-section").css("display", "none");
                $("#main-friends-section").empty(); // Clear the existing content before appending new elements

                // Loop through friend_request and update the friend cards
                displayFriendRequests(blocked_users, true, "blocked");
            }
        });
    });

    $("#Add-Friend, #add-Friends").click(function() {
        $(".friends-search-section").css("display", "flex");
        $(".None-Online").css("display", "none");
        $("#main-friends-section").css("display", "none");
    });

});

$(document).ready(function() {
    $(".find-user").click(function(e) {
        e.preventDefault();
        let username = $(".friends-search").val();
        let url = 'http://127.0.0.1:5001/api/v1/friends/request/' + username;
        $.ajax({
            url: url,
            type: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            beforeSend: function(xhr) {
                xhr.setRequestHeader('x-access-token', getCookie('access_token'));
            },
            success: function(response) {
                $(".friends-search").css("border", "2px solid rbga(0, 255, 0, 0.9)");
                $("#Not-Found").css("display", "block")
                               .css("color", "rgba(0, 255, 0, 0.9)")
                               .text(response.message);
                $(".friends-search").val("");
            },
            error: function(jqXHR, textStatus, errorThrown) {
                    $(".friends-search").css("border", "2px solid rgba(255, 0, 0, 0.9)");
                    $("#Not-Found").css("display", "block").text(jqXHR.responseJSON.message);
          }
      });
    });
        $(".friends-search").focus(function() {
        $(".friends-search").css("border", "2px solid #ccc"); // Reset the border style
        $("#Not-Found").css("display", "none"); // Hide the #Not-Found element
    });
});

$(document).ready(function() {
    // Add a click event handler for each button
    $("#All-Online, #All-Friends, #All-Pending, #All-Blocked, #Add-Friend").click(function() {
        // Reset the color property for all buttons
        $("#friendsNav .nav-link").css("color", "#fff");
        $("#Add-Friend").css("color", "#fff");
        
        // Change the color property for the clicked button to blue
        $(this).css("color", "rgba(0, 255, 0, 0.9)");
    });
});

$(document).ready(function() {
    $("#staticBackdrop10").find("#modal-dropdown-btn").on("click", function() {
        let option = "block";
        //let user_id = $("#hidden-modal-id").first().val();
        if (unblock) {
            let url = 'http://127.0.0.1:5001/api/v1/friends/' + option;
            let payload = {"user_id": unblock};
                RequestCall('PUT', url, payload, null, null, function(data) {
                        flashMsg(data.message, 'success');
            });
        }
        else {
            flashMsg("You can't unblock this user", 'danger');
        }
    });
    //sends a POST request to the user route
    
    $(".open-chat").click(function(e) {
        e.preventDefault();
        let url = "http://127.0.0.1:5000/friends/" + unblock;
        $(this).attr("href", url);
        window.location.href = url;
        /*$.get(url, function(data) {
            $("#main-friends-section").html(data);
        });*/
    });

    $("#clear-privateChat").click(function() {
        let option = "clear";
        let currentURL = window.location.href;
        let friend_id = currentURL.substring(currentURL.lastIndexOf('/') + 1);
        let url = 'http://127.0.0.1:5001/api/v1/friends/' + option;
        let payload = {"friend_id": friend_id};
        RequestCall('DELETE', url, payload, null, null, function(data) {
            flashMsg(data.message, 'success');
        });
    });
});

