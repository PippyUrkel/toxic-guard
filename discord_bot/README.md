# ToxiGuard Discord Moderation Bot & NLP Pipeline Explainer

### Course: Natural Language Processing (25PEC4CS1)
**Department of Computer Engineering • Fr. Conceicao Rodrigues College of Engineering (CRCE), Mumbai**

---

## Overview

The **ToxiGuard Discord Bot** is an automated moderation system and pedagogical NLP explainer for Discord servers. Utilizing the **25PEC4CS1 6-Stage NLP Pipeline**, it enforces server safety standards through automated tiered punishments (including **automatic permanent bans for high-severity violations >= 85%**) while delivering interpretable linguistic reasoning reports for every moderation decision.

---

## Tiered Enforcement Matrix

| Severity Tier | Toxicity Probability ($P_{\max}$) | Automated Action | Transparency & Reasoning |
| :--- | :--- | :--- | :--- |
| **Tier 3: Auto-Ban** | **$\ge 85.0\%$** (or `severe_toxic` / `threat` $\ge 0.85$) | **Immediate Permanent Server Ban** | Sends formal infraction notice + full 6-stage NLP report to user DM and routes audit proof to mod logs. |
| **Tier 2: Auto-Timeout** | **$70.0\% - 84.9\%$** (or 3+ warnings) | **15-Minute Timeout (Mute)** | Deletes message, mutes member, and posts stage-by-stage attribution report. |
| **Tier 1: Warning** | **$50.0\% - 69.9\%$** | **Message Deletion & Warning** | Removes message, logs infraction, and warns user (escalates at 3 warnings). |
| **Clean (Pass)** | **$< 50.0\%$** | **Permitted** | Message delivered without restriction. |

---

## Environment Configuration (`.env`)

The bot automatically loads its configuration from `.env` (or `.env.example`):

```bash
# Discord Gateway Token (from https://discord.com/developers/applications)
DISCORD_BOT_TOKEN=your_token_here

# Bot Prefix
DISCORD_BOT_PREFIX=!

# General Warning/Deletion Threshold (default: 50%)
TOXICITY_THRESHOLD=0.50

# Automated Auto-Ban (default: 85% or severe_toxic/threat >= 85%)
AUTOBAN_THRESHOLD=0.85
AUTOBAN_ENABLED=true

# Automated Timeout (default: 70% to 84%)
TIMEOUT_THRESHOLD=0.70
TIMEOUT_ENABLED=true
TIMEOUT_DURATION_MINUTES=15

# Message Management & Logging
DELETE_FLAGGED_MESSAGES=true
SEND_PUBLIC_EXPLANATION=true
SEND_DM_ON_PUNISHMENT=true

# Designated Moderation Log Channel ID (optional)
MOD_LOG_CHANNEL_ID=
```

---

## Bot Commands Reference

### Automated Moderation & User Management (Admin / Mod Only)

| Command | Arguments | Description |
| :--- | :--- | :--- |
| `!autoban` | `[<0.50-0.99> \| on \| off]` | View or update auto-ban threshold (e.g. `!autoban 0.85` or `!autoban off`). |
| `!timeout` | `[<0.50-0.95> \| duration <min> \| off]` | Configure timeout threshold (e.g. `!timeout 0.70`) or duration (`!timeout duration 30`). |
| `!infractions` | `@user` | Displays member infraction records, prior actions, and peak toxicity score. |
| `!clear_infractions` | `@user` | Clears moderation infraction history for a user. |
| `!scan_channel` | `[limit]` | Audits recent channel messages (10-100) and prints an aggregate toxicity health report. |
| `!scan_user` | `@user [limit]` | Evaluates a user's recent messages in the channel to compute their risk profile. |
| `!set_log_channel` | `#channel` | Routes all moderation audit logs to a designated staff channel. |
| `!unban` | `<user_id> [reason]` | Revokes a permanent ban for a user by Discord User ID. |

### Explainer & Educational Commands (Open to All Users)

| Command | Slash Command | Description |
| :--- | :--- | :--- |
| `!explain <text>` | `/explain <text>` | Generates a 6-stage NLP reasoning report showing why content was flagged or allowed. |
| `!analyze <text>` | `/analyze <text>` | Multi-label classification with ASCII progress bars across all 6 target dimensions. |
| `!inspect <token>` | - | Lexical inspection of a word (morphology, Porter stem, lemma, leetspeak, WordNet synset). |
| `!pipeline` | `/pipeline` | Complete theoretical documentation of the 25PEC4CS1 NLP syllabus. |
| `!test_cases` | - | Benchmark test suite showcasing adversarial evasion, WSD polysemy, and anaphora. |
| `!stats` | - | Displays session moderation counters (scanned, flagged, clean, bans, timeouts). |

---

## Setup & Running

### 1. Configure `.env`
Create or edit `.env` in the repository root:
```bash
cp .env.example .env
```
Edit `.env` and add your `DISCORD_BOT_TOKEN`.

### 2. Required Discord Gateway Intents
In the [Discord Developer Portal](https://discord.com/developers/applications):
- Under **Bot -> Privileged Gateway Intents**:
  - Enable **Message Content Intent** (Required for text monitoring).
  - Enable **Server Members Intent** (Required for autoban and timeout).
- Under **OAuth2 -> URL Generator**:
  - Scopes: `bot`, `applications.commands`
  - Permissions: `Administrator` or (`Manage Messages`, `Ban Members`, `Moderate Members`, `Send Messages`, `Read Message History`).

### 3. Launch Bot

**Live Discord Connection**:
```bash
uv run python -m discord_bot.bot
```

**Offline Terminal Simulation Console** (no token required):
```bash
uv run python -m discord_bot.bot --simulate
```

**One-Shot Command Tests**:
```bash
uv run python -m discord_bot.bot --explain "Shut up you disgusting pig, go die in a ditch, I will murder you."
uv run python -m discord_bot.bot --test "You are a st*pid id1ot"
```
