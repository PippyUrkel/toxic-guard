import { useState } from "react";
import { Container } from "../shared/Container";

const COMMANDS = [
  {
    prefix: "!autoban <val|off>",
    slash: "-",
    description: "Configures automatic permanent ban threshold (default: >= 0.85 / 85%).",
  },
  {
    prefix: "!timeout <val|off>",
    slash: "-",
    description: "Configures automated 15-minute mute threshold (default: >= 0.70 / 70%).",
  },
  {
    prefix: "!scan_channel [limit]",
    slash: "-",
    description: "Audits recent channel messages (10-100) and computes channel toxicity health.",
  },
  {
    prefix: "!scan_user @user",
    slash: "-",
    description: "Evaluates a member's recent messages to calculate their aggregate toxicity risk profile.",
  },
  {
    prefix: "!infractions @user",
    slash: "-",
    description: "Displays member violation history, prior warnings, and peak toxicity score.",
  },
  {
    prefix: "!explain <text>",
    slash: "/explain <text>",
    description: "Generates full 6-stage NLP reasoning report showing why content was flagged or banned.",
  },
  {
    prefix: "!analyze <text>",
    slash: "/analyze <text>",
    description: "Evaluates text across all 6 toxicity classes with visual probability bars and trigger tokens.",
  },
  {
    prefix: "!inspect <token>",
    slash: "-",
    description: "Deep lexical inspection of a word (morphology, Porter stem, lemma, leetspeak, WordNet synset).",
  },
  {
    prefix: "!pipeline",
    slash: "/pipeline",
    description: "Outputs complete theoretical and mathematical documentation of the 25PEC4CS1 pipeline.",
  },
  {
    prefix: "!stats",
    slash: "-",
    description: "Displays real-time session moderation counters (scanned, flagged, clean, bans, timeouts).",
  },
];

export const DiscordSection = () => {
  const [terminalInput, setTerminalInput] = useState("!explain Shut up you disgusting pig, go die in a ditch, I will murder you.");
  const [terminalOutput, setTerminalOutput] = useState<string>(
`[TOXIGUARD DISCORD BOT SIMULATION READY - .ENV CONFIG LOADED]
Tiered Enforcement: Flag >= 50% | Timeout >= 70% | Auto-Ban >= 85%
Type !explain <text>, !analyze <text>, !autoban 0.85, !scan_channel, or !stats
Or click any sample command below to simulate instant bot responses.`
  );
  const [isSimulating, setIsSimulating] = useState(false);

  const runCommandSimulation = async (cmdString: string) => {
    const trimmed = cmdString.trim();
    if (!trimmed) return;

    setIsSimulating(true);
    setTerminalOutput((prev) => `${prev}\n\n> ${trimmed}\n[Processing NLP Pipeline...]`);

    try {
      const parts = trimmed.split(" ");
      const cmd = parts[0].toLowerCase();
      const arg = parts.slice(1).join(" ");

      if (cmd === "!pipeline") {
        setTerminalOutput((prev) => `${prev}\n
================================================================
TOXIGUARD NLP PIPELINE ARCHITECTURE (Course: 25PEC4CS1)
Fr. Conceicao Rodrigues College of Engineering (CRCE), Mumbai
================================================================
Stage 1: Mathematical Foundations, Tokenization & Bayesian Priors
Stage 2: Word-Level Adversarial Normalization & N-Gram LM Perplexity
Stage 3: Syntactic Penn Treebank HMM + Viterbi POS Trellis Decoding
Stage 4: Semantic Disambiguation (WordNet Lesk WSD) & TF-IDF Cosine
Stage 5: Pragmatics: Hobbs Anaphora Resolution & Centering Theory
Stage 6: Explainable AI (XAI) Token Attribution & Privacy Audit
================================================================`);
      } else if (cmd === "!autoban") {
        const val = arg ? arg : "0.85";
        setTerminalOutput((prev) => `${prev}\n
[AUTOBAN SETTINGS UPDATED]
  Status    : ENABLED
  Threshold : ${val.includes("off") ? "DISABLED" : `${(parseFloat(val) || 0.85) * 100}%`}
  Policy    : Members posting content exceeding this threshold receive an immediate permanent server ban with audit log attribution.`);
      } else if (cmd === "!scan_channel") {
        setTerminalOutput((prev) => `${prev}\n
[CHANNEL AUDIT REPORT: #general]
  Messages Scanned : 50
  Flagged Messages : 4 (8.0% toxicity rate)
  Peak Toxicity    : 98.9% (toxic, threat)
  Channel Health   : FAIR

[SAMPLED TOXIC VIOLATIONS]
  * user_9102      -> toxic (98.9%): "Shut up you disgusting pig, go die..." [AUTOBANNED]
  * player_x       -> insult (78.4%): "You are an idiot" [TIMED OUT 15m]`);
      } else if (cmd === "!stats") {
        setTerminalOutput((prev) => `${prev}\n
[TOXIGUARD SESSION MODERATION METRICS]
  Messages Monitored : 184
  Messages Flagged   : 26
  Messages Clean     : 158
  Timeouts Issued    : 12 (Threshold: >= 70%)
  Bans Issued        : 5  (Threshold: >= 85% Auto-Ban)

[ACTIVE POLICY (.ENV)]
  Auto-Ban Threshold : 85.0% (ENABLED)
  Timeout Threshold  : 70.0% (Duration: 15m)
  General Warning    : 50.0%

[TRIGGERED CATEGORY BREAKDOWN]
  toxic          : 26
  severe_toxic   : 7
  obscene        : 11
  threat         : 8
  insult         : 20
  identity_hate  : 3`);
      } else if (cmd === "!test_cases") {
        setTerminalOutput((prev) => `${prev}\n
[BENCHMARK TEST SUITE: 25PEC4CS1 PIPELINE]
- Scenario: Severe Attack
  Input   : "Shut up you disgusting pig, go die in a ditch, I will murder you."
  Verdict : AUTOBAN (>=85%) (toxic: 99.0%, threat: 95.3%)

- Scenario: Moderate Insult
  Input   : "You are a stupid idiot."
  Verdict : AUTOBAN (>=85%) (toxic: 95.3%, insult: 95.3%)

- Scenario: Polysemous Praise (WSD)
  Input   : "The guitarist was killing it on stage tonight."
  Verdict : CLEAN (threat: 2.0%, WSD Safe Metaphor)

- Scenario: Cross-Sentence Anaphora
  Input   : "Alex shoved David. He is violent and should be banned."
  Verdict : TIMEOUT (>=70%) (insult: 78.4%, Anaphor 'He' -> Antecedent: 'Alex')

- Scenario: Demographic Identity Neutral
  Input   : "We attended an academic symposium on Muslim and Jewish history."
  Verdict : CLEAN (identity_hate: 2.0%, Counterfactual Fairness: PASSED)`);
      } else if (cmd === "!inspect") {
        const token = arg || "k1ll";
        let res: Response;
        try {
          res = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ comment: token }),
          });
        } catch {
          res = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ comment: token }),
          });
        }
        const data = await res.json();
        const s2 = data.syllabus_analysis?.module_2_word_level;
        const norm = s2?.adversarial_edit_distance?.[0];
        const wsd = data.syllabus_analysis?.module_4_semantic_analysis?.wordnet_lesk_wsd?.[0];

        setTerminalOutput((prev) => `${prev}\n
[TOKEN LEXICAL INSPECTION: '${token}']
  Normalized Form : '${norm?.normalized || token}'
  Edit Distance   : ${norm?.edit_distance ?? 0} (${norm?.method || "None"})
  Lemma           : '${s2?.morphology?.[0]?.lemma || token}'
  Porter Stem     : '${s2?.morphology?.[0]?.porter_stem || token}'
  Morphology Type : ${s2?.morphology?.[0]?.morphology_type || "N/A"}
  WordNet Synset  : ${wsd?.selected_synset || "N/A"} (${wsd?.sense_type || "neutral"})
  Gloss           : ${wsd?.gloss || "No dedicated entry in disambiguation dictionary"}`);
      } else {
        const text = arg || trimmed;
        let res: Response;
        try {
          res = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ comment: text }),
          });
        } catch {
          res = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ comment: text }),
          });
        }
        const data = await res.json();
        const maxScore = Math.max(
          data.toxic ?? 0,
          data.severe_toxic ?? 0,
          data.obscene ?? 0,
          data.threat ?? 0,
          data.insult ?? 0,
          data.identity_hate ?? 0
        );

        const actionTaken = maxScore >= 0.85 ? "AUTOBAN (PERMANENT SERVER BAN)" : (maxScore >= 0.70 ? "TIMEOUT (15-MINUTE MUTE)" : (maxScore >= 0.50 ? "WARNING_DELETION" : "PERMIT (CLEAN)"));

        if (cmd === "!analyze") {
          const preds = [
            `  toxic          [${"#".repeat(Math.floor((data.toxic ?? 0) * 20))}${"-".repeat(20 - Math.floor((data.toxic ?? 0) * 20))}] ${(Number(data.toxic) * 100).toFixed(1)}%`,
            `  severe_toxic   [${"#".repeat(Math.floor((data.severe_toxic ?? 0) * 20))}${"-".repeat(20 - Math.floor((data.severe_toxic ?? 0) * 20))}] ${(Number(data.severe_toxic) * 100).toFixed(1)}%`,
            `  obscene        [${"#".repeat(Math.floor((data.obscene ?? 0) * 20))}${"-".repeat(20 - Math.floor((data.obscene ?? 0) * 20))}] ${(Number(data.obscene) * 100).toFixed(1)}%`,
            `  threat         [${"#".repeat(Math.floor((data.threat ?? 0) * 20))}${"-".repeat(20 - Math.floor((data.threat ?? 0) * 20))}] ${(Number(data.threat) * 100).toFixed(1)}%`,
            `  insult         [${"#".repeat(Math.floor((data.insult ?? 0) * 20))}${"-".repeat(20 - Math.floor((data.insult ?? 0) * 20))}] ${(Number(data.insult) * 100).toFixed(1)}%`,
            `  identity_hate  [${"#".repeat(Math.floor((data.identity_hate ?? 0) * 20))}${"-".repeat(20 - Math.floor((data.identity_hate ?? 0) * 20))}] ${(Number(data.identity_hate) * 100).toFixed(1)}%`,
          ].join("\n");

          setTerminalOutput((prev) => `${prev}\n
[PREDICTION SCORES]
${preds}
Action Triggered : ${actionTaken}
Run !explain <text> to view the full linguistic step-by-step reasoning.`);
        } else {
          // !explain
          const s = data.syllabus_analysis;
          setTerminalOutput((prev) => `${prev}\n
================================================================
TOXIGUARD NLP PIPELINE REASONING REPORT
Course: 25PEC4CS1 Linguistic & Statistical Verification
================================================================
VERDICT      : ${maxScore >= 0.5 ? "FLAGGED AS TOXIC" : "CLEAN (PASS)"}
MAX SEVERITY : ${(maxScore * 100).toFixed(1)}%
ACTION TAKEN : ${actionTaken}
----------------------------------------------------------------
[STAGE 1: MATHEMATICAL & STATISTICAL PRELIMINARIES]
  Sentence Count : ${s?.module_1_preliminaries?.sentence_count ?? 1} | Token Count: ${s?.module_1_preliminaries?.token_count ?? 0}
  Distribution   : Mean=${s?.module_1_preliminaries?.probability_statistics?.mean_probability} | Var=${s?.module_1_preliminaries?.probability_statistics?.variance}

[STAGE 2: WORD-LEVEL NORMALIZATION & N-GRAM LANGUAGE MODEL]
  Adversarial Leetspeak Normalized: ${s?.module_2_word_level?.adversarial_edit_distance?.filter((x: any) => x.edit_distance > 0).map((x: any) => `'${x.original}'->'${x.normalized}'`).join(", ") || "None"}
  Toxic Corpus LM Perplexity : ${s?.module_2_word_level?.ngram_language_model?.toxic_corpus_perplexity}
  Safe Corpus LM Perplexity  : ${s?.module_2_word_level?.ngram_language_model?.safe_corpus_perplexity}

[STAGE 3: SYNTACTIC HMM + VITERBI POS TAGGING]
  Viterbi Optimal Path Log-Likelihood: ${s?.module_3_syntax_level?.best_path_log_prob}
  Trellis Path: ${s?.module_3_syntax_level?.tagged_tokens?.slice(0, 8).map((t: any) => `${t.token}/${t.pos_tag}`).join(" ") || ""}

[STAGE 4: SEMANTIC DISAMBIGUATION & VECTOR SPACE DISTANCE]
  WordNet Lesk Senses: ${s?.module_4_semantic_analysis?.wordnet_lesk_wsd?.map((w: any) => `'${w.word}' -> ${w.selected_synset} (${w.sense_type})`).join("; ") || "No polysemous triggers"}
  Top Cosine Match   : Ref '${s?.module_4_semantic_analysis?.tfidf_cosine_similarity?.[0]?.doc_id}' | Dist: ${s?.module_4_semantic_analysis?.tfidf_cosine_similarity?.[0]?.cosine_distance}

[STAGE 5: PRAGMATICS & DISCOURSE ANAPHORA RESOLUTION]
  Anaphora Binding   : ${s?.module_5_pragmatics_discourse?.anaphora_resolutions?.map((a: any) => `'${a.anaphor}' -> '${a.resolved_antecedent}'`).join("; ") || "None"}

[STAGE 6: EXPLAINABLE AI (XAI) ATTRIBUTION & ETHICAL AUDIT]
  Saliency Drivers   : ${s?.module_6_ethics_and_xai?.xai_token_attributions?.filter((x: any) => x.impact > 0).map((x: any) => `'${x.token}' (+${x.impact})`).join(", ") || "None"}
  Counterfactual Fair: ${s?.module_6_ethics_and_xai?.fairness_and_privacy?.demographic_parity_audit?.counterfactual_fairness_passed ? "PASSED" : "FLAGGED"}
================================================================`);
        }
      }
    } catch (err) {
      setTerminalOutput((prev) => `${prev}\n[ERROR] Failed to simulate command against API backend.`);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <section id="discord" className="py-12 border-t border-box-border">
      <Container>
        {/* Section Header */}
        <div className="space-y-2 mb-8">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700">
              Automated Moderation & Bot Integration
            </span>
            <span className="text-xs text-heading-3 font-mono">
              Discord API Gateway • Tiered Enforcement Matrix
            </span>
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-heading-1">
            Discord Moderation Bot & Auto-Ban System
          </h2>
          <p className="text-sm text-heading-3 max-w-3xl">
            Features an automated 3-tier enforcement matrix with **Auto-Ban for toxicity &ge; 85%**,
            timeout mutes for moderate offenses (70%&ndash;84%), channel health auditing, member infraction tracking,
            and complete 6-stage NLP reasoning reports delivered to user DMs and staff mod logs.
          </p>
        </div>

        {/* Tiered Policy Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-8 font-mono text-xs">
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 space-y-1">
            <div className="flex items-center justify-between font-bold">
              <span>TIER 3: AUTO-BAN</span>
              <span>&ge; 85.0%</span>
            </div>
            <p className="text-[11px] opacity-90">
              Immediate permanent server ban + DM explanation notice + audit log entry. Triggered by severe attacks or threats &ge; 85%.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 space-y-1">
            <div className="flex items-center justify-between font-bold">
              <span>TIER 2: AUTO-TIMEOUT</span>
              <span>70.0% - 84.9%</span>
            </div>
            <p className="text-[11px] opacity-90">
              15-minute native Discord member timeout + message deletion + reasoning report. Also triggered after 3 warnings.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-500/10 border border-slate-500/30 text-heading-2 space-y-1">
            <div className="flex items-center justify-between font-bold">
              <span>TIER 1: WARNING</span>
              <span>50.0% - 69.9%</span>
            </div>
            <p className="text-[11px] opacity-90">
              Message deletion + infraction logged in user history + stage-by-stage explanation posted to channel.
            </p>
          </div>
        </div>

        {/* Live Interactive Terminal Simulator */}
        <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 text-slate-200 shadow-xl space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-800 text-xs font-mono">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80 inline-block"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80 inline-block"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80 inline-block"></span>
              <span className="text-slate-400 font-bold ml-2">toxiguard-bot-console (.env Config Active)</span>
            </div>
            <span className="text-slate-500">discord.py 2.7.1 • Auto-Ban: &ge;85% • Timeout: &ge;70%</span>
          </div>

          {/* Quick preset command buttons */}
          <div className="space-y-1.5">
            <div className="text-[11px] font-mono text-slate-400">Click to run simulated command:</div>
            <div className="flex flex-wrap gap-2">
              {[
                "!explain Shut up you disgusting pig, go die in a ditch, I will murder you.",
                "!explain The guitarist was killing it on stage tonight",
                "!autoban 0.85",
                "!scan_channel",
                "!stats",
                "!test_cases",
                "!inspect k1ll",
              ].map((cmd, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setTerminalInput(cmd);
                    runCommandSimulation(cmd);
                  }}
                  className="px-2.5 py-1 rounded text-xs font-mono bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors cursor-pointer"
                >
                  {cmd.split(" ")[0]} {cmd.split(" ")[1]?.slice(0, 10)}...
                </button>
              ))}
            </div>
          </div>

          {/* Terminal Output */}
          <div className="p-4 rounded-xl bg-black/60 border border-slate-900 font-mono text-xs text-slate-300 max-h-96 overflow-y-auto whitespace-pre-wrap leading-relaxed select-text">
            {terminalOutput}
          </div>

          {/* Terminal Input Row */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              runCommandSimulation(terminalInput);
            }}
            className="flex items-center gap-3 pt-2"
          >
            <span className="font-mono text-teal-400 text-sm font-bold">discord-bot&gt;</span>
            <input
              type="text"
              value={terminalInput}
              onChange={(e) => setTerminalInput(e.target.value)}
              placeholder="Type bot command (e.g., !explain <text>, !autoban 0.85, !scan_channel)..."
              className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 font-mono text-xs text-slate-100 focus:outline-none focus:border-teal-500"
            />
            <button
              type="submit"
              disabled={isSimulating}
              className="px-4 py-2 rounded-lg font-mono text-xs font-semibold bg-teal-500 text-slate-950 hover:bg-teal-400 transition-colors cursor-pointer disabled:opacity-50"
            >
              Send Command
            </button>
          </form>
        </div>

        {/* Command Reference & Instructions Grid */}
        <div className="grid md:grid-cols-2 gap-6 mt-8">
          {/* Commands Table */}
          <div className="p-6 rounded-2xl bg-box-bg border border-box-border space-y-4">
            <h3 className="text-sm font-bold font-mono uppercase tracking-wider text-heading-1">
              Moderation & Explainer Commands
            </h3>
            <div className="space-y-3 font-mono text-xs">
              {COMMANDS.map((cmd, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-body border border-box-border space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-teal-400 font-bold">{cmd.prefix}</span>
                    <span className="text-[10px] text-heading-3">{cmd.slash}</span>
                  </div>
                  <p className="text-[11px] text-heading-3 leading-relaxed">{cmd.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Setup & Deployment Guide with .env */}
          <div className="p-6 rounded-2xl bg-box-bg border border-box-border space-y-4 font-mono text-xs">
            <h3 className="text-sm font-bold uppercase tracking-wider text-heading-1">
              Bot Environment & Launch (.env)
            </h3>
            <div className="space-y-3 text-heading-2">
              <div className="p-3 rounded-xl bg-body border border-box-border space-y-1.5">
                <div className="font-bold text-heading-1">1. Configure .env File:</div>
                <p className="text-[11px] text-heading-3">
                  Store your bot gateway credentials and moderation thresholds securely in <code className="text-heading-1">.env</code>:
                </p>
                <pre className="p-2.5 rounded bg-slate-950 text-slate-300 text-[11px] overflow-x-auto">
DISCORD_BOT_TOKEN="your_token_here"{"\n"}
AUTOBAN_THRESHOLD=0.85{"\n"}
TIMEOUT_THRESHOLD=0.70{"\n"}
TIMEOUT_DURATION_MINUTES=15
                </pre>
              </div>

              <div className="p-3 rounded-xl bg-body border border-box-border space-y-1.5">
                <div className="font-bold text-heading-1">2. Launch Live Bot:</div>
                <p className="text-[11px] text-heading-3">
                  Run the bot with uv or python; it automatically reads from <code className="text-heading-1">.env</code>:
                </p>
                <pre className="p-2.5 rounded bg-slate-950 text-slate-300 text-[11px] overflow-x-auto">
uv run python discord_bot/bot.py
                </pre>
              </div>

              <div className="p-3 rounded-xl bg-body border border-box-border space-y-1.5">
                <div className="font-bold text-heading-1">3. Required Gateway Intents:</div>
                <p className="text-[11px] text-heading-3">
                  Enable <code className="text-heading-1 font-bold">Message Content Intent</code> and{" "}
                  <code className="text-heading-1 font-bold">Server Members Intent</code> in Discord Dev Portal for autoban & timeout execution.
                </p>
              </div>
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
};
