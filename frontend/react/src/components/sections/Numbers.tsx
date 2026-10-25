import { useState } from "react";
import { Container } from "../shared/Container";

const TOXICITY_LABELS = [
  "toxic",
  "severe_toxic",
  "obscene",
  "threat",
  "insult",
  "identity_hate",
];

export const Numbers = ({ predictions }: { predictions: any }) => {
  const [activeTab, setActiveTab] = useState<string>("mod2");

  const colors: Record<string, string> = {
    toxic: "text-rose-500",
    obscene: "text-purple-500",
    threat: "text-amber-500",
    insult: "text-teal-500",
    severe_toxic: "text-red-600",
    identity_hate: "text-fuchsia-500",
  };

  const syllabus = predictions?.syllabus_analysis;

  return (
    <section className="relative mt-12 md:mt-16 space-y-10">
      <Container className="flex flex-col items-center">
        {/* Core 6 Toxicity Scores */}
        <div
          className="w-full max-w-5xl p-6 sm:py-8 rounded-3xl bg-box-bg
                      border border-box-border shadow-lg shadow-box-shadow md:divide-x divide-box-border
                      grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-y-6"
        >
          {TOXICITY_LABELS.map((label) => {
            const rawVal = Number(predictions?.[label] ?? 0);
            return (
              <div key={label} className="text-center px-3">
                <h2 className="font-bold text-xl sm:text-2xl text-heading-1 flex justify-center items-center gap-1.5">
                  <span>{(rawVal * 100).toFixed(1)}%</span>
                  <span className={`text-sm ${colors[label]}`}>●</span>
                </h2>
                <p className="mt-1 text-sm text-heading-3 capitalize font-medium">
                  {label.replace("_", " ")}
                </p>
              </div>
            );
          })}
        </div>

        {/* 25PEC4CS1 Syllabus Deep-Dive Tabs */}
        {syllabus && (
          <div className="w-full max-w-5xl mt-8 p-6 rounded-3xl bg-box-bg border border-box-border shadow-lg text-heading-2">
            <div className="flex flex-wrap items-center justify-between gap-2 pb-4 border-b border-box-border">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider px-3 py-1 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
                  25PEC4CS1 Syllabus Pipeline Breakdown
                </span>
                <h3 className="text-lg font-bold text-heading-1 mt-2">
                  Multi-Stage Linguistic & Statistical Inspector
                </h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {[
                  { id: "mod2", label: "M2: Word & N-Grams" },
                  { id: "mod3", label: "M3: HMM Viterbi POS" },
                  { id: "mod4", label: "M4: WordNet WSD & Cosine" },
                  { id: "mod5", label: "M5: Hobbs Anaphora" },
                  { id: "mod6", label: "M6: XAI & Fairness" },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                      activeTab === tab.id
                        ? "bg-gradient-to-r from-purple-600 to-teal-500 text-white"
                        : "bg-body border border-box-border text-heading-3"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-5 text-sm">
              {activeTab === "mod2" && (
                <div className="space-y-3">
                  <p>
                    <strong>Laplace Smoothed Bigram Perplexity:</strong> Toxic LM ={" "}
                    <code className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-300">
                      {syllabus.module_2_word_level.ngram_language_model.toxic_corpus_perplexity}
                    </code>{" "}
                    | Safe LM ={" "}
                    <code className="px-2 py-0.5 rounded bg-teal-500/10 text-teal-300">
                      {syllabus.module_2_word_level.ngram_language_model.safe_corpus_perplexity}
                    </code>
                  </p>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="border-b border-box-border text-purple-400">
                          <th className="py-2">Surface Token</th>
                          <th className="py-2">De-obfuscated (Edit Dist)</th>
                          <th className="py-2">Lemma</th>
                          <th className="py-2">Porter Stem</th>
                          <th className="py-2">Morphology Class</th>
                        </tr>
                      </thead>
                      <tbody>
                        {syllabus.module_2_word_level.morphology.map((m: any, idx: number) => {
                          const adv = syllabus.module_2_word_level.adversarial_edit_distance[idx];
                          return (
                            <tr key={idx} className="border-b border-box-border/40">
                              <td className="py-1.5 font-semibold">{m.surface_form}</td>
                              <td className="py-1.5">
                                {adv?.normalized} <span className="opacity-70">({adv?.method})</span>
                              </td>
                              <td className="py-1.5">{m.lemma}</td>
                              <td className="py-1.5">{m.porter_stem}</td>
                              <td className="py-1.5">{m.morphology_type}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {activeTab === "mod3" && (
                <div className="space-y-3">
                  <p>
                    <strong>Viterbi Optimal Path Log-Probability:</strong>{" "}
                    <code>{syllabus.module_3_syntax_level.best_path_log_prob}</code>
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {syllabus.module_3_syntax_level.tagged_tokens.map((t: any, idx: number) => (
                      <div
                        key={idx}
                        title={t.description}
                        className="px-3 py-2 rounded-xl border border-box-border bg-body flex flex-col items-center"
                      >
                        <span className="font-semibold text-heading-1">{t.token}</span>
                        <span className="text-xs font-bold text-teal-400">{t.pos_tag}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === "mod4" && (
                <div className="space-y-4">
                  <div>
                    <h4 className="font-bold text-heading-1 mb-2">
                      WordNet Synsets & Lesk Word Sense Disambiguation (Mod 4.1, 4.2, 4.4)
                    </h4>
                    {syllabus.module_4_semantic_analysis.wordnet_lesk_wsd.length > 0 ? (
                      syllabus.module_4_semantic_analysis.wordnet_lesk_wsd.map((w: any, i: number) => (
                        <div key={i} className="p-3 rounded-xl bg-body border border-box-border mb-2">
                          <div className="font-semibold text-teal-400">
                            Token "{w.word}" → Synset: {w.selected_synset} ({w.sense_type})
                          </div>
                          <div className="text-xs mt-1">Gloss: {w.gloss}</div>
                          <div className="text-xs mt-1 opacity-80">
                            Synonyms: {w.lexical_relations.synonyms.join(", ")} | Antonyms:{" "}
                            {w.lexical_relations.antonyms.join(", ")} | Hypernyms:{" "}
                            {w.lexical_relations.hypernyms.join(", ")}
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs opacity-75">No ambiguous polysemous trigger tokens detected.</p>
                    )}
                  </div>
                  <div>
                    <h4 className="font-bold text-heading-1 mb-2">
                      TF-IDF Cosine Similarity & Distance (Mod 4.3)
                    </h4>
                    <div className="grid sm:grid-cols-2 gap-2">
                      {syllabus.module_4_semantic_analysis.tfidf_cosine_similarity
                        .slice(0, 4)
                        .map((c: any, idx: number) => (
                          <div key={idx} className="p-2.5 rounded-xl bg-body border border-box-border text-xs">
                            <div className="font-semibold">
                              {c.doc_id} ({c.category})
                            </div>
                            <div className="text-teal-400 mt-1">
                              Cosine Sim: {c.cosine_similarity} | Cosine Dist: {c.cosine_distance}
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "mod5" && (
                <div className="space-y-3">
                  <h4 className="font-bold text-heading-1">
                    Hobbs & Centering Anaphora Resolution (Mod 5.1)
                  </h4>
                  {syllabus.module_5_pragmatics_discourse.anaphora_resolutions.length > 0 ? (
                    <div className="space-y-2">
                      {syllabus.module_5_pragmatics_discourse.anaphora_resolutions.map(
                        (a: any, idx: number) => (
                          <div key={idx} className="p-2.5 rounded-xl bg-body border border-box-border text-xs">
                            Pronoun <strong>"{a.anaphor}"</strong> (Sentence {a.sentence}) → Resolved Antecedent:{" "}
                            <span className="text-teal-400 font-semibold">{a.resolved_antecedent}</span>{" "}
                            <span className="opacity-75">
                              [{a.algorithm} | {a.constraints_satisfied}]
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  ) : (
                    <p className="text-xs opacity-75">No pronouns requiring anaphora resolution in this comment.</p>
                  )}
                </div>
              )}

              {activeTab === "mod6" && (
                <div className="space-y-3">
                  <h4 className="font-bold text-heading-1">
                    Explainable AI (XAI) Token Attribution & Privacy Audit (Mod 6.2)
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {syllabus.module_6_ethics_and_xai.xai_token_attributions.map(
                      (item: any, idx: number) => (
                        <span
                          key={idx}
                          title={item.reason}
                          className={`px-2.5 py-1 rounded-lg text-xs font-medium ${
                            item.impact > 0
                              ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                              : item.impact < 0
                              ? "bg-teal-500/20 text-teal-300 border border-teal-500/40"
                              : "bg-body border border-box-border"
                          }`}
                        >
                          {item.token} {item.impact !== 0 ? `(${item.impact > 0 ? "+" : ""}${item.impact})` : ""}
                        </span>
                      )
                    )}
                  </div>
                  <p className="text-xs mt-2">
                    <strong>Anonymized Text Preview:</strong>{" "}
                    <code>
                      {syllabus.module_6_ethics_and_xai.fairness_and_privacy.privacy_compliance.anonymized_preview}
                    </code>
                  </p>
                  <p className="text-xs">
                    <strong>Fairness Audit:</strong>{" "}
                    {syllabus.module_6_ethics_and_xai.fairness_and_privacy.demographic_parity_audit.bias_mitigation_note}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </Container>
    </section>
  );
};
