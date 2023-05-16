window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki

    const datatablesSimple = document.getElementById('datatablesSimple');
    if (datatablesSimple) {
        new simpleDatatables.DataTable(datatablesSimple);
    }
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
    const reminderButton = $(".send-btn");
    $('.set-alarm').click(function() {
        if ($("#datatablesSimple tbody tr").find("input[name='row-radio']").length > 0) {
            return;
        }

        $("#datatablesSimple tbody tr").each(function() {
            var currentDate = new Date().toISOString().slice(0,10);
            var dateValue = $(this).closest("tr").find("td:nth-child(3)").text();
	    if (new Date(Date.parse(dateValue)) >= new Date(currentDate) || new Date(Date.parse(dateValue)).toLocaleDateString() === new Date().toLocaleDateString()){
                var radioButton = $("<input type='radio' name='row-radio' class='form-check-input mt-0'>");
                $(this).closest("tr").find("td:first-child").prepend(radioButton);
            }
        });

        $("input[name='row-radio']").click(function() {
            $('.datatable-bottom').append("<td><button class='send-btn'>Set Reminder</button></td>");
            var dateValue = $(this).closest("tr").find("td:nth-child(3)").text();
            var timeValue = $(this).closest("tr").find("td:nth-child(8)").text();
            var topicValue = $(this).closest("tr").find("td:nth-child(5)").text();
            var dateObj = new Date(dateValue + " " + timeValue);
            var reminderDateObj;
            var now;
            $(document).on("click", ".send-btn", function() {
                reminderButton.prop("disabled", true);
                reminderDateObj = dateObj;
                now = new Date();
                var secondsUntilReminder = Math.floor((reminderDateObj.getTime() - now.getTime()) / 1000);
                if (reminderDateObj >= now){

                    console.log("Reminder set for " + secondsUntilReminder + " seconds from now.");
                    var postData = {
                                "text": "Don't forget to study your topic for the day" + topicValue,
                                "Time": timeValue,
                                "Date": dateValue
                                };
                    console.log(postData);
            
                      $.ajax({
                            url: "http://127.0.0.1:5001/api/v1/reminder/",
                            type: "POST",
                            data: JSON.stringify(postData),
                            headers: {    
                                        "Content-Type" : "application/json",
                                    },
                            beforeSend: function(xhr) {
                                xhr.setRequestHeader('x-access-token', getCookie('access_token'));
                        },
                            success: function(response) {
                                    var message = $("<div>");
                                    message.addClass("flash-message success");
                                    message.text("Reminder set for!" + dateObj.toISOString());
                                    $("body").append(message);
 
              // Automatically hide the message after a few seconds
                                    setTimeout(function() {
                                            message.hide();
                                        }, 5000);

                                    },
                                    
                            error: function(error) {
                                var message = $("<div>");
                                message.addClass("flash-message fail");
                                message.text("some error occured while updating Data!");
                                $("body").append(message);
 
                                // Automatically hide the message after a few seconds
                                setTimeout(function() {
                                message.hide();
                                                }, 5000);
                                    }
                    }); 
                } else {
                    alert("Reminder time is not valid.");
                    }
                this.remove();
            });
        });
    });
});


$(document).ready(function() {
        getQuote(); // Call getQuote() function on page load
		setInterval(getQuote, 60000);
        function getQuote() {
				$.ajax({
					url: "https://api.adviceslip.com/advice",
					type: 'GET',
					dataType: 'json',
					success: function(data) {
						$('#get-quote').text(data.slip.advice);
					},
					error: function(jqXHR, textStatus, errorThrown) {
						console.log('Error: ' + textStatus + ' - ' + errorThrown);
					}
				});
        };
	});

$(document).ready(function() {
  $('a.nav-link').click(function() {
    var myID = $(this).attr('href').split("=")[1];
    localStorage.setItem('myID', myID); // store myID value as an environment variable
  });
});

$(document).ready(function() {
    $("#auto-btn").click(function() {
    var day = $("#auto-input").val();
        console.log(day);
    var myID = localStorage.getItem('myID');
     $.ajax({
         type: "POST",
       url: "http://127.0.0.1:5001/api/v1/auto-dash",
       headers: {
           "Content-Type" : "application/json",
                 },
      beforeSend: function(xhr) {
         xhr.setRequestHeader('x-access-token', getCookie('access_token'));
                         },
         data: JSON.stringify({ "Day": day, "Course" : myID}),
       dataType: "json",
       success: function(data) {
           var message = $("<div>");
           message.addClass("flash-message success");
           message.text("Course succesfully added");
           $("body").append(message);
  
               // Automatically hide the message after a few seconds
            setTimeout(function() {
            message.hide();
                    }, 5000);
 
            },
       error: function(xhr, status, error) {
           var message = $("<div>");
           message.addClass("flash-message fail");
           message.text("some error occured while creating Data!");
           $("body").append(message);
           // Automatically hide the message after a few seconds
           setTimeout(function() {
               message.hide();
           }, 5000);

       }
     }); 
   });
});
