import Swiper from 'https://cdn.jsdelivr.net/npm/swiper@10/swiper-bundle.min.mjs'
import { flashMsg, RequestCall } from './settings.js';

window.addEventListener('DOMContentLoaded', event => {

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        // Uncomment Below to persist sidebar toggle between refreshes
        // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
        //     document.body.classList.toggle('sb-sidenav-toggled');
        // }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }
});

// function deletes a users Schedule from the database via the API endpoint
$(document).ready(function() {
$('#my-btn').click(function() {
    var id = prompt("Enter item ID:");
    let url = 'http://127.0.0.1:5001/api/v1/tasks/' + id;
    if (id != null && id.trim() != '') {
      RequestCall('DELETE', url, null, null, null, function(data) {
        console.log(data);
        flashMsg('data Deleted successfully!', 'success');
        });
    }
});
});

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
            console.log(data);
            flashMsg('data Updated successfully!', 'success');
        });
         $('.send-btn').remove();
          //location.reload()
        });
      });
    });
  });

/*$(document).ready(function() {
   var url = 'http://127.0.0.1:5001/api/v1/community/';
    $("#create-groupchat").click(function() {
        let room = $('#new-community-name').val();
        console.log(room);
        let desc = $('#new-community-desc').val();
        console.log(desc);
        var data = {
            'room': room,
            'description': desc
            };
        RequestCall('POST', url, data, null, null, function(data) {
            console.log(data);
            flashMsg(data.message, 'success');
        });
    });
});

$(document).ready(function() {
  $("#create-groupchat").click(function(e) {
    e.preventDefault();

    var formData = new FormData();
    var fileInput = $("#fileInput")[0];
    var file = fileInput.files[0];
    formData.append("image", file);

    let room = $('#new-community-name').val();
    let desc = $('#new-community-desc').val();

    var data = {
      'room': room,
      'description': desc
    };

    // Add the data to the FormData object
    for (var key in data) {
      formData.append(key, data[key]);
    }

    var url = 'http://127.0.0.1:5001/api/v1/testing/';
    RequestCall('POST', url, formData, null, null, function(data) {
        console.log(data);
        flashMsg(data.message, 'success');
    });
    });
});*/


$(document).ready(function() {
  // Get the buttons that trigger the modal
  var buttons = $('.btn-trigger-modal');

  // Handle button click event
  buttons.on('click', function() {
    // Get the data for the clicked button
    var pdfUrl = $(this).data('pdf-url');
    var pdfredirect = $(this).data('pdf-redirect');
    var pdfTitle = $(this).data('pdf-title');

    // Set the modal content dynamically
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
    console.log('I have been clicked');
    
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
