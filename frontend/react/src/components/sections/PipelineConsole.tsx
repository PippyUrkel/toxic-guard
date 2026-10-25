import { useState, useId } from "react";
import { Container } from "../shared/Container";
import { extractTextFromPDF } from "../../utils/pdfReader";

export interface PredictionPayload {
  toxic: number;
  severe_toxic: number;
  obscene: number;
  threat: number;
  insult: number;
  identity_hate: number;
  engine_mode?: string;
  syllabus_analysis?: any;
  error?: string;
}

interface PipelineConsoleProps {
  onAnalysisComplete: (data: PredictionPayload | null, text: string) => void;
  result: PredictionPayload | null;
  loading: boolean;
  setLoading: (val: boolean) => void;
}

const TOXICITY_TARGETS = [
  { key: "toxic", label: "Toxic", desc: "General profanity or abusive language" },
  { key: "severe_toxic", label: "Severe Toxic", desc: "Extremely hateful, aggressive content" },
  { key: "obscene", label: "Obscene", desc: "Vulgarity, crude, sexually explicit terms" },
  { key: "threat", label: "Threat", desc: "Statements of intent to inflict harm/violence" },
  { key: "insult", label: "Insult", desc: "Disparaging, demeaning, or mocking remarks" },
  { key: "identity_hate", label: "Identity Hate", desc: "Attacks based on race, religion, gender" },
] as const;

const PRESETS = [
  {
    label: "Adversarial Leetspeak",
    text: "You are a st*pid id1ot and I will k1ll you.",
    desc: "Tests regex normalization and Levenshtein edit distance.",
  },
  {
    label: "Polysemous Metaphor",
    text: "The guitarist was killing it on stage tonight, the concert was incredible.",
    desc: "Tests WordNet Lesk WSD to prevent false-positive threat detection.",
  },
  {
    label: "Anaphora Binding",
    text: "Alex threw a punch at David. He is violent and should be reprimanded.",
    desc: "Tests Hobbs algorithm to resolve pronoun antecedents across sentences.",
  },
  {
    label: "Identity & Neutrality",
    text: "We attended an academic symposium on Muslim and Jewish cultural history.",
    desc: "Tests counterfactual debiasing to avoid false identity_hate triggers.",
  },
  {
    label: "Hostile Attack",
    text: "Shut up you disgusting pig, go die in a ditch.",
    desc: "Multi-category severe violation combining threat, insult, and obscenity.",
  },
  {
    label: "Clean Text",
    text: "Please submit your laboratory assignments by Friday afternoon.",
    desc: "Standard academic sentence with no toxic lexicon.",
  },
];

export const PipelineConsole = ({
  onAnalysisComplete,
  result,
  loading,
  setLoading,
}: PipelineConsoleProps) => {
  const [comment, setComment] = useState(
    "You are a st*pid id1ot and I will k1ll you."
  );
  const [fileName, setFileName] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const fileInputId = useId();

  const handleAnalyze = async (textToAnalyze?: string) => {
    const text = (textToAnalyze ?? comment).trim();
    if (!text) return;

    setLoading(true);
    setErrorMsg("");

    try {
      // First try relative /predict (proxied by Vite or served by Flask), then fallback to absolute
      let response: Response;
      try {
        response = await fetch("/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ comment: text }),
        });
      } catch {
        response = await fetch("http://127.0.0.1:5000/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ comment: text }),
        });
      }

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      onAnalysisComplete(data, text);
    } catch (err: any) {
      console.error("Analysis request failed:", err);
      setErrorMsg(
        "Could not connect to the NLP API backend. Ensure the Flask server is running on http://127.0.0.1:5000."
      );
      onAnalysisComplete(null, text);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setErrorMsg("");
    setLoading(true);

    try {
      let extracted = "";
      if (file.type === "text/plain" || file.name.endsWith(".txt")) {
        extracted = await file.text();
      } else if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
        extracted = await extractTextFromPDF(file);
      } else {
        setErrorMsg("Unsupported file format. Please upload a .txt or .pdf file.");
        setLoading(false);
        return;
      }

      setComment(extracted);
      await handleAnalyze(extracted);
    } catch (err) {
      console.error("File parsing error:", err);
      setErrorMsg("Failed to extract textual content from uploaded file.");
    } finally {
      setLoading(false);
    }
  };

  const wordCount = comment.trim() ? comment.trim().split(/\s+/).length : 0;
  const charCount = comment.length;

  // Compute maximum category probability
  const maxScore = result
    ? Math.max(
        result.toxic ?? 0,
        result.severe_toxic ?? 0,
        result.obscene ?? 0,
        result.threat ?? 0,
        result.insult ?? 0,
        result.identity_hate ?? 0
      )
    : 0;

  const isFlagged = maxScore >= 0.5;
  const isSevere = (result?.severe_toxic ?? 0) >= 0.5 || (result?.threat ?? 0) >= 0.5;

  return (
    <section id="console" className="pt-8 pb-12">
      <Container>
        {/* Section Header */}
        <div className="space-y-2 mb-8">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-xs uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700">
              Interactive Execution Environment
            </span>
            <span className="text-xs text-heading-3 font-mono">
              Course Code: 25PEC4CS1 • Natural Language Processing
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-heading-1">
            Sentence Toxicity Detection & Pipeline Inspector
          </h1>
          <p className="text-sm text-heading-3 max-w-3xl leading-relaxed">
            Submit any sentence or paragraph to run the full 6-stage NLP verification pipeline:
            Adversarial Leetspeak Normalization, HMM Viterbi POS Tagging, WordNet Lesk WSD,
            Hobbs Anaphora Resolution, BiLSTM Ensemble Scoring, and Explainable AI (XAI) Attribution.
          </p>
        </div>

        {/* Input Console Card */}
        <div className="p-5 sm:p-6 rounded-2xl bg-box-bg border border-box-border shadow-sm space-y-5">
          {/* Preset Buttons */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-heading-3">
              <span>Benchmark Test Presets:</span>
              <span>Click any preset to load scenario</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {PRESETS.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setComment(p.text);
                    setFileName("");
                    handleAnalyze(p.text);
                  }}
                  title={p.desc}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium border border-box-border hover:bg-slate-500/10 text-heading-2 transition-colors cursor-pointer"
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Textarea Area */}
          <div className="space-y-2">
            <div className="relative">
              <textarea
                rows={4}
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Type or paste input text here for NLP pipeline verification..."
                className="w-full p-4 rounded-xl font-mono text-sm bg-body border border-box-border text-heading-1 focus:outline-none focus:ring-1 focus:ring-slate-500 transition-all resize-y"
              />
            </div>
            <div className="flex flex-wrap items-center justify-between gap-3 text-xs font-mono text-heading-3">
              <div className="flex items-center gap-4">
                <span>Tokens: ~{wordCount}</span>
                <span>Characters: {charCount}</span>
                {fileName && (
                  <span className="text-teal-400">File: {fileName}</span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <label
                  htmlFor={fileInputId}
                  className="px-3 py-1 rounded-md border border-box-border hover:bg-slate-500/10 cursor-pointer text-heading-2 transition-colors"
                >
                  Upload TXT / PDF
                </label>
                <input
                  id={fileInputId}
                  type="file"
                  accept=".txt,.pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => {
                    setComment("");
                    setFileName("");
                    setErrorMsg("");
                  }}
                  className="px-3 py-1 rounded-md border border-box-border hover:bg-slate-500/10 text-heading-3 hover:text-heading-1 transition-colors cursor-pointer"
                >
                  Clear
                </button>
              </div>
            </div>
          </div>

          {/* Execution Controls */}
          <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-box-border">
            <div className="text-xs text-heading-3 font-mono">
              Endpoint: <code className="text-heading-2">POST /predict</code>
            </div>
            <button
              type="button"
              disabled={loading || !comment.trim()}
              onClick={() => handleAnalyze()}
              className="px-6 py-2.5 rounded-lg font-mono text-xs font-semibold bg-slate-900 text-slate-100 dark:bg-slate-100 dark:text-slate-900 hover:opacity-90 disabled:opacity-40 transition-opacity cursor-pointer flex items-center gap-2"
            >
              {loading ? (
                <>
                  <svg
                    className="animate-spin w-4 h-4"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8v8H4z"
                    />
                  </svg>
                  <span>Processing 6 NLP Stages...</span>
                </>
              ) : (
                <span>Execute Pipeline Analysis</span>
              )}
            </button>
          </div>

          {/* Error Banner */}
          {errorMsg && (
            <div className="p-3.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-xs font-mono text-rose-400">
              [API ERROR] {errorMsg}
            </div>
          )}
        </div>

        {/* Prediction Results Overview */}
        {result && (
          <div className="mt-8 space-y-6">
            {/* Verdict Card */}
            <div
              className={`p-5 rounded-2xl border transition-all ${
                isSevere
                  ? "bg-rose-950/20 border-rose-500/40 text-rose-200"
                  : isFlagged
                  ? "bg-amber-950/20 border-amber-500/40 text-amber-200"
                  : "bg-emerald-950/20 border-emerald-500/40 text-emerald-200"
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2 font-mono text-xs uppercase tracking-wider">
                    <span
                      className={`w-2 h-2 rounded-full ${
                        isSevere
                          ? "bg-rose-400 animate-ping"
                          : isFlagged
                          ? "bg-amber-400"
                          : "bg-emerald-400"
                      }`}
                    />
                    <span className="font-bold">
                      {isSevere
                        ? "CRITICAL VIOLATION: HIGH SEVERITY TOXICITY DETECTED"
                        : isFlagged
                        ? "MODERATION WARNING: TOXIC CONTENT FLAGGED"
                        : "VERDICT: CLEAN CONTENT (PIPELINE PASSED)"}
                    </span>
                  </div>
                  <p className="text-xs font-mono opacity-90">
                    Engine Mode: {result.engine_mode || "Hybrid BiLSTM + Statistical & WSD Pipeline"} • Max Confidence: {(maxScore * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="font-mono text-right text-xs">
                  <span className="px-3 py-1 rounded bg-black/40 border border-white/10 font-bold">
                    {isFlagged ? "ACTION: FILTER & FLAG" : "ACTION: PERMIT"}
                  </span>
                </div>
              </div>
            </div>

            {/* 6 Toxicity Dimension Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              {TOXICITY_TARGETS.map((t) => {
                const rawScore = Number(result[t.key] ?? 0);
                const pct = (rawScore * 100).toFixed(1);
                const flagged = rawScore >= 0.5;

                return (
                  <div
                    key={t.key}
                    className="p-4 rounded-xl bg-box-bg border border-box-border flex flex-col justify-between space-y-3"
                  >
                    <div>
                      <div className="flex items-center justify-between text-xs font-mono text-heading-3">
                        <span className="font-semibold text-heading-1">{t.label}</span>
                        <span
                          className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${
                            flagged
                              ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                              : "bg-slate-500/10 text-heading-3"
                          }`}
                        >
                          {flagged ? "FLAG" : "OK"}
                        </span>
                      </div>
                      <div className="mt-2 text-2xl font-bold font-mono tracking-tight text-heading-1">
                        {pct}%
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <div className="w-full h-1.5 rounded-full bg-slate-800/40 overflow-hidden">
                        <div
                          className={`h-full transition-all duration-500 ${
                            flagged ? "bg-rose-500" : "bg-emerald-500"
                          }`}
                          style={{ width: `${Math.min(100, Math.max(2, rawScore * 100))}%` }}
                        />
                      </div>
                      <p className="text-[10px] text-heading-3 line-clamp-1" title={t.desc}>
                        {t.desc}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Mathematical Distribution Panel (Module 1.4) */}
            {result.syllabus_analysis?.module_1_preliminaries?.probability_statistics && (
              <div className="p-4 rounded-xl bg-box-bg border border-box-border font-mono text-xs text-heading-2">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-heading-1 uppercase text-[11px] tracking-wider">
                      Statistical Distribution (Mod 1.4):
                    </span>
                    <span>
                      Mean (μ):{" "}
                      <strong className="text-heading-1">
                        {result.syllabus_analysis.module_1_preliminaries.probability_statistics.mean_probability}
                      </strong>
                    </span>
                    <span className="text-heading-3">•</span>
                    <span>
                      Variance (σ²):{" "}
                      <strong className="text-heading-1">
                        {result.syllabus_analysis.module_1_preliminaries.probability_statistics.variance}
                      </strong>
                    </span>
                    <span className="text-heading-3">•</span>
                    <span>
                      Std Dev (σ):{" "}
                      <strong className="text-heading-1">
                        {result.syllabus_analysis.module_1_preliminaries.probability_statistics.std_dev}
                      </strong>
                    </span>
                  </div>
                  <div className="text-[11px] text-heading-3">
                    Total Sentences: {result.syllabus_analysis.module_1_preliminaries.sentence_count} | Tokens: {result.syllabus_analysis.module_1_preliminaries.token_count}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </Container>
    </section>
  );
};
