/*Toggle button*/
document.getElementById("toggleBtn").addEventListener("click", function() {
  this.classList.toggle("active");
  if (this.classList.contains("active")) {
    this.textContent = "Turn off";
    fetch('/toggle', {
      method: 'POST',
      body: JSON.stringify({value: 1}),
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => {
    })
    .catch(error => {
    });
  } else {
    this.textContent = "Turn on";
    fetch('/toggle', {
      method: 'POST',
      body: JSON.stringify({value: 0}),
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => {
    })
    .catch(error => {
    });
  }
});

/*For settings page*/
document.addEventListener("DOMContentLoaded", function() {
  const inputFields = document.querySelectorAll("input[type='number']");
  inputFields.forEach(function(inputField) {
    inputField.addEventListener("input", function() {
      let value = parseInt(inputField.value);
      if (isNaN(value)) {
        inputField.value = "";
      } else if (value > 10) {
        inputField.value = "10";
      } else if (value < -10) {
        inputField.value = "-10";
      }
    });

    inputField.addEventListener("blur", function() {
      let value = parseInt(inputField.value);
      if (isNaN(value)) {
        inputField.value = "";
      } else if (value > 10) {
        inputField.value = "10";
      }
    });
  });
});

// Function to save settings
function saveSettings() {
  const scheduleData = [];
  const inputFields = document.querySelectorAll("input[type='number']");
  inputFields.forEach(function(inputField) {
    scheduleData.push(parseInt(inputField.value));
  });

  // Send schedule data to Flask backend via AJAX
  fetch('/settings', {
    method: 'POST',
    body: JSON.stringify({schedule: scheduleData}),
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(function(response) {
    if (response.ok) {
      console.log("Settings saved!");
    } else {
      console.error("Failed to save settings:", response.statusText);
    }
  })
  .catch(function(error) {
    console.error("Failed to save settings:", error);
  });
  alert("Settings saved!");
}

function resetSettings(){
  alert("Settings reset!");
  fetch('/reset', {
  })
}


