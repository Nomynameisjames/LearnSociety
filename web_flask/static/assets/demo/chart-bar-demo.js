const dates = Array.from(document.querySelectorAll('tbody td:nth-child(3)')).map(td => td.textContent.trim());
    
   // Get all the values from the Average column in the table
 const averages = Array.from(document.querySelectorAll('tbody td:nth-child(7)')).map(td => Number(td.textContent.trim()));
   
   
  
   // Bar Chart Example
var ctx = document.getElementById("myBarChart");
var myLineChart = new Chart(ctx, {
    type: 'bar',
    data: {
    labels: dates,
    datasets: [{
        label: "Average",
        backgroundColor: "rgba(2,117,216,1)",
        borderColor: "rgba(2,117,216,1)",
        data: averages,
      }],
    },
    options: {
        scales: {
            xAxes: [{
                time: {
                    unit: 'Dates'
                },
                gridLines: {
                    display: false

                },
                title: {
                    display: true,
                    text: 'Dates'
                },
                ticks: {
                    maxTicksLimit: 25
                }
            }],
            yAxes: [{
                ticks: {
                min: 0,
                max: 100,
                maxTicksLimit: 10
                },
                title: {
                    display: true,
                    text: 'Average'
                },
                gridLines: {
                    display: true
                }
            }],
        },
        legend: {
            display: false
        }
    }
 });

