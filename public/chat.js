const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const chatbox = document.getElementById("chatbox");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const userId = sessionStorage.getItem("user_id");
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
});


function appendMessage(sender, text, role) {
  const parts = text.split(/\n{2,}/); // split on double newlines

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

// Auto-trigger GPT greeting after login
window.addEventListener("DOMContentLoaded", () => {
  const userId = sessionStorage.getItem("user_id");
  if (userId) {
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
    });
  }
});

function triggerInitialGreeting(userId) {
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
  })
  .catch(err => console.error("Init message failed:", err));
}

