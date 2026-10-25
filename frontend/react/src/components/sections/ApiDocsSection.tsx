import { Container } from "../shared/Container";

export const ApiDocsSection = () => {
  return (
    <section id="api" className="py-12 border-t border-box-border">
      <Container>
        {/* Section Header */}
        <div className="space-y-2 mb-8">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700">
              RESTful Integration
            </span>
            <span className="text-xs text-heading-3 font-mono">
              OpenAPI Specification & Endpoints
            </span>
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-heading-1">
            Flask NLP Engine REST API
          </h2>
          <p className="text-sm text-heading-3 max-w-3xl">
            Integrate the 6-stage toxicity detection pipeline into any external platform, microservice,
            or chat application via JSON HTTP endpoints.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 font-mono text-xs">
          {/* Endpoint Specification */}
          <div className="p-6 rounded-2xl bg-box-bg border border-box-border space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-box-border">
              <span className="font-bold text-heading-1 uppercase text-sm">
                Prediction Endpoint
              </span>
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[11px] font-bold">
                POST /predict
              </span>
            </div>

            <div className="space-y-2">
              <div className="font-bold text-heading-1">Request Headers:</div>
              <pre className="p-3 rounded-lg bg-body border border-box-border text-heading-2">
Content-Type: application/json
              </pre>
            </div>

            <div className="space-y-2">
              <div className="font-bold text-heading-1">Request Payload:</div>
              <pre className="p-3 rounded-lg bg-body border border-box-border text-heading-2">
{`{
  "comment": "Input sentence or paragraph to evaluate"
}`}
              </pre>
            </div>

            <div className="space-y-2">
              <div className="font-bold text-heading-1">Response JSON Schema:</div>
              <pre className="p-3 rounded-lg bg-body border border-box-border text-heading-2 overflow-x-auto text-[11px]">
{`{
  "toxic": 0.9900,
  "severe_toxic": 0.9526,
  "obscene": 0.0200,
  "threat": 0.9526,
  "insult": 0.9526,
  "identity_hate": 0.0200,
  "engine_mode": "Hybrid BiLSTM + Statistical WSD Pipeline",
  "syllabus_analysis": {
    "module_1_preliminaries": { ... },
    "module_2_word_level": { ... },
    "module_3_syntax_level": { ... },
    "module_4_semantic_analysis": { ... },
    "module_5_pragmatics_discourse": { ... },
    "module_6_ethics_and_xai": { ... }
  }
}`}
              </pre>
            </div>
          </div>

          {/* Code Samples */}
          <div className="p-6 rounded-2xl bg-box-bg border border-box-border space-y-4">
            <span className="font-bold text-heading-1 uppercase text-sm">
              Quick Integration Snippets
            </span>

            <div className="space-y-2">
              <div className="font-bold text-heading-1">cURL (Command-Line):</div>
              <pre className="p-3 rounded-lg bg-slate-950 text-slate-300 overflow-x-auto text-[11px]">
{`curl -X POST http://127.0.0.1:5000/predict \\
  -H "Content-Type: application/json" \\
  -d '{"comment": "You are an idiot"}'`}
              </pre>
            </div>

            <div className="space-y-2">
              <div className="font-bold text-heading-1">Python (requests):</div>
              <pre className="p-3 rounded-lg bg-slate-950 text-slate-300 overflow-x-auto text-[11px]">
{`import requests

url = "http://127.0.0.1:5000/predict"
payload = {"comment": "You are an idiot"}
res = requests.post(url, json=payload)
data = res.json()
print("Toxicity Score:", data["toxic"])`}
              </pre>
            </div>

            <div className="space-y-2">
              <div className="font-bold text-heading-1">JavaScript (Fetch):</div>
              <pre className="p-3 rounded-lg bg-slate-950 text-slate-300 overflow-x-auto text-[11px]">
{`const res = await fetch("http://127.0.0.1:5000/predict", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ comment: "You are an idiot" }),
});
const data = await res.json();
console.log(data);`}
              </pre>
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
};
