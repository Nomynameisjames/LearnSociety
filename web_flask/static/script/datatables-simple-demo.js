import { flashMsg, RequestCall } from './settings.js';

window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki

    const datatablesSimple = document.getElementById('datatablesSimple');
    if (datatablesSimple) {
        new simpleDatatables.DataTable(datatablesSimple);
    }
});

// function that sets reminder for the user by making a POST request to the server
// to trigger the reminder function
$(document).ready(function() {
    const reminderButton = $(".send-btn");
    $('.set-alarm').click(function() {
        if ($("#datatablesSimple tbody tr").find("input[name='row-radio']").length > 0) {
            return;
        }
        // add radio buttons to each row that has a date greater than or equal to today's date
        $("#datatablesSimple tbody tr").each(function() {
            var currentDate = new Date().toISOString().slice(0,10);
            var dateValue = $(this).closest("tr").find("td:nth-child(3)").text();
	    if (new Date(Date.parse(dateValue)) >= new Date(currentDate) || new Date(Date.parse(dateValue)).toLocaleDateString() === new Date().toLocaleDateString()){
                var radioButton = $("<input type='radio' name='row-radio' class='form-check-input mt-0'>");
                $(this).closest("tr").find("td:first-child").prepend(radioButton);
            }
        });
        // add a button to the bottom of the table to set the reminder
        $("input[name='row-radio']").click(function() {
            $('.datatable-bottom').append("<td><button class='send-btn'>Set Reminder</button></td>");
            var dateValue = $(this).closest("tr").find("td:nth-child(3)").text();
            var timeValue = $(this).closest("tr").find("td:nth-child(8)").text();
            var topicValue = $(this).closest("tr").find("td:nth-child(5)").text();
            var dateObj = new Date(dateValue + " " + timeValue);
            var reminderDateObj;
            var now;
            // when the button is clicked, disable the button and set the reminder
            $(document).on("click", ".send-btn", function() {
                reminderButton.prop("disabled", true);
                reminderDateObj = dateObj;
                now = new Date();
                var secondsUntilReminder = Math.floor((reminderDateObj.getTime() - now.getTime()) / 1000);
                // check if the reminder time is valid
                if (reminderDateObj >= now){

                    console.log("Reminder set for " + secondsUntilReminder + " seconds from now.");
                    var postData = {
                                "text": "Don't forget to study your topic for the day" + topicValue,
                                "Time": timeValue,
                                "Date": dateValue
                                };
                    console.log(postData);
                    let url = "http://127.0.0.1:5001/api/v1/reminder/";
                    // make a POST request to the server to trigger the reminder function
                    RequestCall('POST', url, postData, null, null, function(response) {
                        flashMsg("Reminder set for " + dateObj.toISOString(), "success");
                    });
                } else {
                    alert("Reminder time is not valid.");
                    }
                // remove the button after the reminder is set
                this.remove();
            });
        });
    });
});

// function Gets the quote of the day from the API and displays it on the dashboard
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

// function to get the course ID from the URL and store it as an environment variable
$(document).ready(function() {
  $('a.nav-link').click(function() {
    var myID = $(this).attr('href').split("=")[1];
    localStorage.setItem('myID', myID); // store myID value as an environment variable
  });
});

// function to get the course name from the database
$(document).ready(function() {
    $("#auto-btn").click(function() {
    var day = $("#auto-input").val();
        console.log(day);
    var myID = localStorage.getItem('myID');
    let postData = {"Day": day, "Course" : myID};
    let url = "http://127.0.0.1:5001/api/v1/auto-dash";
    RequestCall('POST', url, postData, null, null, function(response) {
        flashMsg("Course succesfully added", "success");
    });
   });
});
