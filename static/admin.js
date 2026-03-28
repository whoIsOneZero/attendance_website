const datePicker = document.getElementById("exportDate");
const statsLabel = document.getElementById("statsLabel");
const totalDisplay = document.getElementById("totalToday");
const breakdownContainer = document.getElementById("breakdownContainer");

// Function to fetch stats for a specific date
async function updateDashboard(selectedDate) {
  totalDisplay.textContent = "...";
  breakdownContainer.innerHTML = ""; // Clear old stats

  try {
    const response = await fetch(`/api/stats-by-date?date=${selectedDate}`);
    const data = await response.json();

    totalDisplay.textContent = data.total;

    // Populate Breakdown
    if (data.breakdown.length > 0) {
      data.breakdown.forEach((item) => {
        const row = document.createElement("div");
        row.className = "breakdown-row";
        row.innerHTML = `
                    <span>${item.type}</span>
                    <span class="breakdown-count">${item.count}</span>
                `;
        breakdownContainer.appendChild(row);
      });
    } else {
      breakdownContainer.innerHTML =
        "<p style='font-size:0.8rem; opacity:0.5;'>No records found.</p>";
    }

    const today = new Date().toISOString().split("T")[0];
    statsLabel.textContent =
      selectedDate === today
        ? "Attendance for Today"
        : `Attendance for ${selectedDate}`;
  } catch (err) {
    totalDisplay.textContent = "Error";
  }
}

// Event: Change Date
datePicker.addEventListener("change", (e) => {
  updateDashboard(e.target.value);
});

// Event: Download Excel
document.getElementById("downloadBtn").addEventListener("click", () => {
  const date = datePicker.value;
  if (!date) return alert("Please select a date");
  window.location.href = `/export-attendance?date=${date}`;
});

// Init: Set today's date and load initial stats
const todayStr = new Date().toISOString().split("T")[0];
datePicker.value = todayStr;
updateDashboard(todayStr);
