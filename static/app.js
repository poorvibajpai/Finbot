const thread = document.getElementById("thread");
const form = document.getElementById("composer");
const input = document.getElementById("input");

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderMarkdownLite(str) {
  // Only bold (**text**) — kept intentionally minimal.
  return escapeHtml(str).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
}

function addMessage(role, text) {
  const el = document.createElement("div");
  el.className = "msg " + role;
  el.innerHTML = renderMarkdownLite(text);
  thread.appendChild(el);
  thread.scrollTop = thread.scrollHeight;
  return el;
}

function addTyping() {
  const el = document.createElement("div");
  el.className = "msg typing";
  el.textContent = "FinBot is typing…";
  thread.appendChild(el);
  thread.scrollTop = thread.scrollHeight;
  return el;
}

async function sendMessage(text) {
  addMessage("user", text);
  const typing = addTyping();
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    typing.remove();
    addMessage("bot", data.reply || "Sorry, something went wrong.");
  } catch (err) {
    typing.remove();
    addMessage("bot", "Sorry, I couldn't reach the server. Please try again.");
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  sendMessage(text);
});

// Greeting on load
addMessage("bot", window.__GREETING__);
input.focus();
