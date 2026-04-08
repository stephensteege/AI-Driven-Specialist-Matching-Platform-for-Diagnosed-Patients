/**
 * File: script.js
 *
 * Description:
 * This client-side script handles user interaction for the chat interface,
 * including input handling, UI updates, and communication with the backend
 * Flask API for intent and slot prediction.
 *
 * Main Features:
 * - Dynamically updates character count and textarea size.
 * - Sends user input to the backend (/predict) via a POST request.
 * - Displays user and system messages as chat bubbles.
 * - Formats model responses (intent + slots) for readability.
 * - Handles request timeouts and error states gracefully.
 * - Supports quick input via clickable suggestion chips.
 * - Provides light/dark theme toggle functionality.
 */

// Cache frequently used DOM elements for efficiency and readability.
const messageInput = document.getElementById("message");
const sendBtn = document.getElementById("sendBtn");
const charCount = document.getElementById("charCount");
const chatForm = document.getElementById("chatForm");
const chatbox = document.getElementById("chatbox");
const chips = document.querySelectorAll(".chip");
const themeSwitch = document.getElementById("themeSwitch");
const themeLabel = document.getElementById("themeLabel");

/**
 * Updates the displayed character count and enables/disables
 * the send button based on whether input is present.
 */
function updateCharCount() {
  const length = messageInput.value.length;
  charCount.textContent = length;
  sendBtn.disabled = messageInput.value.trim().length === 0;
}

/**
 * Automatically resizes the textarea height based on content,
 * with a maximum height limit to prevent excessive growth.
 */
function autoResizeTextarea() {
  messageInput.style.height = "auto";
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 220)}px`;
}

/**
 * Ensures the chatbox is visible when messages are added.
 */
function showChatbox() {
  chatbox.classList.remove("hidden");
}

/**
 * Creates and appends a chat bubble (user or system) to the chatbox.
 *
 * @param {string} text - The message content to display.
 * @param {string} className - CSS class defining the bubble style.
 */
function addBubble(text, className) {
  const li = document.createElement("li");
  li.className = className;
  li.textContent = text;
  chatbox.appendChild(li);

  showChatbox();

  // Scroll to the newest message for better UX.
  li.scrollIntoView({ behavior: "smooth", block: "end" });
}

/**
 * Formats the backend response into a readable string.
 * Displays the predicted intent and any meaningful slot labels.
 *
 * @param {Object} data - JSON response from backend.
 * @returns {string} - Formatted text for display.
 */
function formatResponse(data) {
  let text = `Intent: ${data.intent}\n\nSlots:\n`;
  let foundUsefulSlot = false;

  // Only display slots that are not "O" (outside/no label).
  if (Array.isArray(data.slots) && data.slots.length > 0) {
    for (const item of data.slots) {
      if (item.slot !== "O") {
        text += `• ${item.word} → ${item.slot}\n`;
        foundUsefulSlot = true;
      }
    }
  }

  // If no meaningful slots were found, display fallback message.
  if (!foundUsefulSlot) {
    text += "No slots found.";
  }

  return text.trim();
}

/**
 * Sends user input to the backend for prediction and handles
 * response rendering, including loading states and errors.
 *
 * @param {string} inputText - The user's input text.
 */
async function runPrediction(inputText) {
  // Create and display a temporary loading message.
  const loadingBubble = document.createElement("li");
  loadingBubble.className = "system_bubble";
  loadingBubble.textContent = "Thinking...";
  chatbox.appendChild(loadingBubble);

  showChatbox();
  loadingBubble.scrollIntoView({ behavior: "smooth", block: "end" });

  // Setup request timeout using AbortController.
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    // Send POST request to backend API.
    const response = await fetch("/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: inputText }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    // Read raw response first to handle invalid JSON safely.
    const rawText = await response.text();

    let data;
    try {
      data = JSON.parse(rawText);
    } catch (jsonError) {
      // Handle malformed JSON responses.
      loadingBubble.remove();
      console.error("Invalid JSON response:", jsonError, rawText);
      addBubble("The server returned invalid JSON.", "system_bubble error_bubble");
      return;
    }

    loadingBubble.remove();

    // Handle HTTP errors returned by backend.
    if (!response.ok) {
      console.error("Prediction failed:", data);
      addBubble(
        data.error || data.details || "Request failed.",
        "system_bubble error_bubble"
      );
      return;
    }

    // Display formatted prediction result.
    addBubble(formatResponse(data), "system_bubble");

  } catch (err) {
    clearTimeout(timeoutId);
    loadingBubble.remove();
    console.error("Fetch error:", err);

    // Handle request timeout specifically.
    if (err.name === "AbortError") {
      addBubble("The request took too long. Please try again.", "system_bubble error_bubble");
      return;
    }

    // Handle general connection errors.
    addBubble("Could not connect to backend.", "system_bubble error_bubble");
  }
}

/**
 * Handles form submission:
 * - Prevents page reload
 * - Displays user message
 * - Clears input
 * - Sends request to backend
 */
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const inputText = messageInput.value.trim();
  if (!inputText) return;

  addBubble(inputText, "user_bubble");

  // Reset input field after submission.
  messageInput.value = "";
  updateCharCount();
  autoResizeTextarea();

  await runPrediction(inputText);
});

/**
 * Update UI in real-time as the user types.
 */
messageInput.addEventListener("input", () => {
  updateCharCount();
  autoResizeTextarea();
});

/**
 * Allow Enter key to submit the form (without Shift).
 * Shift + Enter allows multi-line input.
 */
messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled) {
      chatForm.requestSubmit();
    }
  }
});

/**
 * Handle quick suggestion chips:
 * - Fill input
 * - Auto-submit immediately
 */
chips.forEach((chip) => {
  chip.addEventListener("click", () => {
    const text = chip.textContent.trim();
    messageInput.value = text;
    updateCharCount();
    autoResizeTextarea();
    chatForm.requestSubmit();
  });
});

/**
 * Toggle between light and dark themes.
 * Updates both the HTML attribute and accessibility state.
 */
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

// Initialize UI state on page load.
updateCharCount();
autoResizeTextarea();