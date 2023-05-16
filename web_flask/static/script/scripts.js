
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

$(document).ready(function() {
    console.log("ready!");
});

function getCookie(cname) {
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

$(document).ready(function() {
$('#my-btn').click(function() {
    var id = prompt("Enter item ID:");
    if (id != null && id.trim() != '') {
      $.ajax({
        url: 'http://127.0.0.1:5001/api/v1/tasks/' + id,
        type: 'DELETE',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('x-access-token', getCookie('access_token'));
        },  
        success: function(data) {
           console.log(data);
            // Code to save the new table data and display success message
           // Code to save the table data goes here
 
           // Display a success message
           var message = $("<div>");
           message.addClass("flash-message success");
           message.text("data Deleted successfully!");
           $("body").append(message);
 
           // Automatically hide the message after a few seconds
            setTimeout(function() {
            message.hide();
           }, 7000);
         },
        error: function(xhr, Status, error) {
           console.log('Error', Status, error);
           var message = $("<div>");
           message.addClass("flash-message fail");
           message.text("error occured while Deleting data!" + ' ' + error);
           $("body").append(message);
           // Automatically hide the message after a few seconds
             setTimeout(function() {
             message.hide();
             }, 7000);
         }
        });
    }
});
});

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

        // make call to api using the Ajax method 
        $.ajax({
          url: 'http://127.0.0.1:5001/api/v1/tasks/' + rowId.trim(),
          type: "PUT",
          data: JSON.stringify(postData),
            contentType: "application/json",
            beforeSend: function(xhr) {
                xhr.setRequestHeader('x-access-token', getCookie('access_token'));
            },
            success: function(response) {
            // send flash message upon success
              var message = $("<div>");
             message.addClass("flash-message success");
             message.text("data Updated successfully!");
             $("body").append(message);
  
             // Automatically hide the message after a few seconds
              setTimeout(function() {
              message.hide();
             }, 7000);
            },
            error: function(error) {
              var message = $("<div>");
             message.addClass("flash-message fail");
             message.text("some error occured while updating Data!", +' '+ error);
             $("body").append(message);
  
             // Automatically hide the message after a few seconds
              setTimeout(function() {
              message.hide();
             }, 7000);
            }
          });
         $('.send-btn').remove();
          //location.reload()
        });
      });
    });
  });
