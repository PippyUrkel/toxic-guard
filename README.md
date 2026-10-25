# ToxiGuard — Multi-Level Toxic Comment Detection & NLP Pipeline Platform

### Course: Natural Language Processing (25PEC4CS1)
**Department of Computer Engineering • Fr. Conceicao Rodrigues College of Engineering (CRCE), Bandra, Mumbai**

---

## Table of Contents

1. [Project Description](#project-description)
2. [Syllabus Topic Coverage](#syllabus-topic-coverage)
3. [System Architecture](#system-architecture)
4. [Project Structure](#project-structure)
5. [Detailed Working of the 6-Stage NLP Pipeline](#detailed-working-of-the-6-stage-nlp-pipeline)
6. [Discord Moderation Bot & Commands](#discord-moderation-bot--commands)
7. [Unified Web Platform](#unified-web-platform)
8. [Setup & Quickstart (with `uv`)](#setup--quickstart-with-uv)
9. [Technologies Used](#technologies-used)
10. [Ethical Considerations & Governance](#ethical-considerations--governance)

---

## Project Description

**ToxiGuard** is a multi-label toxicity classification platform and pedagogical Natural Language Processing engine developed for the **25PEC4CS1** curriculum. It bridges classical statistical NLP, knowledge-based linguistic methods, and deep bidirectional sequence models (BiLSTM) to detect toxicity across six distinct categories:

1. `toxic` — General offensive, abusive, or hostile language.
2. `severe_toxic` — Extremely aggressive, vitriolic, or dangerous attacks.
3. `obscene` — Vulgar, crude, or sexually explicit profanity.
4. `threat` — Explicit or implied declarations of intent to inflict harm.
5. `insult` — Demeaning, mocking, or derogatory remarks directed at an individual.
6. `identity_hate` — Prejudiced attacks targeting religion, race, gender, nationality, or sexual orientation.

Beyond binary filtering, ToxiGuard provides full **linguistic interpretability**: resolving adversarial obfuscations (leetspeak), tagging syntactic structures via HMM Viterbi decoding, disambiguating metaphorical versus harmful polysemy using WordNet WSD, tracking discourse referents using Hobbs' algorithm and Centering Theory, and providing token-level saliency attribution (XAI).

---

## Syllabus Topic Coverage

| Syllabus Topic | How ToxiGuard Implements It |
| :--- | :--- |
| **Module 1: Preliminaries & Stats** | Empirical probability modeling, sample Mean ($\mu$), Variance ($\sigma^2$), Standard Deviation ($\sigma$), and Bayesian class priors from the Jigsaw dataset. |
| **Module 2: Word-Level & Morphology** | Levenshtein minimum edit distance and leetspeak character decoding. Porter Stemmer, inflectional/derivational morphology classification. Laplace-smoothed Bigram Language Model perplexity evaluation against Toxic vs. Safe corpora. Pointwise Mutual Information (PMI) collocations. |
| **Module 3: Syntax Analysis** | Penn Treebank POS tagging implemented with Hidden Markov Models (HMM) and Viterbi dynamic programming trellis decoding to compute optimal syntactic state sequences and log-likelihoods. |
| **Module 4: Semantic Analysis** | Word Sense Disambiguation via WordNet Simplified Lesk algorithm, distinguishing metaphorical praise ("killing it on stage") from lethal threats. TF-IDF Vector Space Model (VSM) with Cosine Similarity and Cosine Distance ($D_c = 1 - S_c$). |
| **Module 5: Pragmatics & Discourse** | Cross-sentence pronominal anaphora resolution via Hobbs' Syntactic Algorithm. Centering Theory tracking Forward-Looking Centers ($C_f$), Preferred Center ($C_p$), Backward-Looking Center ($C_b$), and transition state classifications (Continue, Retain, Shift). |
| **Module 6: Ethics, Privacy & XAI** | Token attribution saliency weights, automated PII redaction (emails, phone numbers, IP addresses), and counterfactual fairness auditing ensuring protected demographic identity terms do not trigger false-positive identity hate. |

---

## System Architecture

```
[Raw User Text / Document Upload]
              |
              v
[Stage 1: Lexical Ingestion & Statistical Preliminaries]
              |
              v
[Stage 2: Adversarial Normalization, Stemming & N-Gram LM]
              |
              v
[Stage 3: Syntactic Penn Treebank HMM + Viterbi POS Tagging]
              |
              v
[Stage 4: Semantic WordNet Lesk WSD & TF-IDF Cosine Distance]
              |
              v
[Stage 5: Pragmatic Hobbs Anaphora & Centering Discourse]
              |
              v
[Multi-Label Ensemble: BiLSTM Neural Classifier + Rule/WSD Bayes]
              |
              v
[Stage 6: Governance: PII Redaction, Demographic Parity & XAI]
              |
        +-----+-----+
        |           |
        v           v
 [Unified Web UI] [Discord Bot]
  (Port 5000/5173) (discord.py)
```

---

## Project Structure

```
toxicity_model/
├── pyproject.toml              # Project metadata & uv dependencies (discord.py, Flask, etc.)
├── uv.lock                     # Deterministic dependency lockfile
├── start.py                    # Unified one-command launcher
├── run.sh                      # Shell launch script
├── run.bat                     # Windows batch launch script
├── .gitignore                  # Git ignore rules
├── comment.ipynb               # Model training & EDA Jupyter notebook
│
├── discord_bot/                # Discord Bot Integration
│   ├── __init__.py
│   ├── bot.py                  # Bot gateway listener, commands & offline CLI simulator
│   └── README.md               # Discord developer portal setup & bot guide
│
├── toxicity_app/               # Flask Application & NLP Engine
│   ├── __init__.py
│   ├── app.py                  # REST API (/predict, /api/health) & unified static server
│   ├── nlp_pipeline.py         # Complete 6-module NLP implementation
│   ├── static/
│   │   └── style.css           # Clean, non-AI dark stylesheet for fallback view
│   └── templates/
│       └── index.html          # Clean technical template view (?classic=1)
│
└── frontend/react/             # Unified Web Interface (React + Vite + Tailwind v4)
    ├── package.json
    ├── vite.config.ts          # Vite configuration with proxy to Flask
    ├── index.html
    └── src/
        ├── App.tsx             # Root dashboard
        ├── main.tsx
        ├── index.css           # Modern, professional non-AI styling
        ├── store/ThemeStore.ts # Light/Dark theme persistence
        ├── utils/pdfReader.ts  # PDF text extraction utility
        └── components/
            ├── Layout.tsx
            ├── elements/
            │   ├── Navbar.tsx  # Header navigation & theme switch
            │   └── Footer.tsx  # Academic course credentials
            ├── sections/
            │   ├── PipelineConsole.tsx  # Input console, presets & 6-target metrics
            │   ├── PipelineStages.tsx   # Interactive 6-module syllabus inspector
            │   ├── DiscordSection.tsx   # Discord bot simulator & command reference
            │   └── ApiDocsSection.tsx   # REST API OpenAPI documentation
            └── shared/
                ├── Container.tsx
                └── Button.tsx
```

---

## Discord Moderation Bot & Commands

The WhatsApp and Chrome extensions have been replaced with a real-time **Discord Moderation Bot** built using the official Discord API (`discord.py`).

### Key Capabilities

1. **Automated Channel Moderation**:
   - Scans all messages in configured server channels.
   - Deletes messages exceeding toxicity thresholds (default: 50%).
   - Notifies the channel with the exact violated categories and reasons.

2. **Interactive Explainer Commands**:
   - `!analyze <text>` / `/analyze <text>`: Multi-label classification with visual progress bars.
   - `!explain <text>` / `/explain <text>`: Full step-by-step breakdown across all 6 NLP stages.
   - `!pipeline` / `/pipeline`: Theoretical reference guide for the 25PEC4CS1 syllabus.
   - `!inspect <token>`: Lexical inspection of a word (morphology, stem, lemma, leetspeak, WordNet synset).
   - `!test_cases`: Preloaded test scenarios (adversarial evasion, polysemy, anaphora, fairness).
   - `!stats`: Session moderation counters and category distributions.
   - `!threshold <value>`: Adjusts moderation sensitivity threshold.
   - `!moderate <on|off>`: Enables or disables automated message deletion.

3. **Offline CLI Simulator**:
   To test all bot commands without creating a Discord bot token:
   ```bash
   uv run python -m discord_bot.bot --simulate
   ```

---

## Unified Web Platform

The application has been consolidated into a single unified web dashboard:

1. **Input & Preset Console**:
   - Direct text input with character and token counters.
   - Benchmark scenario presets (Adversarial Leetspeak, Polysemous Metaphor, Anaphora Binding, Counterfactual Fairness, Hostile Threat, Clean Text).
   - Native support for `.txt` and `.pdf` file upload.

2. **Classification & Risk Summary**:
   - Clear status verdict: `CLEAN (PASS)`, `MODERATION WARNING`, or `CRITICAL VIOLATION`.
   - Discrete gauge bars for all 6 target dimensions (`toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate`).
   - Mathematical distribution metrics: Mean ($\mu$), Variance ($\sigma^2$), Standard Deviation ($\sigma$), and Jigsaw class priors.

3. **6-Stage Syllabus Inspector**:
   - Stage 1: Preliminary tokenization, sentence counts, and dataset class priors.
   - Stage 2: Levenshtein edit distance table, Porter stemming, morphology classification, and Laplace-smoothed Bigram Perplexity comparison (Toxic LM vs. Safe LM).
   - Stage 3: HMM Viterbi POS tagged sequence with Penn Treebank grammatical descriptions and optimal trellis log-likelihood.
   - Stage 4: WordNet Simplified Lesk WSD disambiguation cards resolving polysemous senses; TF-IDF Cosine Similarity & Distance table.
   - Stage 5: Hobbs' Algorithm pronoun-antecedent binding table; Centering Theory state transitions ($C_f, C_p, C_b$).
   - Stage 6: Token attribution saliency weights, automated PII redaction preview, and counterfactual fairness audit.

4. **Interactive Discord Terminal Simulator**:
   - Allows users to execute Discord bot commands directly inside the web browser.

5. **REST API Documentation**:
   - Complete OpenAPI documentation for `POST /predict` and `GET /api/health` with cURL, Python, and JavaScript snippets.

---

## Setup & Quickstart (with `uv`)

### 1. Prerequisites
- Python >= 3.10
- Node.js >= 18 (for building/running React frontend)
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### 2. Launch Everything with One Command
```bash
uv run start.py
```
This automatically:
1. Spawns the Flask NLP API on `http://127.0.0.1:5000`
2. Installs frontend dependencies and launches Vite on `http://localhost:5173`
3. Connects the Discord Bot (if `DISCORD_BOT_TOKEN` is exported)
4. Opens the unified dashboard in your default browser

### 3. Running Individual Components

**Run Discord Bot with Real Discord Gateway**:
```bash
export DISCORD_BOT_TOKEN="your_token_here"
uv run python -m discord_bot.bot
```

**Run Discord Bot in Offline Simulation Mode**:
```bash
uv run python -m discord_bot.bot --simulate
```

**Run Flask API Server Independently**:
```bash
uv run python toxicity_app/app.py
```

**Build React Frontend**:
```bash
cd frontend/react
npm install
npm run build
```

---

## Technologies Used

| Domain | Technology |
| :--- | :--- |
| **Linguistic Pipeline** | Pure Python 3.11, NLTK WordNet, Penn Treebank Taggers, Levenshtein Distance |
| **Statistical & Neural NLP** | NumPy, SciPy, scikit-learn, TensorFlow / Keras (BiLSTM), Laplace Add-1 Smoothing |
| **Backend & REST API** | Flask 3.0, Flask-CORS, Jinja2 |
| **Bot Integration** | Discord API, `discord.py` 2.7.1, Gateway Intents, Application Commands |
| **Frontend Dashboard** | React 18, TypeScript 5, Vite 5, Tailwind CSS v4, Zustand |

---

## Ethical Considerations & Governance

1. **Explainable AI (XAI)**:
   - High-stakes moderation requires transparent justification. The system provides token-level impact weights so users understand which specific words triggered the filter.

2. **Counterfactual Fairness & Demographic Parity**:
   - Standard toxic keyword filters often penalize non-toxic discussions involving identity groups (e.g., race, religion, sexual orientation). ToxiGuard conducts counterfactual debiasing to ensure identity terms unaccompanied by hostile lexicon do not trigger false-positive `identity_hate` flags.

3. **Data Privacy & PII Protection**:
   - Automated regular expression masking redacts Personally Identifiable Information (email addresses, phone numbers, IP addresses, user handles) prior to model evaluation or logging.
   - All neural and statistical inference runs locally on `127.0.0.1:5000`, ensuring user text is never transmitted to third-party proprietary APIs.
