// Timer to count time since page were loaded

// Nullify vars
var totalSeconds = 0;
var alert_show = false;


// Run after page will be loaded
$(window).on('load', function() {
    // Get time limit
    time_limit = Number(document.getElementById("time_limit").textContent);
    setInterval(setTime, 1000);
})


function setTime() {
    // Declare labels
    var minutesLabel = document.getElementById("minutes");
    var secondsLabel = document.getElementById("seconds");

    // Increase value
    ++totalSeconds;
    secondsLabel.innerHTML = pad(totalSeconds % 60);
    minutesLabel.innerHTML = pad(parseInt(totalSeconds / 60));

    // Update hidden form with current value
    time_spent = document.getElementById("time_spent");
    time_spent.value = getTimeSpent();

    // Check: Is time over?
    if (time_spent.value > time_limit) {
        // Check: Has been alert already shown?
        if (alert_show == false) {
            alert_show = true;
            alert('You are out of time. Press ok to go to next iteration.');
            time_spent.value = time_limit;
            document.getElementById("btn_skip").click();
        }
    }

}


function pad(val) {
  var valString = val + "";
  if (valString.length < 2) {
    return "0" + valString;
  } else {
    return valString;
  }
}


function getTimeSpent() {
    minutes = Number(document.getElementById("minutes").textContent);
    seconds = Number(document.getElementById("seconds").textContent);

    timeSpent = minutes*60+seconds;
    return timeSpent
}
