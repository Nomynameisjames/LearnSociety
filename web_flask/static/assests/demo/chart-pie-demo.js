// Set new default font family and font color to mimic Bootstrap's default styling
   const courses = []; // array to store course names
   const courseCounts = {}; // object to store course counts
   const coursePercentages = {};
   const avg = [];
   // object to store course percentages
   
   const tableRows = document.querySelectorAll("tbody tr"); // get all table rows
   
   tableRows.forEach((row) => {
    const courseName = row.children[3].textContent.trim(); // get course name from 4th cell
  
    if (!courses.includes(courseName)) { // add new course name to array
      courses.push(courseName);
    }
  
    if (courseCounts[courseName]) { // increment course count
      courseCounts[courseName]++;
    } else {
      courseCounts[courseName] = 1;
    }
  });
  
  // calculate percentages
   const totalCount = tableRows.length;
   courses.forEach((course) => {
    const count = courseCounts[course];
    const percentage = (count / totalCount) * 100;
    coursePercentages[course] = parseFloat(percentage.toFixed(1));
  });
  
  for (const key in coursePercentages) {
    avg.push(coursePercentages[key]);
  } 
// Pie Chart Example
var ctx = document.getElementById("myPieChart");
var myPieChart = new Chart(ctx, {
  type: 'pie',
  data: {
      labels: courses,
    datasets: [{
        data: avg,
      backgroundColor: ['#007bff', '#dc3545', '#ffc107', '#28a745',  '#FFA500',
                        '#800080', '#964B00', '#FF0000', '#FF00FF', '#FFD700', 
                        '#FF8C00', '#FF6347', '#FF4500', '#FF1493', '#FF00FF',
                        '#FFC0CB', '#FFD700', '#FF00FF', '#FF1493', '#FF4500',
                        '#FF4500', '#FF6347', '#FF8C00', '#FFA500', '#FFC0CB',
                        '#FFC0CB', '#FFD700', '#FF00FF', '#FF1493', '#FF4500',
                        '#FF4500', '#FF6347', '#FF8C00', '#FFA500', '#FFC0CB',
                        '#FFC0CB', '#FFD700', '#FF00FF', '#FF1493', '#FF4500',
                        '#FF4500', '#FF6347', '#FF8C00', '#FFA500', '#FFC0CB',
                        '#FFC0CB', '#FFD700', '#FF00FF', '#FF1493', '#FF4500', 
                        '#FF6347', '#FF8'],
    }],

  },
});

