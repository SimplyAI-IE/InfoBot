const USE_LOCAL = true;
const API_BASE = USE_LOCAL ? "http://localhost:10000" : "https://your-backend-service.onrender.com";

const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const chatbox = document.getElementById("chatbox");

function ensureUserId() {
  let userId = sessionStorage.getItem("user_id");
  if (!userId) {
    userId = "anon_" + Math.random().toString(36).substring(2, 12);
    sessionStorage.setItem("user_id", userId);
  }
  return userId;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const userId = ensureUserId();
  const userMessage = input.value.trim();
  const tone = sessionStorage.getItem("user_tone");

  if (!userMessage) return;

  appendMessage(sessionStorage.getItem("user_name")?.split(" ")[0] || "You", userMessage, "user");
  input.value = "";

  try {
    const res = await fetch(`${API_BASE}/respond`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        message: userMessage,
        tone: tone || ""
      })
    });

    const data = await res.json();
    appendMessage("Whitesands Concierge", data.response || "Something went wrong.", "planner");

    if (data.user_id) {
      sessionStorage.setItem("user_id", data.user_id);
    }
  } catch (err) {
    console.error("Fetch error:", err);
    appendMessage("System", "Unable to connect to the assistant. Please try again.", "planner");
  }
});

function appendMessage(sender, text, role) {
  const parts = text.split(/\n{2,}/);
  parts.forEach(part => {
    const message = document.createElement("div");
    message.classList.add("message", role);
    const formatted = part.trim().replace(
      /(https?:\/\/[^\s]+)/g,
      '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    message.innerHTML = `<strong>${sender}:</strong> ${formatted}`;
    chatbox.appendChild(message);

    if (role === "planner") {
      const btn = document.getElementById("download-pdf");
      if (btn) btn.disabled = false;
    }
  });

  chatbox.scrollTop = chatbox.scrollHeight;
}

window.addEventListener("DOMContentLoaded", () => {
  const userId = ensureUserId();
  fetch(`${API_BASE}/respond`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      message: "__INIT__"
    })
  })
  .then(res => res.json())
  .then(data => {
    appendMessage("Whitesands Concierge", data.response || "Welcome!", "planner");
    if (data.user_id) {
      sessionStorage.setItem("user_id", data.user_id);
    }
  })
  .catch(err => {
    console.error("Init request failed:", err);
    appendMessage("System", "Failed to start the assistant.", "planner");
  });
});
