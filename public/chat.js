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

  const res = await fetch("https://api.simplyai.ie/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      message: userMessage,
      tone: tone || ""
    })
  });

  const data = await res.json();
  appendMessage("Pension Guru", data.response || "Something went wrong.", "planner");

  // Store returned user_id if new
  if (data.user_id) {
    sessionStorage.setItem("user_id", data.user_id);
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

// Auto-trigger GPT greeting
window.addEventListener("DOMContentLoaded", () => {
  const userId = ensureUserId();
  fetch("https://api.simplyai.ie/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      message: "__INIT__"
    })
  })
  .then(res => res.json())
  .then(data => {
    appendMessage("Pension Guru", data.response || "Welcome!", "planner");
    if (data.user_id) {
      sessionStorage.setItem("user_id", data.user_id);
    }
  });
});