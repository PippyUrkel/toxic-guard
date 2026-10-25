document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("sendBtn");
  const input = document.getElementById("commentInput");
  const output = document.getElementById("output");

  btn.addEventListener("click", async () => {
    const text = input.value.trim() || "You are killing it on stage!";
    output.style.display = "block";
    output.innerHTML = "⏳ Running 6-Module NLP Pipeline...";

    try {
      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ comment: text }),
      });

      const data = await response.json();
      const maxScore = Math.max(
        data.toxic || 0,
        data.severe_toxic || 0,
        data.obscene || 0,
        data.threat || 0,
        data.insult || 0,
        data.identity_hate || 0
      );

      const wsdList = data.syllabus_analysis?.module_4_semantic_analysis?.wordnet_lesk_wsd || [];
      const wsdSummary = wsdList.length
        ? wsdList.map((w) => `${w.word} → ${w.selected_synset}`).join(", ")
        : "No ambiguous polysemy";

      output.innerHTML = `
        <div><strong>Status:</strong> ${maxScore > 0.5 ? "🚨 TOXIC" : "✅ SAFE"} (${(maxScore * 100).toFixed(1)}%)</div>
        <div><strong>Toxic:</strong> ${(data.toxic * 100).toFixed(1)}% | <strong>Insult:</strong> ${(data.insult * 100).toFixed(1)}%</div>
        <div><strong>Threat:</strong> ${(data.threat * 100).toFixed(1)}% | <strong>Obscene:</strong> ${(data.obscene * 100).toFixed(1)}%</div>
        <div style="margin-top:4px;color:#5eead4;"><strong>Lesk WSD:</strong> ${wsdSummary}</div>
      `;
    } catch (err) {
      output.innerHTML = "❌ Ensure Flask server is running on http://127.0.0.1:5000";
    }
  });
});
