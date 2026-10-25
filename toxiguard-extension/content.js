console.log("✅ content.js loaded on WhatsApp Web");

function detectAndHighlight() {
  // Function to find the WhatsApp message input box
  const findInputBox = () =>
    document.querySelector(
      "div[contenteditable='true'][data-tab='10'], div[contenteditable='true'][role='textbox']"
    );

  // Interval to keep checking until input box is available
  const checkInput = setInterval(() => {
    const inputBox = findInputBox();

    if (!inputBox) {
      console.warn("⚠️ Input box not found yet");
      return;
    }

    console.log("✅ Input box found:", inputBox);
    clearInterval(checkInput); // Stop checking once found

    // Observer to detect typing or changes in the input box
    const observer = new MutationObserver(async () => {
      const text = inputBox.innerText.trim();

      if (!text) {
        inputBox.style.border = "none";
        return;
      }

      console.log("📝 Text detected:", text);

      try {
        const response = await fetch("http://127.0.0.1:5000/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ comment: text }),
        });

        const data = await response.json();
        console.log("📦 Prediction result:", data);

        const toxicScore = Math.max(
          data.toxic,
          data.severe_toxic,
          data.obscene,
          data.threat,
          data.insult,
          data.identity_hate
        );

        if (toxicScore > 0.5) {
          inputBox.style.setProperty("border", "3px solid red", "important");
          console.log("🚨 Toxic detected — red border applied");
        } else {
          inputBox.style.setProperty("border", "3px solid green", "important");
          console.log("✅ Non-toxic — green border applied");
        }
      } catch (err) {
        console.error("❌ Error fetching from Flask:", err);
      }
    });

    observer.observe(inputBox, { childList: true, subtree: true, characterData: true });
  }, 1000); // Check every second
}

// Start the detection
detectAndHighlight();
