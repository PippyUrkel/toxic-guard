import { useState, useEffect } from "react";
import { Layout } from "./components/Layout";
import {
  PipelineConsole,
  PredictionPayload,
} from "./components/sections/PipelineConsole";
import { PipelineStages } from "./components/sections/PipelineStages";
import { DiscordSection } from "./components/sections/DiscordSection";
import { ApiDocsSection } from "./components/sections/ApiDocsSection";

function App() {
  const [result, setResult] = useState<PredictionPayload | null>(null);
  const [loading, setLoading] = useState(false);

  // Automatically execute default preset on initial mount with retry
  useEffect(() => {
    let attempts = 0;
    const runDefault = async () => {
      try {
        setLoading(true);
        let response: Response;
        try {
          response = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              comment: "You are a st*pid id1ot and I will k1ll you.",
            }),
          });
        } catch {
          response = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              comment: "You are a st*pid id1ot and I will k1ll you.",
            }),
          });
        }
        if (response.ok) {
          const data = await response.json();
          setResult(data);
        } else if (attempts < 2) {
          attempts++;
          setTimeout(runDefault, 1500);
        }
      } catch (err) {
        if (attempts < 2) {
          attempts++;
          setTimeout(runDefault, 1500);
        }
      } finally {
        setLoading(false);
      }
    };
    runDefault();
  }, []);

  return (
    <Layout title="ToxiGuard — 25PEC4CS1 NLP Linguistic & Toxicity Pipeline">
      <PipelineConsole
        result={result}
        loading={loading}
        setLoading={setLoading}
        onAnalysisComplete={(data) => setResult(data)}
      />
      <PipelineStages syllabus={result?.syllabus_analysis} />
      <DiscordSection />
      <ApiDocsSection />
    </Layout>
  );
}

export default App;
