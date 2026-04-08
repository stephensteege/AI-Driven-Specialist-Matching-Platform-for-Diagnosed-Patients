const messageInput = document.getElementById("message");
const sendBtn = document.getElementById("sendBtn");
const charCount = document.getElementById("charCount");
const chatForm = document.getElementById("chatForm");
const chatbox = document.getElementById("chatbox");
const chips = document.querySelectorAll(".chip");
const themeSwitch = document.getElementById("themeSwitch");
const themeLabel = document.getElementById("themeLabel");

function updateCharCount() {
  const length = messageInput.value.length;
  charCount.textContent = length;
  sendBtn.disabled = messageInput.value.trim().length === 0;
}

function autoResizeTextarea() {
  messageInput.style.height = "auto";
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 220)}px`;
}

function showChatbox() {
  chatbox.classList.remove("hidden");
}

function addBubble(text, className) {
  const li = document.createElement("li");
  li.className = className;
  li.textContent = text;
  chatbox.appendChild(li);
  showChatbox();
  li.scrollIntoView({ behavior: "smooth", block: "end" });
}

function formatResponse(data) {
  let text = `Intent: ${data.intent}\n\nSlots:\n`;
  let foundUsefulSlot = false;

  if (Array.isArray(data.slots) && data.slots.length > 0) {
    for (const item of data.slots) {
      if (item.slot !== "O") {
        text += `• ${item.word} → ${item.slot}\n`;
        foundUsefulSlot = true;
      }
    }
  }

  if (!foundUsefulSlot) {
    text += "No slots found.";
  }

  return text.trim();
}

async function runPrediction(inputText) {
  const loadingBubble = document.createElement("li");
  loadingBubble.className = "system_bubble";
  loadingBubble.textContent = "Thinking...";
  chatbox.appendChild(loadingBubble);
  showChatbox();
  loadingBubble.scrollIntoView({ behavior: "smooth", block: "end" });

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: inputText }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    const rawText = await response.text();

    let data;
    try {
      data = JSON.parse(rawText);
    } catch (jsonError) {
      loadingBubble.remove();
      console.error("Invalid JSON response:", jsonError, rawText);
      addBubble("The server returned invalid JSON.", "system_bubble error_bubble");
      return;
    }

    loadingBubble.remove();

    if (!response.ok) {
      console.error("Prediction failed:", data);
      addBubble(data.error || data.details || "Request failed.", "system_bubble error_bubble");
      return;
    }

    addBubble(formatResponse(data), "system_bubble");
  } catch (err) {
    clearTimeout(timeoutId);
    loadingBubble.remove();
    console.error("Fetch error:", err);

    if (err.name === "AbortError") {
      addBubble("The request took too long. Please try again.", "system_bubble error_bubble");
      return;
    }

    addBubble("Could not connect to backend.", "system_bubble error_bubble");
  }
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const inputText = messageInput.value.trim();
  if (!inputText) return;

  addBubble(inputText, "user_bubble");
  messageInput.value = "";
  updateCharCount();
  autoResizeTextarea();

  await runPrediction(inputText);
});

messageInput.addEventListener("input", () => {
  updateCharCount();
  autoResizeTextarea();
});

messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled) {
      chatForm.requestSubmit();
    }
  }
});

chips.forEach((chip) => {
  chip.addEventListener("click", () => {
    const text = chip.textContent.trim();
    messageInput.value = text;
    updateCharCount();
    autoResizeTextarea();
    chatForm.requestSubmit();
  });
});

themeSwitch.addEventListener("click", () => {
  const html = document.documentElement;
  const isDark = html.getAttribute("data-theme") === "dark";

  if (isDark) {
    html.setAttribute("data-theme", "light");
    themeSwitch.setAttribute("aria-checked", "false");
    themeLabel.textContent = "Light";
  } else {
    html.setAttribute("data-theme", "dark");
    themeSwitch.setAttribute("aria-checked", "true");
    themeLabel.textContent = "Dark";
  }
});

updateCharCount();
autoResizeTextarea();