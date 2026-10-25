import { useState } from "react";
import { Container } from "../shared/Container";

interface PipelineStagesProps {
  syllabus: any;
}

const STAGES = [
  {
    id: "stage1",
    num: "Stage 1",
    title: "Preliminaries & Priors",
    module: "Module 1",
    desc: "Mathematical Foundations, Tokenization & Bayesian Priors",
  },
  {
    id: "stage2",
    num: "Stage 2",
    title: "Word-Level & Morphology",
    module: "Module 2",
    desc: "Adversarial Normalization, Stemming & N-Gram Language Models",
  },
  {
    id: "stage3",
    num: "Stage 3",
    title: "Syntax & POS Tagging",
    module: "Module 3",
    desc: "Penn Treebank HMM Sequence Labeling & Viterbi Trellis Decoding",
  },
  {
    id: "stage4",
    num: "Stage 4",
    title: "Semantics & WordNet WSD",
    module: "Module 4",
    desc: "Simplified Lesk Disambiguation, Lexical Relations & Cosine Distance",
  },
  {
    id: "stage5",
    num: "Stage 5",
    title: "Pragmatics & Discourse",
    module: "Module 5",
    desc: "Hobbs' Syntactic Anaphora Resolution & Centering Theory Transitions",
  },
  {
    id: "stage6",
    num: "Stage 6",
    title: "Ethics, Privacy & XAI",
    module: "Module 6",
    desc: "Token Impact Attribution, PII Anonymization & Counterfactual Fairness",
  },
];

export const PipelineStages = ({ syllabus }: PipelineStagesProps) => {
  const [activeStage, setActiveStage] = useState<string>("stage2");

  if (!syllabus) {
    return (
      <section id="pipeline" className="py-12 border-t border-box-border">
        <Container>
          <div className="p-8 rounded-2xl bg-box-bg border border-box-border text-center space-y-2">
            <h3 className="text-base font-bold text-heading-1">
              Pipeline Stage Inspector Standby
            </h3>
            <p className="text-xs font-mono text-heading-3 max-w-md mx-auto">
              Execute an analysis in the console above to inspect live intermediate outputs
              for all 6 natural language processing syllabus modules.
            </p>
          </div>
        </Container>
      </section>
    );
  }

  const s1 = syllabus.module_1_preliminaries;
  const s2 = syllabus.module_2_word_level;
  const s3 = syllabus.module_3_syntax_level;
  const s4 = syllabus.module_4_semantic_analysis;
  const s5 = syllabus.module_5_pragmatics_discourse;
  const s6 = syllabus.module_6_ethics_and_xai;

  return (
    <section id="pipeline" className="py-12 border-t border-box-border">
      <Container>
        {/* Section Header */}
        <div className="space-y-2 mb-8">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700">
              Linguistic Pipeline Architecture
            </span>
            <span className="text-xs text-heading-3 font-mono">
              6-Stage Sequential Decomposition
            </span>
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-heading-1">
            25PEC4CS1 NLP Syllabus Pipeline Deep-Dive
          </h2>
          <p className="text-sm text-heading-3 max-w-3xl">
            Each stage transforms raw text into structured mathematical, syntactic, and semantic representations
            to detect abuse while eliminating false positives from polysemous metaphors and adversarial evasions.
          </p>
        </div>

        {/* Stage Selector Tabs */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2 mb-8">
          {STAGES.map((s) => {
            const isActive = activeStage === s.id;
            return (
              <button
                key={s.id}
                type="button"
                onClick={() => setActiveStage(s.id)}
                className={`p-3 rounded-xl text-left border transition-all cursor-pointer flex flex-col justify-between ${
                  isActive
                    ? "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900 border-slate-700 dark:border-slate-300 shadow-sm"
                    : "bg-box-bg text-heading-2 border-box-border hover:bg-slate-500/10"
                }`}
              >
                <div>
                  <div className="text-[10px] font-mono uppercase tracking-wider opacity-75">
                    {s.num} • {s.module}
                  </div>
                  <div className="text-xs font-bold mt-1 line-clamp-1">{s.title}</div>
                </div>
                <div className="text-[10px] opacity-75 mt-2 line-clamp-1 font-mono">
                  {s.desc}
                </div>
              </button>
            );
          })}
        </div>

        {/* Stage Content Panel */}
        <div className="p-6 rounded-2xl bg-box-bg border border-box-border space-y-6">
          {/* ===================================================================== */}
          {/* STAGE 1: PRELIMINARIES & PRIORS                                       */}
          {/* ===================================================================== */}
          {activeStage === "stage1" && s1 && (
            <div className="space-y-6">
              <div className="space-y-1">
                <span className="text-xs font-mono text-teal-400 font-semibold uppercase">
                  Stage 1: Mathematical Foundations & Corpus Statistics (Module 1)
                </span>
                <h3 className="text-lg font-bold text-heading-1">
                  Corpus Distribution Modeling & Bayesian Class Priors
                </h3>
                <p className="text-xs text-heading-3 leading-relaxed">
                  Calculates sample statistics (mean probability, variance, standard deviation) across multi-label classes.
                  Integrates Jigsaw Kaggle training corpus priors to adjust posterior distributions and account for class imbalance.
                </p>
              </div>

              {/* Sequential Execution Chain */}
              <div className="p-4 rounded-xl bg-body border border-box-border">
                <div className="text-xs font-mono font-semibold text-heading-1 mb-2">
                  Pipeline Execution Stages:
                </div>
                <div className="flex flex-wrap gap-2">
                  {s1.stages_executed?.map((st: string, idx: number) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-md text-xs font-mono bg-box-bg border border-box-border text-heading-2"
                    >
                      {st}
                    </span>
                  ))}
                </div>
              </div>

              {/* Kaggle Class Priors Table */}
              <div className="space-y-2">
                <div className="text-xs font-mono font-semibold text-heading-1">
                  Jigsaw Kaggle Dataset Baseline Class Priors:
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left font-mono text-xs border border-box-border">
                    <thead className="bg-body border-b border-box-border text-heading-3">
                      <tr>
                        <th className="p-2.5">Category</th>
                        <th className="p-2.5">Prior P(C)</th>
                        <th className="p-2.5">Distribution Proportion</th>
                        <th className="p-2.5">Imbalance Factor</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-box-border">
                      {Object.entries(s1.jigsaw_class_priors || {}).map(([k, v]: [string, any]) => (
                        <tr key={k} className="hover:bg-slate-500/5">
                          <td className="p-2.5 font-semibold text-heading-1 capitalize">{k.replace("_", " ")}</td>
                          <td className="p-2.5 text-teal-400">{v}</td>
                          <td className="p-2.5">{(Number(v) * 100).toFixed(2)}%</td>
                          <td className="p-2.5 text-heading-3">
                            {Number(v) < 0.02 ? "Extreme Rare (1:100+)" : "Moderate (1:10 - 1:20)"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ===================================================================== */}
          {/* STAGE 2: WORD-LEVEL & MORPHOLOGY                                      */}
          {/* ===================================================================== */}
          {activeStage === "stage2" && s2 && (
            <div className="space-y-6">
              <div className="space-y-1">
                <span className="text-xs font-mono text-teal-400 font-semibold uppercase">
                  Stage 2: Morphology, Stemming & Edit Distance (Module 2)
                </span>
                <h3 className="text-lg font-bold text-heading-1">
                  Adversarial Normalization & N-Gram Language Model Perplexity
                </h3>
                <p className="text-xs text-heading-3 leading-relaxed">
                  Defeats intentional leetspeak substitutions (e.g. <code className="text-heading-2">k1ll</code>, <code className="text-heading-2">id1ot</code>) via Levenshtein minimum edit distance.
                  Extracts root lemmas, Porter stems, and analyzes sentence perplexity using Laplace (add-1) smoothing across toxic vs safe bigram language models.
                </p>
              </div>

              {/* Bigram LM Perplexity Comparison */}
              {s2.ngram_language_model && (
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-body border border-box-border space-y-1">
                    <div className="text-xs font-mono text-heading-3">Toxic Language Model Perplexity</div>
                    <div className="text-2xl font-bold font-mono text-heading-1">
                      {s2.ngram_language_model.toxic_corpus_perplexity}
                    </div>
                    <p className="text-[11px] text-heading-3">
                      Laplace Add-1 Smoothed. Lower perplexity indicates high alignment with toxic vocabulary patterns.
                    </p>
                  </div>
                  <div className="p-4 rounded-xl bg-body border border-box-border space-y-1">
                    <div className="text-xs font-mono text-heading-3">Safe Language Model Perplexity</div>
                    <div className="text-2xl font-bold font-mono text-heading-1">
                      {s2.ngram_language_model.safe_corpus_perplexity}
                    </div>
                    <p className="text-[11px] text-heading-3">
                      Laplace Add-1 Smoothed. Evaluated against clean conversational baseline corpus.
                    </p>
                  </div>
                </div>
              )}

              {/* Adversarial Normalization Table */}
              <div className="space-y-2">
                <div className="text-xs font-mono font-semibold text-heading-1">
                  Adversarial Normalization Table (Edit Distance & Leetspeak):
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left font-mono text-xs border border-box-border">
                    <thead className="bg-body border-b border-box-border text-heading-3">
                      <tr>
                        <th className="p-2.5">Original Token</th>
                        <th className="p-2.5">Normalized Canonical</th>
                        <th className="p-2.5">Edit Dist (Levenshtein)</th>
                        <th className="p-2.5">Lexicon Matched</th>
                        <th className="p-2.5">Normalization Algorithm</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-box-border">
                      {s2.adversarial_edit_distance?.map((row: any, idx: number) => (
                        <tr key={idx} className="hover:bg-slate-500/5">
                          <td className="p-2.5 font-semibold text-heading-1">{row.original}</td>
                          <td className="p-2.5 text-teal-400 font-semibold">{row.normalized}</td>
                          <td className="p-2.5">{row.edit_distance}</td>
                          <td className="p-2.5">
                            {row.matched_lexicon ? (
                              <span className="px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-400 text-[10px]">
                                TRUE
                              </span>
                            ) : (
                              <span className="text-heading-3 text-[10px]">FALSE</span>
                            )}
                          </td>
                          <td className="p-2.5 text-heading-2">{row.method}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Morphology Decomposition Table */}
              {s2.morphology && s2.morphology.length > 0 && (
                <div className="space-y-2">
                  <div className="text-xs font-mono font-semibold text-heading-1">
                    Morphological Analysis & Stemming Breakdown:
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left font-mono text-xs border border-box-border">
                      <thead className="bg-body border-b border-box-border text-heading-3">
                        <tr>
                          <th className="p-2.5">Surface Form</th>
                          <th className="p-2.5">Lemma</th>
                          <th className="p-2.5">Porter Stem</th>
                          <th className="p-2.5">Morphology Classification</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-box-border">
                        {s2.morphology.map((m: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-500/5">
                            <td className="p-2.5 font-semibold text-heading-1">{m.surface_form}</td>
                            <td className="p-2.5 text-teal-400">{m.lemma}</td>
                            <td className="p-2.5">{m.porter_stem}</td>
                            <td className="p-2.5 text-heading-2">{m.morphology_type}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ===================================================================== */}
          {/* STAGE 3: SYNTAX & HMM POS TAGGING                                     */}
          {/* ===================================================================== */}
          {activeStage === "stage3" && s3 && (
            <div className="space-y-6">
              <div className="space-y-1">
                <span className="text-xs font-mono text-teal-400 font-semibold uppercase">
                  Stage 3: Syntax Analysis & Sequence Labeling (Module 3)
                </span>
                <h3 className="text-lg font-bold text-heading-1">
                  Penn Treebank HMM POS Tagging & Viterbi Trellis Path
                </h3>
                <p className="text-xs text-heading-3 leading-relaxed">
                  Part-of-Speech tagging models transition probabilities P(t_i | t_i-1) and emission probabilities P(w_i | t_i).
                  Dynamic programming via the Viterbi algorithm identifies the globally optimal state sequence through the trellis.
                </p>
              </div>

              {/* Viterbi Metrics */}
              <div className="p-4 rounded-xl bg-body border border-box-border flex flex-wrap items-center justify-between gap-4 font-mono text-xs">
                <div>
                  <span className="text-heading-3">Optimal Trellis Path Log-Likelihood: </span>
                  <strong className="text-teal-400 text-sm">{s3.best_path_log_prob ?? "N/A"}</strong>
                </div>
                <div className="text-heading-3">
                  Decoding: Viterbi Trellis (State Transitions + Emissions)
                </div>
              </div>

              {/* POS Tagged Token Grid */}
              <div className="space-y-2">
                <div className="text-xs font-mono font-semibold text-heading-1">
                  Tagged Token Sequence:
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
                  {s3.tagged_tokens?.map((t: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-body border border-box-border font-mono flex flex-col justify-between"
                    >
                      <div className="text-sm font-bold text-heading-1 break-words">{t.token}</div>
                      <div className="mt-2 flex items-center justify-between">
                        <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-800 text-slate-100 border border-slate-700">
                          {t.pos_tag}
                        </span>
                      </div>
                      <div className="text-[10px] text-heading-3 mt-1.5 line-clamp-1" title={t.description}>
                        {t.description}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ===================================================================== */}
          {/* STAGE 4: SEMANTICS & WORDNET WSD                                      */}
          {/* ===================================================================== */}
          {activeStage === "stage4" && s4 && (
            <div className="space-y-6">
              <div className="space-y-1">
                <span className="text-xs font-mono text-teal-400 font-semibold uppercase">
                  Stage 4: Semantic Analysis & Word Sense Disambiguation (Module 4)
                </span>
                <h3 className="text-lg font-bold text-heading-1">
                  WordNet Simplified Lesk WSD & TF-IDF Cosine Distance
                </h3>
                <p className="text-xs text-heading-3 leading-relaxed">
                  Crucial for polysemy: disambiguates words like <code className="text-heading-2">killing</code> in praise ("killing it on stage")
                  versus lethal threats. Computes TF-IDF vector space embeddings with Cosine Similarity ($S_c$) and Distance ($D_c = 1 - S_c$).
                </p>
              </div>

              {/* WordNet WSD Cards */}
              <div className="space-y-3">
                <div className="text-xs font-mono font-semibold text-heading-1">
                  WordNet Simplified Lesk WSD Sense Disambiguation:
                </div>
                {s4.wordnet_lesk_wsd && s4.wordnet_lesk_wsd.length > 0 ? (
                  <div className="space-y-3">
                    {s4.wordnet_lesk_wsd.map((w: any, idx: number) => (
                      <div key={idx} className="p-4 rounded-xl bg-body border border-box-border font-mono text-xs space-y-2">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-sm text-heading-1">"{w.word}"</span>
                            <span className="text-heading-3">→</span>
                            <span className="text-teal-400 font-bold">{w.selected_synset}</span>
                          </div>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold ${
                              w.sense_type.includes("toxic")
                                ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                                : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                            }`}
                          >
                            {w.sense_type}
                          </span>
                        </div>
                        <p className="text-heading-2 text-[11px] leading-relaxed">
                          <strong>Gloss:</strong> {w.gloss}
                        </p>
                        <div className="flex flex-wrap gap-4 text-[11px] text-heading-3 pt-1 border-t border-box-border/50">
                          <span>
                            <strong>Synonyms:</strong> {w.lexical_relations?.synonyms?.join(", ") || "None"}
                          </span>
                          <span>
                            <strong>Antonyms:</strong> {w.lexical_relations?.antonyms?.join(", ") || "None"}
                          </span>
                          <span>
                            <strong>Hypernyms:</strong> {w.lexical_relations?.hypernyms?.join(", ") || "None"}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 rounded-xl bg-body border border-box-border text-xs font-mono text-heading-3">
                    No polysemous trigger words requiring WordNet WSD sense selection detected in current input.
                  </div>
                )}
              </div>

              {/* TF-IDF Cosine Similarity & Distance Table */}
              {s4.tfidf_cosine_similarity && (
                <div className="space-y-2">
                  <div className="text-xs font-mono font-semibold text-heading-1">
                    TF-IDF Vector Space Model — Cosine Similarity & Distance:
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left font-mono text-xs border border-box-border">
                      <thead className="bg-body border-b border-box-border text-heading-3">
                        <tr>
                          <th className="p-2.5">Reference Document</th>
                          <th className="p-2.5">Category</th>
                          <th className="p-2.5">Cosine Similarity (S_c)</th>
                          <th className="p-2.5">Cosine Distance (D_c = 1 - S_c)</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-box-border">
                        {s4.tfidf_cosine_similarity.slice(0, 5).map((c: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-500/5">
                            <td className="p-2.5 font-semibold text-heading-1">{c.doc_id}</td>
                            <td className="p-2.5 text-heading-2 capitalize">{c.category}</td>
                            <td className="p-2.5 text-teal-400 font-semibold">{c.cosine_similarity}</td>
                            <td className="p-2.5 text-heading-3">{c.cosine_distance}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ===================================================================== */}
          {/* STAGE 5: PRAGMATICS & ANAPHORA                                        */}
          {/* ===================================================================== */}
          {activeStage === "stage5" && s5 && (
            <div className="space-y-6">
              <div className="space-y-1">
                <span className="text-xs font-mono text-teal-400 font-semibold uppercase">
                  Stage 5: Pragmatics & Discourse Processing (Module 5)
                </span>
                <h3 className="text-lg font-bold text-heading-1">
                  Hobbs' Algorithm Anaphora Resolution & Centering Theory Transitions
                </h3>
                <p className="text-xs text-heading-3 leading-relaxed">
                  Resolves pronouns (he, she, they, you, it) back to their contextual antecedent entities.
                  Centering Theory tracks local discourse salience using Forward-Looking Centers ($C_f$),
                  Preferred Center ($C_p$), Backward-Looking Center ($C_b$), and transition classification (Continue, Retain, Shift).
                </p>
              </div>

              {/* Hobbs Anaphora Table */}
              <div className="space-y-2">
                <div className="text-xs font-mono font-semibold text-heading-1">
                  Hobbs' Algorithm Pronominal Anaphora Resolution:
                </div>
                {s5.anaphora_resolutions && s5.anaphora_resolutions.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left font-mono text-xs border border-box-border">
                      <thead className="bg-body border-b border-box-border text-heading-3">
                        <tr>
                          <th className="p-2.5">Anaphor (Pronoun)</th>
                          <th className="p-2.5">Sentence Index</th>
                          <th className="p-2.5">Resolved Antecedent</th>
                          <th className="p-2.5">Algorithm</th>
                          <th className="p-2.5">Agreement Constraints</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-box-border">
                        {s5.anaphora_resolutions.map((a: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-500/5">
                            <td className="p-2.5 font-bold text-heading-1">"{a.anaphor}"</td>
                            <td className="p-2.5">S{a.sentence}</td>
                            <td className="p-2.5 text-teal-400 font-bold">{a.resolved_antecedent}</td>
                            <td className="p-2.5 text-heading-2">{a.algorithm}</td>
                            <td className="p-2.5 text-heading-3">{a.constraints_satisfied}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="p-4 rounded-xl bg-body border border-box-border text-xs font-mono text-heading-3">
                    No pronominal anaphors requiring cross-sentence antecedent binding detected in input.
                  </div>
                )}
              </div>

              {/* Centering Theory Transitions */}
              {s5.centering_table && (
                <div className="space-y-2">
                  <div className="text-xs font-mono font-semibold text-heading-1">
                    Centering Theory Discourse State Transitions:
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left font-mono text-xs border border-box-border">
                      <thead className="bg-body border-b border-box-border text-heading-3">
                        <tr>
                          <th className="p-2.5">Utterance</th>
                          <th className="p-2.5">Forward Centers (Cf)</th>
                          <th className="p-2.5">Preferred Center (Cp)</th>
                          <th className="p-2.5">Backward Center (Cb)</th>
                          <th className="p-2.5">Transition Classification</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-box-border">
                        {s5.centering_table.map((ct: any, idx: number) => (
                          <tr key={idx} className="hover:bg-slate-500/5">
                            <td className="p-2.5 font-bold text-heading-1">{ct.utterance}</td>
                            <td className="p-2.5">{ct.Cf_forward_centers?.join(", ") || "None"}</td>
                            <td className="p-2.5 text-teal-400">{ct.Cp_preferred_center}</td>
                            <td className="p-2.5 text-heading-2">{ct.Cb_backward_center}</td>
                            <td className="p-2.5 font-semibold text-heading-1">{ct.transition}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ===================================================================== */}
          {/* STAGE 6: ETHICS, PRIVACY & XAI                                        */}
          {/* ===================================================================== */}
          {activeStage === "stage6" && s6 && (
            <div className="space-y-6">
              <div className="space-y-1">
                <span className="text-xs font-mono text-teal-400 font-semibold uppercase">
                  Stage 6: Governance, Fairness & Explainability (Module 6)
                </span>
                <h3 className="text-lg font-bold text-heading-1">
                  Explainable AI (XAI) Token Attribution & Privacy Compliance
                </h3>
                <p className="text-xs text-heading-3 leading-relaxed">
                  Provides transparency by attributing positive/negative saliency weights to each token.
                  Conducts counterfactual debiasing to ensure mentions of protected demographic identity groups do not trigger false-positive identity hate.
                </p>
              </div>

              {/* XAI Token Impact Heatmap / Strip */}
              <div className="space-y-2">
                <div className="text-xs font-mono font-semibold text-heading-1">
                  Token Impact Attribution (Saliency Weights):
                </div>
                <div className="flex flex-wrap gap-2 p-4 rounded-xl bg-body border border-box-border">
                  {s6.xai_token_attributions?.map((item: any, idx: number) => {
                    const isToxic = item.impact > 0;
                    const isBenign = item.impact < 0;

                    return (
                      <span
                        key={idx}
                        title={`${item.reason} | Categories: ${item.categories?.join(", ") || "None"}`}
                        className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium border ${
                          isToxic
                            ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                            : isBenign
                            ? "bg-teal-500/20 text-teal-300 border-teal-500/40"
                            : "bg-box-bg text-heading-2 border-box-border"
                        }`}
                      >
                        {item.token}{" "}
                        {item.impact !== 0 && (
                          <span className="text-[10px] opacity-80">
                            ({item.impact > 0 ? `+${item.impact}` : item.impact})
                          </span>
                        )}
                      </span>
                    );
                  })}
                </div>
              </div>

              {/* Privacy & Fairness Summary */}
              {s6.fairness_and_privacy && (
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-body border border-box-border space-y-2 font-mono text-xs">
                    <div className="font-bold text-heading-1 uppercase text-[11px]">
                      Data Privacy & PII Redaction Audit:
                    </div>
                    <div>
                      <span className="text-heading-3">Anonymized Preview: </span>
                      <code className="text-teal-400 break-all">
                        {s6.fairness_and_privacy.privacy_compliance?.anonymized_preview || "None"}
                      </code>
                    </div>
                    <div className="text-heading-3">
                      Redacted Items: {s6.fairness_and_privacy.privacy_compliance?.pii_count_redacted ?? 0}
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-body border border-box-border space-y-2 font-mono text-xs">
                    <div className="font-bold text-heading-1 uppercase text-[11px]">
                      Demographic Parity & Counterfactual Fairness:
                    </div>
                    <div>
                      <span className="text-heading-3">Counterfactual Check: </span>
                      <strong className="text-emerald-400">
                        {s6.fairness_and_privacy.demographic_parity_audit?.counterfactual_fairness_passed
                          ? "PASSED (NO FALSE IDENTITY BIAS)"
                          : "FLAGGED"}
                      </strong>
                    </div>
                    <p className="text-[11px] text-heading-2 leading-relaxed">
                      {s6.fairness_and_privacy.demographic_parity_audit?.bias_mitigation_note}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </Container>
    </section>
  );
};
