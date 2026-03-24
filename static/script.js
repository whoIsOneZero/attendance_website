// === GLOBAL UTILITIES (Runs on all pages) ===
document.addEventListener("DOMContentLoaded", () => {
  // --- Password Toggle Logic ---
  const toggleBtn = document.querySelector("#togglePassword");
  const passwordInput = document.querySelector("#password");

  if (toggleBtn && passwordInput) {
    toggleBtn.addEventListener("click", function () {
      const isPassword = passwordInput.getAttribute("type") === "password";
      passwordInput.setAttribute("type", isPassword ? "text" : "password");
      this.textContent = isPassword ? "HIDE" : "SHOW";
    });
  }

  // --- Login Loader Logic ---
  const loginForm = document.querySelector("form[action*='login']");
  const loader = document.getElementById("loader");

  if (loginForm && loader) {
    loginForm.addEventListener("submit", () => {
      const btn = loginForm.querySelector("button[type='submit']");
      loader.style.display = "flex";
      btn.disabled = true;
      btn.style.opacity = "0.5";
      btn.textContent = "Logging in...";
    });
  }
});

// === ATTENDANCE PAGE LOGIC ===
const form = document.getElementById("attendanceForm");
const memberInput = document.getElementById("memberSearch");
const hiddenIdInput = document.getElementById("selected_member_id");
const membersList = document.getElementById("membersList");
const loader = document.getElementById("loader"); // Global reference for index.html

const memberModal = document.getElementById("memberModal");
const openRegisterBtn = document.getElementById("openRegisterBtn");
const openUpdateBtn = document.getElementById("openUpdateBtn");
const saveMemberBtn = document.getElementById("saveMemberBtn");
const modalTitle = document.getElementById("modalTitle");
const closeModal = document.getElementById("closeModal");

let allMembers = [];
let currentEditId = null;

// Helper: Show Toast Notifications
let popupTimer; // Variable to track the timer

function showPopup(message, type = "success") {
  const popup = document.getElementById("popup");
  const content = document.getElementById("popup-content");

  if (!popup || !content) {
    alert(message);
    return;
  }

  // Clear any existing timer if a new popup is triggered
  clearTimeout(popupTimer);

  content.textContent = message;
  popup.className = `popup ${type} show`;

  // Auto-hide after 4 seconds
  popupTimer = setTimeout(() => {
    popup.classList.remove("show");
  }, 4000);
}

if (form) {
  // 1. Attendance Submission (Clock In)
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const memberId = hiddenIdInput.value;
    if (!memberId) {
      showPopup("❌ Please select a valid member first", "error");
      return;
    }

    // --- SHOW LOADER ---
    if (loader) loader.style.display = "flex";

    const payload = {
      member_id: memberId,
      type: document.getElementById("type").value,
      notes: document.getElementById("notes").value,
    };

    const submitBtn = document.getElementById("submitBtn");
    submitBtn.disabled = true;

    try {
      const res = await fetch("/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await res.json();

      if (res.ok) {
        showPopup("✅ Marked Present!", "success");
        form.reset();
        hiddenIdInput.value = "";
        openUpdateBtn.style.display = "none";
      } else {
        showPopup(`❌ ${result.message}`, "error");
      }
    } catch (err) {
      showPopup("❌ Submission failed. Check connection.", "error");
    } finally {
      // --- HIDE LOADER ---
      if (loader) loader.style.display = "none";
      submitBtn.disabled = false;
      submitBtn.textContent = "Check In";
    }
  });

  // 2. Search & Edit Visibility
  const suggestionsContainer = document.getElementById("customSuggestions");

  memberInput.addEventListener("input", (e) => {
    if (!suggestionsContainer) return;
    const val = e.target.value.toLowerCase().trim();
    suggestionsContainer.innerHTML = "";

    if (val.length < 2) {
      suggestionsContainer.style.display = "none";
      return;
    }

    // Filter members based on name or phone
    const matches = allMembers
      .filter(
        (m) =>
          m.full_name.toLowerCase().includes(val) ||
          m.phone_number.includes(val),
      )
      .slice(0, 8); // Limit to top 8 results for mobile speed

    if (matches.length > 0) {
      matches.forEach((match) => {
        const div = document.createElement("div");
        div.className = "suggestion-item";
        div.textContent = `${match.full_name} (${match.phone_number})`;

        div.onclick = () => {
          memberInput.value = `${match.full_name} (${match.phone_number})`;
          hiddenIdInput.value = match.id;
          openUpdateBtn.style.display = "inline-block";
          suggestionsContainer.style.display = "none";
        };

        suggestionsContainer.appendChild(div);
      });
      suggestionsContainer.style.display = "block";
    } else {
      suggestionsContainer.style.display = "none";
      hiddenIdInput.value = "";
      openUpdateBtn.style.display = "none";
    }
  });

  // Close dropdown if user clicks outside
  document.addEventListener("click", (e) => {
    if (e.target !== memberInput) {
      suggestionsContainer.style.display = "none";
    }
  });

  // 3. Open Modal: New Member
  openRegisterBtn.addEventListener("click", () => {
    currentEditId = null;
    modalTitle.textContent = "New Member Registration";
    document.getElementById("modal_name").value = memberInput.value;
    document.getElementById("modal_phone").value = "";
    document.getElementById("modal_scd").value = "";
    document.getElementById("modal_membership_type").value = "Member";
    memberModal.style.display = "flex";
  });

  // 4. Open Modal: Update Member
  openUpdateBtn.addEventListener("click", () => {
    const match = allMembers.find((m) => m.id === hiddenIdInput.value);
    if (match) {
      currentEditId = match.id;
      modalTitle.textContent = "Update Member Profile";
      document.getElementById("modal_name").value = match.full_name;
      document.getElementById("modal_phone").value = match.phone_number;
      document.getElementById("modal_scd").value = match.scd_group || "";
      document.getElementById("modal_membership_type").value =
        match.membership_type || "Member";
      memberModal.style.display = "flex";
    }
  });

  // 5. Save Logic (Unified Create/Update)
  saveMemberBtn.addEventListener("click", async () => {
    const payload = {
      full_name: document.getElementById("modal_name").value.trim(),
      phone_number: document.getElementById("modal_phone").value.trim(),
      scd_group: document.getElementById("modal_scd").value,
      membership_type: document.getElementById("modal_membership_type").value,
    };

    if (!payload.full_name || !payload.phone_number) {
      showPopup("❌ Name and Phone are required", "error");
      return;
    }

    // --- SHOW LOADER ---
    if (loader) loader.style.display = "flex";

    const url = currentEditId ? "/update-member" : "/create-member";
    if (currentEditId) payload.id = currentEditId;

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const result = await res.json();
        showPopup(
          currentEditId ? "✅ Profile Updated!" : "✅ Member Registered!",
        );
        memberModal.style.display = "none";

        await loadMembers(); // Refresh local list

        const updatedMember = result.member || payload;
        memberInput.value = `${updatedMember.full_name} (${updatedMember.phone_number})`;
        hiddenIdInput.value = updatedMember.id || currentEditId;
        openUpdateBtn.style.display = "inline-block";
      } else {
        const errData = await res.json();
        showPopup(`❌ ${errData.message}`, "error");
      }
    } catch (err) {
      showPopup("❌ Operation failed", "error");
    } finally {
      // --- HIDE LOADER ---
      if (loader) loader.style.display = "none";
    }
  });

  // Close modal handlers
  closeModal.addEventListener(
    "click",
    () => (memberModal.style.display = "none"),
  );
  memberModal.addEventListener("click", (e) => {
    if (e.target === memberModal) memberModal.style.display = "none";
  });
}

// 6. Fetch Members from Database
// 6. Fetch Members from Database
async function loadMembers() {
  try {
    const response = await fetch("/get-members");
    if (!response.ok) throw new Error("Failed to fetch members");
    const data = await response.json();
    allMembers = data;

    // Check if membersList exists before trying to modify it
    const membersListElement = document.getElementById("membersList");
    if (membersListElement) {
      membersListElement.innerHTML = "";
      allMembers.forEach((member) => {
        const option = document.createElement("option");
        option.value = `${member.full_name} (${member.phone_number})`;
        membersListElement.appendChild(option);
      });
    }
  } catch (error) {
    console.error("Error loading members:", error);
  }
}

// Initial load - ONLY if the attendance form exists
if (form) {
  loadMembers();
}
