import { flashMsg, RequestCall, loader } from './settings.js';

// function takes users Quiz answers and sends to server
$(document).ready(function() {
    let btn = $('#quiz-btn');
    $(btn).click(function() {
        let requestsent = false
        if (requestsent) {
            return;
        }
    loader(btn);
    let answers = {};
    let data = {};
    let dataID = $('.data_id').text().trim().split(' ').pop();

    $('.input-group input[type="text"]').each(function() {
         let answer = $(this).val().trim();
         let question = $(this).closest('.qanda').find('.question p').text().trim();
         if (answer.split(/\s+/).length <= 250) {
             if (answers.hasOwnProperty(question)) {
                answers[question].push(answer);
                 } else {
          answers[question] = [answer];
          data[dataID] = answers
        }
      }
       });

    let url = 'http://127.0.0.1:5001/api/v1/quiz';
    let text = 'success';
    RequestCall('POST', url, data, btn, text, function(response) {
        flashMsg('You have successfully completed the quiz.', 'success');
    });
    }); 
});

/*
$(Document).ready(function() {
    $('#view-correction').click(function() {
        $.ajax({
            type: 'GET',
            url: 'http://127.0.0.1.5001/api/v1/quiz',
            contentType: 'application/json',
            dataType: 'json',
            success: function(data) {
                console.log(data)
                $.each(data, function(key, value) {
                    if (key === "True" || key === "False") {
                        $.each(value, function(q, a) {
                            var answer = $('input[name="' + q + '"]');
                            if (answer.val() === a) {
                                answer.after('<span class="correct">✔</span>');
                                } else {
                                    answer.after('<span class="incorrect">✘</span>');
                                }
                        });
                            }
                });
            },
            error: function(xhr, textstatus, errorThrown) {
                console.log('Error', errorThrown)
            }
        });
    });
});
*/

$(document).ready(function() {
    let auto = $('#status').data('my-var');
    let topicValue = '';
    if (auto === 'True') {
        $("#datatablesSimple tbody tr").each(function() {
      // Check if date matches current date
            let currentDate = new Date().toISOString().slice(0,10);

            let dateValue = $(this).closest("tr").find("td:nth-child(3)").text();
        if (dateValue === currentDate) {
        // Get topic from table row
             topicValue = $(this).closest("tr").find("td:nth-child(5)").text();

        }
        });
        
    }
     $('#article-link').click(function() {
         let url = 'http://127.0.0.1:5001/api/v1/articles';
         let postData = { 'topic': topicValue };
         RequestCall('POST', url, postData, function(response) {
             cosole.log(response)
            });

     });
});

$(document).ready(function() {
			$('#book-btn').on('click', function() {
				$(this).siblings('iframe').toggle();
			});
		});
