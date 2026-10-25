"""
=========================================================================================
ToxiGuard Discord Auto-Moderation & NLP Pipeline Explainer Bot
Course: Natural Language Processing (25PEC4CS1)
Fr. Conceicao Rodrigues College of Engineering (CRCE), Mumbai
=========================================================================================
Features:
1. Automated Multi-Tier Moderation with Auto-Ban:
   - Tier 3 (Score >= 85% or severe_toxic/threat >= 85%): Instant Auto-Ban + DM report
   - Tier 2 (Score >= 70% to 84%): Native Discord Timeout (Temporary Mute)
   - Tier 1 (Score >= 50% to 69%): Message Deletion + Warning
   - Escalation: 3 warnings automatically escalate to Timeout / Ban
2. Interactive Educational Commands:
   - !explain <text>  : Step-by-step 6-stage NLP reasoning report
   - !analyze <text>  : Probability scores with ASCII bar gauges
   - !inspect <token> : Morphology, Porter stem, WordNet synset & leetspeak decoding
   - !pipeline        : 25PEC4CS1 6-stage syllabus architecture documentation
   - !test_cases      : Benchmark test suite (adversarial, WSD metaphor, anaphora)
3. Mod & Channel Auditing:
   - !diagnose          : Complete health, permission, and gateway intent inspection
   - !invite            : Prints full OAuth2 bot invite link with proper scopes
   - !infractions @user : View user violation history and risk score
   - !scan_channel [N]  : Scan recent channel messages for toxic history
   - !scan_user @user   : Analyze a user's recent message toxicity profile
   - !autoban <val|off> : Configure or toggle autoban threshold
   - !timeout <val|off> : Configure timeout threshold & duration
   - !stats             : Moderation session analytics
4. Discord Apps / Context Menu Integration:
   - Right-click message -> Apps -> 'Check Toxicity'
   - Right-click message -> Apps -> 'Explain NLP Pipeline'
"""

import os
import sys
import time
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict

# -----------------------------------------------------------------------------------------
# Load Environment (.env)
# -----------------------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    env_paths = [Path.cwd() / ".env", Path(__file__).resolve().parent / ".env", Path(__file__).resolve().parent.parent / ".env"]
    for ep in env_paths:
        if ep.exists():
            load_dotenv(ep)
            break
except ImportError:
    pass

# Ensure parent and toxicity_app are on sys.path
BOT_DIR = Path(__file__).resolve().parent
ROOT_DIR = BOT_DIR.parent
APP_DIR = ROOT_DIR / "toxicity_app"

for p in (str(ROOT_DIR), str(APP_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from nlp_pipeline import run_full_nlp_pipeline, TOXIC_LEXICON, analyze_morphology
except ImportError:
    from toxicity_app.nlp_pipeline import run_full_nlp_pipeline, TOXIC_LEXICON, analyze_morphology

# Discord API import
try:
    import discord
    from discord.ext import commands
    from discord import app_commands
    HAS_DISCORD = True
except ImportError:
    HAS_DISCORD = False


# =========================================================================================
# CONFIGURATION & THRESHOLDS (LOADED FROM .ENV WITH SAFE DEFAULTS)
# =========================================================================================

def _get_float_env(key: str, default: float) -> float:
    try:
        return float(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default

def _get_bool_env(key: str, default: bool) -> bool:
    val = os.environ.get(key, "").lower()
    if val in ("true", "1", "yes", "on"):
        return True
    if val in ("false", "0", "no", "off"):
        return False
    return default

def _get_int_env(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default

DEFAULT_PREFIX = os.environ.get("DISCORD_BOT_PREFIX", "!")

CONFIG = {
    "auto_moderate": True,
    "delete_flagged": _get_bool_env("DELETE_FLAGGED_MESSAGES", True),
    "send_explanation": _get_bool_env("SEND_PUBLIC_EXPLANATION", True),
    "send_dm": _get_bool_env("SEND_DM_ON_PUNISHMENT", True),
    # General warning/deletion threshold (e.g. 0.50)
    "threshold": _get_float_env("TOXICITY_THRESHOLD", 0.50),
    # Autoban threshold (e.g. 0.85 = 85%)
    "autoban_threshold": _get_float_env("AUTOBAN_THRESHOLD", 0.85),
    "autoban_enabled": _get_bool_env("AUTOBAN_ENABLED", True),
    # Timeout threshold (e.g. 0.70 = 70%)
    "timeout_threshold": _get_float_env("TIMEOUT_THRESHOLD", 0.70),
    "timeout_enabled": _get_bool_env("TIMEOUT_ENABLED", True),
    "timeout_duration_minutes": _get_int_env("TIMEOUT_DURATION_MINUTES", 15),
    # Escalation: number of Tier 1 warnings before auto-timeout
    "warning_escalation_limit": 3,
    # Mod log channel ID (optional)
    "mod_log_channel_id": os.environ.get("MOD_LOG_CHANNEL_ID") or None,
}

LABELS = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]

SESSION_STATS = {
    "messages_scanned": 0,
    "messages_flagged": 0,
    "messages_clean": 0,
    "timeouts_issued": 0,
    "bans_issued": 0,
    "categories_triggered": {k: 0 for k in LABELS},
}

USER_INFRACTIONS: Dict[int, List[Dict[str, Any]]] = defaultdict(list)


# =========================================================================================
# TECHNICAL FORMATTERS (ZERO EMOJIS, HIGH-DENSITY MONOSPACE)
# =========================================================================================

def format_probabilities_block(predictions: Dict[str, float]) -> str:
    lines = ["[PREDICTION SCORES]"]
    for label in LABELS:
        val = predictions.get(label, 0.0)
        pct = f"{val * 100:5.1f}%"
        bar_len = int(val * 20)
        bar = "#" * bar_len + "-" * (20 - bar_len)
        status = "BAN" if val >= CONFIG["autoban_threshold"] else ("TIMEOUT" if val >= CONFIG["timeout_threshold"] else ("FLAG" if val >= CONFIG["threshold"] else "OK"))
        lines.append(f"  {label:<14} [{bar}] {pct} ({status})")
    return "\n".join(lines)


def format_stage_explanation(text: str, result: Dict[str, Any], action_taken: str = "NONE") -> str:
    preds = result["predictions"]
    syllabus = result["syllabus_analysis"]
    max_label = max(preds.items(), key=lambda x: x[1])
    is_toxic = max_label[1] >= CONFIG["threshold"]

    out = []
    out.append("=" * 64)
    out.append("TOXIGUARD NLP PIPELINE REASONING REPORT")
    out.append("Course: 25PEC4CS1 Linguistic & Statistical Verification")
    out.append("=" * 64)
    out.append(f"VERDICT      : {'FLAGGED AS TOXIC' if is_toxic else 'CLEAN (PASS)'}")
    out.append(f"MAX SEVERITY : {max_label[0]} at {max_label[1]*100:.1f}%")
    out.append(f"ACTION TAKEN : {action_taken}")
    out.append("-" * 64)

    # Stage 1: Preliminaries
    s1 = syllabus["module_1_preliminaries"]
    stats = s1["probability_statistics"]
    out.append("[STAGE 1: MATHEMATICAL & STATISTICAL PRELIMINARIES]")
    out.append(f"  Sentence Count : {s1['sentence_count']} | Token Count: {s1['token_count']}")
    out.append(f"  Distribution   : Mean={stats['mean_probability']} | Var={stats['variance']} | StdDev={stats['std_dev']}")
    out.append(f"  Bayes Priors   : Toxic={s1['jigsaw_class_priors']['toxic']} | Threat={s1['jigsaw_class_priors']['threat']}")
    out.append("")

    # Stage 2: Word-Level & Morphology
    s2 = syllabus["module_2_word_level"]
    norm_tokens = s2["adversarial_edit_distance"]
    modified = [item for item in norm_tokens if item["edit_distance"] > 0 or item["matched_lexicon"]]
    out.append("[STAGE 2: WORD-LEVEL NORMALIZATION & N-GRAM LANGUAGE MODEL]")
    if modified:
        out.append("  Detected Adversarial / Obfuscated Tokens:")
        for m in modified[:5]:
            out.append(f"    * '{m['original']}' -> '{m['normalized']}' (Edit Dist: {m['edit_distance']}, Method: {m['method']})")
    else:
        out.append("  Adversarial Check: No leetspeak or obfuscation detected.")
    
    lm = s2["ngram_language_model"]
    out.append(f"  Bigram Perplexity (Laplace Add-1 Smoothing):")
    out.append(f"    * Toxic Corpus LM : {lm['toxic_corpus_perplexity']}")
    out.append(f"    * Safe Corpus LM  : {lm['safe_corpus_perplexity']}")
    out.append("")

    # Stage 3: Syntax & POS
    s3 = syllabus["module_3_syntax_level"]
    pos_tags = s3.get("tagged_tokens", [])
    out.append("[STAGE 3: SYNTACTIC HMM + VITERBI POS TAGGING]")
    out.append(f"  Viterbi Optimal Path Log-Likelihood: {s3.get('best_path_log_prob', 'N/A')}")
    pos_summary = " ".join([f"{t['token']}/{t['pos_tag']}" for t in pos_tags[:10]])
    out.append(f"  Trellis Path: {pos_summary}")
    out.append("")

    # Stage 4: Semantics & WSD
    s4 = syllabus["module_4_semantic_analysis"]
    wsd_items = s4["wordnet_lesk_wsd"]
    out.append("[STAGE 4: SEMANTIC DISAMBIGUATION & VECTOR SPACE DISTANCE]")
    if wsd_items:
        for w in wsd_items[:3]:
            out.append(f"    * Token '{w['word']}' -> Synset '{w['selected_synset']}' ({w['sense_type']})")
            out.append(f"      Gloss: {w['gloss'][:60]}...")
    else:
        out.append("  WordNet WSD: No ambiguous trigger tokens requiring polysemy resolution.")

    cosines = s4["tfidf_cosine_similarity"]
    if cosines:
        top_c = cosines[0]
        out.append(f"  Top Cosine Match: Ref '{top_c['doc_id']}' ({top_c['category']}) | Sim: {top_c['cosine_similarity']} | Dist: {top_c['cosine_distance']}")
    out.append("")

    # Stage 5: Pragmatics & Anaphora
    s5 = syllabus["module_5_pragmatics_discourse"]
    anaphors = s5.get("anaphora_resolutions", [])
    out.append("[STAGE 5: PRAGMATICS & DISCOURSE ANAPHORA RESOLUTION]")
    if anaphors:
        for a in anaphors[:3]:
            out.append(f"    * Anaphor '{a['anaphor']}' (S{a['sentence']}) -> Antecedent: '{a['resolved_antecedent']}' [{a['algorithm']}]")
    else:
        out.append("  Anaphora: No pronominal anaphors requiring resolution.")
    out.append("")

    # Stage 6: Ethics & XAI
    s6 = syllabus["module_6_ethics_and_xai"]
    attributions = s6["xai_token_attributions"]
    toxic_tokens = [a for a in attributions if a["impact"] > 0]
    safe_tokens = [a for a in attributions if a["impact"] < 0]
    out.append("[STAGE 6: EXPLAINABLE AI (XAI) ATTRIBUTION & ETHICAL AUDIT]")
    if toxic_tokens:
        out.append("  Primary Toxicity Drivers (Positive Saliency):")
        for t in toxic_tokens[:4]:
            out.append(f"    * '{t['token']}' (+{t['impact']}) -> Categories: {', '.join(t['categories'])}")
    if safe_tokens:
        out.append("  Mitigating Context Tokens (WSD Safe):")
        for t in safe_tokens[:2]:
            out.append(f"    * '{t['token']}' ({t['impact']}) -> {t['reason']}")

    fairness = s6["fairness_and_privacy"]
    out.append(f"  Counterfactual Fairness : {'PASSED' if fairness['demographic_parity_audit']['counterfactual_fairness_passed'] else 'FLAGGED'}")
    out.append(f"  PII Redacted Preview    : {fairness['privacy_compliance']['anonymized_preview']}")
    out.append("=" * 64)

    return "\n".join(out)


def format_pipeline_architecture_doc() -> str:
    return """
=========================================================================================
TOXIGUARD NLP PIPELINE ARCHITECTURE (Course: 25PEC4CS1)
Fr. Conceicao Rodrigues College of Engineering (CRCE), Mumbai
=========================================================================================
STAGE 1: MATHEMATICAL & STATISTICAL PRELIMINARIES (Module 1)
- Token & sentence segmentation via regex and Penn Treebank tokenizers.
- Computes sample Mean (mu), Variance (sigma^2), and Standard Deviation (sigma).
- Bayesian class priors from Jigsaw Kaggle dataset prevent bias from class skew.

STAGE 2: WORD-LEVEL NORMALIZATION & N-GRAM LANGUAGE MODELING (Module 2)
- Adversarial Obfuscation Decoding: Levenshtein minimum edit distance and leetspeak map.
- Morphology: Porter Stemmer, lemmatization, inflectional/derivational affix tagging.
- Bigram LM: Sentence perplexity using Laplace (Add-1) smoothing across Toxic vs Safe corpora.

STAGE 3: SYNTACTIC ANALYSIS & PART-OF-SPEECH TAGGING (Module 3)
- Penn Treebank POS tagging with Hidden Markov Models (HMM).
- Trellis dynamic programming via Viterbi decoding calculates the globally optimal POS sequence.

STAGE 4: SEMANTIC DISAMBIGUATION & VECTOR SPACE DISTANCE (Module 4)
- Word Sense Disambiguation: WordNet Simplified Lesk algorithm separating figurative praise
  ('killing it') from literal violence.
- Vector Space Model (VSM): TF-IDF feature extraction, Cosine Similarity & Distance (Dc = 1 - Sc).

STAGE 5: PRAGMATICS & DISCOURSE PROCESSING (Module 5)
- Hobbs' Syntactic Algorithm for pronominal anaphora resolution.
- Centering Theory: Forward Centers (Cf), Preferred Center (Cp), Backward Center (Cb), and
  state transition classification (Continue, Retain, Shift).

STAGE 6: ETHICS, DATA PRIVACY & EXPLAINABLE AI (XAI) (Module 6)
- Token-level impact attribution (saliency weights) explaining each classification.
- Automated PII redaction (emails, phone numbers, IP addresses, handles).
- Demographic parity auditing prevents false-positive bias on protected identity terms.
=========================================================================================
"""


# =========================================================================================
# BOT FACTORY FUNCTION (CREATES & REGISTERS ALL COMMANDS ON GIVEN INTENTS)
# =========================================================================================

def create_bot(intents: discord.Intents) -> commands.Bot:
    bot = commands.Bot(
        command_prefix=DEFAULT_PREFIX,
        intents=intents,
        help_command=None
    )

    async def _send_mod_log(guild: discord.Guild, fallback_channel: discord.TextChannel, message_text: str):
        target_channel = fallback_channel
        if CONFIG["mod_log_channel_id"]:
            try:
                ch = guild.get_channel(int(CONFIG["mod_log_channel_id"]))
                if ch:
                    target_channel = ch
            except Exception:
                pass
        
        chunks = [message_text[i:i + 1900] for i in range(0, len(message_text), 1900)]
        for chunk in chunks:
            try:
                await target_channel.send(f"```\n{chunk}\n```")
            except Exception:
                pass

    @bot.event
    async def on_ready():
        invite_url = f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=1099511753734&scope=bot%20applications.commands"

        print("\n" + "=" * 80)
        print(f"[DISCORD BOT LIVE] Logged in as: {bot.user.name} (ID: {bot.user.id})")
        print(f"[STATUS] Connected Guilds: {len(bot.guilds)}")
        print(f"[STATUS] Message Content Intent : {'ENABLED (Active - Reading Chat)' if bot.intents.message_content else 'DISABLED (CRITICAL: Chat text is empty)'}")
        print(f"[STATUS] Server Members Intent  : {'ENABLED' if bot.intents.members else 'DISABLED'}")
        print(f"[POLICY] Auto-Ban Threshold: {CONFIG['autoban_threshold'] * 100:.1f}% | Timeout: {CONFIG['timeout_threshold'] * 100:.1f}%")
        print("-" * 80)
        print(f"[PROPER BOT OAUTH2 INVITE URL (USE THIS TO INVITE AS A BOT USER WITH INTENTS)]:")
        print(f"  {invite_url}")
        print("=" * 80 + "\n")
        
        try:
            synced = await bot.tree.sync()
            print(f"[DISCORD BOT] Synced {len(synced)} application/context-menu commands.")
        except Exception as e:
            print(f"[DISCORD BOT] Slash command sync note: {e}")

    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return

        # Always process prefix commands first
        if message.content.startswith(bot.command_prefix):
            await bot.process_commands(message)
            return

        # DIAGNOSTIC CHECK: Did Discord send an empty message content?
        if not message.content.strip():
            if not message.attachments and not message.embeds:
                print(f"[CHAT ALERT] Received message from '{message.author.name}' in #{message.channel.name} with EMPTY content.")
                print("  -> CAUSE: 'MESSAGE CONTENT INTENT' is disabled in your Discord Developer Portal.")
                print("  -> FIX: Go to https://discord.com/developers/applications/ -> Bot tab -> Enable 'MESSAGE CONTENT INTENT'.")
            return

        if not CONFIG["auto_moderate"]:
            return

        SESSION_STATS["messages_scanned"] += 1
        result = run_full_nlp_pipeline(message.content)
        preds = result["predictions"]

        max_label, max_score = max(preds.items(), key=lambda x: x[1])
        triggered = [lbl for lbl in LABELS if preds.get(lbl, 0.0) >= CONFIG["threshold"]]

        # Live chat scan terminal log
        print(f"[CHAT SCANNED] #{message.channel.name} | {message.author.name}: \"{message.content[:50]}\" -> Max: {max_label} ({max_score*100:.1f}%)")

        if not triggered:
            SESSION_STATS["messages_clean"] += 1
            return

        SESSION_STATS["messages_flagged"] += 1
        for t in triggered:
            SESSION_STATS["categories_triggered"][t] += 1

        author = message.author
        guild = message.guild
        member = guild.get_member(author.id) if guild else None

        if CONFIG["delete_flagged"]:
            try:
                await message.delete()
                print(f"[MOD ACTION] Deleted violating message from {author.name} in #{message.channel.name}")
            except discord.Forbidden:
                print(f"[DISCORD BOT WARN] Missing 'Manage Messages' permission to delete message in {message.channel}.")
            except Exception as e:
                print(f"[DISCORD BOT WARN] Failed to delete message: {e}")

        # TIER 3: AUTOBAN (>= 85%)
        is_autoban = (
            CONFIG["autoban_enabled"]
            and (max_score >= CONFIG["autoban_threshold"] or preds.get("severe_toxic", 0.0) >= CONFIG["autoban_threshold"] or preds.get("threat", 0.0) >= CONFIG["autoban_threshold"])
        )

        prior_warnings = len([inf for inf in USER_INFRACTIONS[author.id] if inf["action"] == "WARNING"])
        is_timeout = (
            not is_autoban
            and CONFIG["timeout_enabled"]
            and member is not None
            and (max_score >= CONFIG["timeout_threshold"] or prior_warnings >= CONFIG["warning_escalation_limit"])
        )

        action_name = "AUTOBAN" if is_autoban else ("TIMEOUT" if is_timeout else "WARNING_DELETION")

        USER_INFRACTIONS[author.id].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "max_score": max_score,
            "max_label": max_label,
            "triggered_categories": triggered,
            "action": action_name,
            "text_preview": message.content[:80]
        })

        explanation = format_stage_explanation(message.content, result, action_taken=action_name)

        if CONFIG["send_dm"]:
            try:
                dm_lines = [
                    f"[TOXIGUARD MODERATION NOTICE - SERVER: {guild.name if guild else 'DISCORD'}]",
                    f"Action Taken: {action_name}",
                    f"Your message was flagged by the 25PEC4CS1 NLP safety pipeline for violating server guidelines.",
                    f"Trigger Score: {max_label} at {max_score*100:.1f}%",
                    f"Full NLP Reasoning Report:\n",
                    explanation
                ]
                dm_text = "\n".join(dm_lines)
                for chunk in [dm_text[i:i + 1900] for i in range(0, len(dm_text), 1900)]:
                    await author.send(f"```\n{chunk}\n```")
            except Exception:
                pass

        if is_autoban:
            SESSION_STATS["bans_issued"] += 1
            ban_reason = f"ToxiGuard Auto-Ban: High-severity toxicity ({max_label}: {max_score*100:.1f}% >= {CONFIG['autoban_threshold']*100:.1f}%)"
            banned_successfully = False

            if guild:
                try:
                    await guild.ban(author, reason=ban_reason, delete_message_days=1)
                    banned_successfully = True
                    print(f"[ENFORCEMENT] Auto-Banned {author.name} (ID: {author.id}) from {guild.name}")
                except discord.Forbidden:
                    print(f"[DISCORD BOT ERROR] Missing 'Ban Members' permission in guild '{guild.name}'.")
                except Exception as e:
                    print(f"[DISCORD BOT ERROR] Failed to ban user: {e}")

            audit_report = [
                "=" * 64,
                "[TOXIGUARD AUTO-MODERATION ENFORCEMENT: AUTOBAN]",
                "=" * 64,
                f"User        : {author.name} (ID: {author.id})",
                f"Status      : {'PERMANENTLY BANNED' if banned_successfully else 'BAN FAILED (CHECK BOT ROLE/PERMS)'}",
                f"Max Score   : {max_label} = {max_score*100:.1f}% (Threshold: {CONFIG['autoban_threshold']*100:.1f}%)",
                f"Categories  : {', '.join(triggered)}",
                f"Trigger Text: \"{message.content[:80]}\"",
                f"Reason      : Critical toxicity violation detected by the 25PEC4CS1 NLP pipeline.",
                "=" * 64
            ]
            if guild:
                await _send_mod_log(guild, message.channel, "\n".join(audit_report))
                if CONFIG["send_explanation"]:
                    await _send_mod_log(guild, message.channel, explanation)

        elif is_timeout and member:
            SESSION_STATS["timeouts_issued"] += 1
            timeout_duration = timedelta(minutes=CONFIG["timeout_duration_minutes"])
            timeout_reason = f"ToxiGuard Auto-Timeout: Toxicity ({max_label}: {max_score*100:.1f}%)"
            timeout_ok = False

            try:
                await member.timeout(timeout_duration, reason=timeout_reason)
                timeout_ok = True
                print(f"[ENFORCEMENT] Timed out {author.name} for {CONFIG['timeout_duration_minutes']}m in {guild.name}")
            except discord.Forbidden:
                print(f"[DISCORD BOT ERROR] Missing 'Moderate Members' permission for timeout in '{guild.name}'.")
            except Exception as e:
                print(f"[DISCORD BOT ERROR] Failed to timeout user: {e}")

            audit_report = [
                "=" * 64,
                "[TOXIGUARD AUTO-MODERATION ENFORCEMENT: TIMEOUT]",
                "=" * 64,
                f"User        : {author.name} (ID: {author.id})",
                f"Action      : {CONFIG['timeout_duration_minutes']}-MINUTE TIMEOUT ({'APPLIED' if timeout_ok else 'FAILED - NO PERMS'})",
                f"Max Score   : {max_label} = {max_score*100:.1f}% (Threshold: {CONFIG['timeout_threshold']*100:.1f}%)",
                f"Categories  : {', '.join(triggered)}",
                f"Trigger Text: \"{message.content[:80]}\"",
                f"Note        : User temporarily muted from sending messages in this server.",
                "=" * 64
            ]
            if guild:
                await _send_mod_log(guild, message.channel, "\n".join(audit_report))
                if CONFIG["send_explanation"]:
                    await _send_mod_log(guild, message.channel, explanation)

        else:
            audit_report = [
                "=" * 64,
                "[TOXIGUARD AUTO-MODERATION ENFORCEMENT: WARNING]",
                "=" * 64,
                f"User        : {author.name} (ID: {author.id})",
                f"Action      : MESSAGE DELETED & WARNING ISSUED",
                f"Violations  : {', '.join([f'{k}={preds[k]*100:.1f}%' for k in triggered])}",
                f"Warnings    : Infraction #{len(USER_INFRACTIONS[author.id])} (Escalates to timeout at #{CONFIG['warning_escalation_limit']})",
                f"Reason      : Lexical/semantic violation identified by 25PEC4CS1 NLP pipeline.",
                "=" * 64
            ]
            if guild:
                await _send_mod_log(guild, message.channel, "\n".join(audit_report))
                if CONFIG["send_explanation"]:
                    await _send_mod_log(guild, message.channel, explanation)

    # -------------------------------------------------------------------------------------
    # DIAGNOSTIC COMMANDS (!diagnose, !invite)
    # -------------------------------------------------------------------------------------

    @bot.command(name="diagnose", aliases=["check_setup", "healthcheck"])
    async def cmd_diagnose(ctx: commands.Context):
        """Diagnose gateway intents, channel permissions, and bot member status."""
        guild = ctx.guild
        member = guild.me if guild else None
        perms = ctx.channel.permissions_for(member) if member else None

        lines = [
            "=" * 64,
            "TOXIGUARD BOT CONFIGURATION & PERMISSION DIAGNOSTIC",
            "=" * 64,
            f"Bot Identity      : {bot.user.name}#{bot.user.discriminator} (ID: {bot.user.id})",
            f"Server Guild      : {guild.name if guild else 'DM'} (Members: {guild.member_count if guild else 1})",
            "",
            "[GATEWAY INTENTS STATUS (FROM DISCORD DEVELOPER PORTAL)]",
            f"  Message Content Intent : {'ENABLED (Bot CAN read chat messages)' if bot.intents.message_content else 'DISABLED (CRITICAL: Chat text is blocked by Discord)'}",
            f"  Server Members Intent  : {'ENABLED' if bot.intents.members else 'DISABLED'}",
            "",
            "[CHANNEL PERMISSIONS IN THIS CHANNEL]",
            f"  View Channel          : {'OK' if perms and perms.view_channel else 'MISSING'}",
            f"  Read Message History  : {'OK' if perms and perms.read_message_history else 'MISSING'}",
            f"  Send Messages         : {'OK' if perms and perms.send_messages else 'MISSING'}",
            f"  Manage Messages       : {'OK (Can Delete Toxic)' if perms and perms.manage_messages else 'MISSING (Cannot delete messages)'}",
            f"  Moderate Members      : {'OK (Can Timeout)' if perms and perms.moderate_members else 'MISSING (Cannot timeout)'}",
            f"  Ban Members           : {'OK (Can Auto-Ban)' if perms and perms.ban_members else 'MISSING (Cannot auto-ban)'}",
            "",
            "[ACTIVE MODERATION POLICY]",
            f"  Auto-Ban Threshold    : {CONFIG['autoban_threshold'] * 100:.1f}% [{'ENABLED' if CONFIG['autoban_enabled'] else 'DISABLED'}]",
            f"  Timeout Threshold     : {CONFIG['timeout_threshold'] * 100:.1f}% (Duration: {CONFIG['timeout_duration_minutes']}m)",
            f"  General Warning       : {CONFIG['threshold'] * 100:.1f}%",
            "",
            "[BOT INVITE URL - USE TO RE-INVITE AS BOT WITH FULL PERMISSIONS]",
            f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=1099511753734&scope=bot%20applications.commands",
            "=" * 64
        ]
        await ctx.send("```\n" + "\n".join(lines) + "\n```")

    @bot.command(name="invite")
    async def cmd_invite(ctx: commands.Context):
        """Get the full OAuth2 invite URL to add the bot with both 'bot' and 'applications.commands' scopes."""
        url = f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=1099511753734&scope=bot%20applications.commands"
        lines = [
            "[TOXIGUARD BOT OAUTH2 INVITE URL]",
            "To ensure the bot joins your server as a full member with chat-reading and auto-ban permissions, use this exact URL:",
            url
        ]
        await ctx.send("```\n" + "\n".join(lines) + "\n```")

    # -------------------------------------------------------------------------------------
    # REGULAR COMMANDS (!analyze, !explain, !pipeline, !inspect, !autoban, !timeout, etc.)
    # -------------------------------------------------------------------------------------

    @bot.command(name="analyze")
    async def cmd_analyze(ctx: commands.Context, *, text: str = None):
        """Analyze text and display probability matrix and primary trigger tokens."""
        if not text:
            await ctx.send("```\nError: Please provide text to analyze.\nUsage: !analyze <text>\n```")
            return

        result = run_full_nlp_pipeline(text)
        preds = result["predictions"]
        score_block = format_probabilities_block(preds)

        syllabus = result["syllabus_analysis"]
        xai = syllabus["module_6_ethics_and_xai"]["xai_token_attributions"]
        triggers = [t for t in xai if t["impact"] > 0]

        lines = [score_block, ""]
        if triggers:
            lines.append("[DETECTED TRIGGER TOKENS]")
            for t in triggers[:5]:
                lines.append(f"  * Token: '{t['token']}' | Impact: +{t['impact']} | Reason: {t['reason']}")
        else:
            lines.append("[DETECTED TRIGGER TOKENS]\n  None detected (text evaluated as clean).")

        lines.append("")
        lines.append(f"For full 6-stage NLP reasoning, run: {bot.command_prefix}explain <text>")
        await ctx.send(f"```\n" + "\n".join(lines) + "\n```")

    @bot.command(name="explain")
    async def cmd_explain(ctx: commands.Context, *, text: str = None):
        """Explain step-by-step why the 6-stage NLP pipeline classified or filtered the text."""
        if not text:
            await ctx.send("```\nError: Please provide text to explain.\nUsage: !explain <text>\n```")
            return

        result = run_full_nlp_pipeline(text)
        report = format_stage_explanation(text, result)
        chunks = [report[i:i + 1900] for i in range(0, len(report), 1900)]
        for chunk in chunks:
            await ctx.send(f"```\n{chunk}\n```")

    @bot.command(name="pipeline")
    async def cmd_pipeline(ctx: commands.Context):
        """Show full theoretical documentation of the 25PEC4CS1 6-Stage NLP Pipeline."""
        doc = format_pipeline_architecture_doc()
        chunks = [doc[i:i + 1900] for i in range(0, len(doc), 1900)]
        for chunk in chunks:
            await ctx.send(f"```\n{chunk}\n```")

    @bot.command(name="inspect")
    async def cmd_inspect(ctx: commands.Context, token: str = None):
        """Inspect a single token's morphology, stem, lemma, leetspeak map, and WordNet senses."""
        if not token:
            await ctx.send("```\nError: Please specify a word to inspect.\nUsage: !inspect <word>\n```")
            return

        morph = analyze_morphology(token)
        lexicon_hits = TOXIC_LEXICON.get(token.lower(), [])
        res = run_full_nlp_pipeline(token)
        s2 = res["syllabus_analysis"]["module_2_word_level"]
        norm = s2["adversarial_edit_distance"][0] if s2["adversarial_edit_distance"] else {}
        wsd = res["syllabus_analysis"]["module_4_semantic_analysis"]["wordnet_lesk_wsd"]

        lines = [
            f"[TOKEN LEXICAL INSPECTION: '{token}']",
            f"  Normalized Form : '{norm.get('normalized', token)}'",
            f"  Edit Distance   : {norm.get('edit_distance', 0)} ({norm.get('method', 'None')})",
            f"  Lemma           : '{morph.get('lemma', token)}'",
            f"  Porter Stem     : '{morph.get('porter_stem', token)}'",
            f"  Morphology Type : {morph.get('morphology_type', 'N/A')}",
            f"  Toxic Lexicon   : {', '.join(lexicon_hits) if lexicon_hits else 'Not in raw toxic lexicon'}",
        ]
        if wsd:
            w = wsd[0]
            lines.append(f"  WordNet Synset  : {w['selected_synset']} ({w['sense_type']})")
            lines.append(f"  Gloss           : {w['gloss']}")
            lines.append(f"  Synonyms        : {', '.join(w['lexical_relations']['synonyms'][:5])}")
            lines.append(f"  Hypernyms       : {', '.join(w['lexical_relations']['hypernyms'][:5])}")
        else:
            lines.append("  WordNet Sense   : No dedicated polysemy mapping found in knowledge base.")

        await ctx.send("```\n" + "\n".join(lines) + "\n```")

    @bot.command(name="autoban")
    @commands.has_permissions(administrator=True)
    async def cmd_autoban(ctx: commands.Context, arg: str = None):
        """View or configure the auto-ban threshold: !autoban 0.85 OR !autoban off"""
        if not arg:
            status = "ENABLED" if CONFIG["autoban_enabled"] else "DISABLED"
            await ctx.send(f"```\n[AUTOBAN SETTINGS]\n  Status    : {status}\n  Threshold : {CONFIG['autoban_threshold'] * 100:.1f}%\n  Usage     : !autoban <0.50-0.99> OR !autoban <on|off>\n```")
            return

        if arg.lower() in ("off", "disable", "disabled"):
            CONFIG["autoban_enabled"] = False
            await ctx.send("```\n[OK] Auto-ban feature has been DISABLED.\n```")
            return
        elif arg.lower() in ("on", "enable", "enabled"):
            CONFIG["autoban_enabled"] = True
            await ctx.send(f"```\n[OK] Auto-ban feature ENABLED at {CONFIG['autoban_threshold'] * 100:.1f}% threshold.\n```")
            return

        try:
            val = float(arg)
            if not (0.50 <= val <= 0.99):
                await ctx.send("```\nError: Autoban threshold must be between 0.50 and 0.99 (e.g., !autoban 0.85).\n```")
                return
            CONFIG["autoban_threshold"] = round(val, 2)
            CONFIG["autoban_enabled"] = True
            await ctx.send(f"```\n[OK] Auto-ban threshold updated to {CONFIG['autoban_threshold'] * 100:.1f}%. Users exceeding this score will be automatically banned.\n```")
        except ValueError:
            await ctx.send("```\nUsage: !autoban <0.50 - 0.99> (e.g. !autoban 0.85) OR !autoban off\n```")

    @bot.command(name="timeout")
    @commands.has_permissions(administrator=True)
    async def cmd_timeout(ctx: commands.Context, setting: str = None, value: str = None):
        """Configure timeout parameters: !timeout 0.70 OR !timeout duration 30 OR !timeout off"""
        if not setting:
            status = "ENABLED" if CONFIG["timeout_enabled"] else "DISABLED"
            await ctx.send(f"```\n[TIMEOUT SETTINGS]\n  Status    : {status}\n  Threshold : {CONFIG['timeout_threshold'] * 100:.1f}%\n  Duration  : {CONFIG['timeout_duration_minutes']} minutes\n  Usage     : !timeout <0.50-0.90> OR !timeout duration <minutes> OR !timeout <on|off>\n```")
            return

        if setting.lower() in ("off", "disable"):
            CONFIG["timeout_enabled"] = False
            await ctx.send("```\n[OK] Auto-timeout feature DISABLED.\n```")
            return
        elif setting.lower() in ("on", "enable"):
            CONFIG["timeout_enabled"] = True
            await ctx.send(f"```\n[OK] Auto-timeout feature ENABLED at {CONFIG['timeout_threshold'] * 100:.1f}% threshold.\n```")
            return
        elif setting.lower() == "duration" and value:
            try:
                mins = int(value)
                CONFIG["timeout_duration_minutes"] = max(1, min(1440, mins))
                await ctx.send(f"```\n[OK] Timeout duration set to {CONFIG['timeout_duration_minutes']} minutes.\n```")
            except ValueError:
                await ctx.send("```\nUsage: !timeout duration <minutes>\n```")
            return

        try:
            val = float(setting)
            if not (0.50 <= val <= 0.95):
                await ctx.send("```\nError: Timeout threshold must be between 0.50 and 0.95.\n```")
                return
            CONFIG["timeout_threshold"] = round(val, 2)
            CONFIG["timeout_enabled"] = True
            await ctx.send(f"```\n[OK] Timeout threshold updated to {CONFIG['timeout_threshold'] * 100:.1f}%.\n```")
        except ValueError:
            await ctx.send("```\nUsage: !timeout <0.50 - 0.95> OR !timeout duration <minutes>\n```")

    @bot.command(name="set_log_channel")
    @commands.has_permissions(administrator=True)
    async def cmd_set_log_channel(ctx: commands.Context, channel: discord.TextChannel = None):
        """Set designated moderation log channel: !set_log_channel #mod-logs"""
        if not channel:
            await ctx.send("```\nUsage: !set_log_channel #channel-name\n```")
            return
        CONFIG["mod_log_channel_id"] = str(channel.id)
        await ctx.send(f"```\n[OK] ToxiGuard moderation audit logs routed to: #{channel.name} (ID: {channel.id})\n```")

    @bot.command(name="infractions", aliases=["history"])
    @commands.has_permissions(moderate_members=True)
    async def cmd_infractions(ctx: commands.Context, member: discord.Member = None):
        """View user infraction history and risk score: !infractions @user"""
        if not member:
            await ctx.send("```\nUsage: !infractions @user\n```")
            return

        records = USER_INFRACTIONS.get(member.id, [])
        if not records:
            await ctx.send(f"```\n[USER INFRACTIONS RECORD: {member.name}]\n  No infractions logged. Member standing is clean.\n```")
            return

        max_recorded = max([r["max_score"] for r in records])
        lines = [
            f"[USER INFRACTIONS RECORD: {member.name}]",
            f"  Total Violations : {len(records)}",
            f"  Max Toxic Score  : {max_recorded * 100:.1f}%",
            f"  Current Status   : {'CRITICAL RISK' if max_recorded >= CONFIG['autoban_threshold'] else ('WARNING' if max_recorded >= CONFIG['threshold'] else 'MONITORED')}",
            "",
            "[RECENT INCIDENT LOGS]"
        ]
        for r in records[-5:]:
            lines.append(f"  * {r['timestamp'][:19]} | Action: {r['action']:<14} | Max: {r['max_label']} ({r['max_score']*100:.1f}%) | Text: \"{r['text_preview']}\"")

        await ctx.send("```\n" + "\n".join(lines) + "\n```")

    @bot.command(name="clear_infractions")
    @commands.has_permissions(administrator=True)
    async def cmd_clear_infractions(ctx: commands.Context, member: discord.Member = None):
        """Clear infraction records for a user: !clear_infractions @user"""
        if not member:
            await ctx.send("```\nUsage: !clear_infractions @user\n```")
            return
        USER_INFRACTIONS.pop(member.id, None)
        await ctx.send(f"```\n[OK] Cleared all infraction records for: {member.name} (ID: {member.id})\n```")

    @bot.command(name="scan_channel")
    @commands.has_permissions(moderate_members=True)
    async def cmd_scan_channel(ctx: commands.Context, limit: int = 50):
        """Scan recent messages in channel for aggregate toxicity metrics: !scan_channel [limit]"""
        limit = max(10, min(100, limit))
        await ctx.send(f"```\n[Scanning last {limit} messages in #{ctx.channel.name} using 25PEC4CS1 NLP Pipeline...]\n```")

        total_scanned = 0
        toxic_count = 0
        max_seen = 0.0
        flagged_entries = []

        async for msg in ctx.channel.history(limit=limit):
            if msg.author.bot or not msg.content.strip():
                continue
            total_scanned += 1
            res = run_full_nlp_pipeline(msg.content)
            preds = res["predictions"]
            m_lbl, m_score = max(preds.items(), key=lambda x: x[1])
            if m_score > max_seen:
                max_seen = m_score
            if m_score >= CONFIG["threshold"]:
                toxic_count += 1
                flagged_entries.append((msg.author.name, m_lbl, m_score, msg.content[:40]))

        toxic_ratio = (toxic_count / total_scanned * 100) if total_scanned > 0 else 0.0
        lines = [
            f"[CHANNEL AUDIT REPORT: #{ctx.channel.name}]",
            f"  Messages Scanned : {total_scanned}",
            f"  Flagged Messages : {toxic_count} ({toxic_ratio:.1f}% toxicity rate)",
            f"  Peak Toxicity    : {max_seen * 100:.1f}%",
            f"  Channel Health   : {'POOR' if toxic_ratio > 20 else ('FAIR' if toxic_ratio > 5 else 'HEALTHY')}",
        ]
        if flagged_entries:
            lines.append("\n[SAMPLED TOXIC VIOLATIONS]")
            for author_name, lbl, score, preview in flagged_entries[:4]:
                lines.append(f"  * {author_name:<14} -> {lbl} ({score*100:.1f}%): \"{preview}\"")

        await ctx.send("```\n" + "\n".join(lines) + "\n```")

    @bot.command(name="scan_user")
    @commands.has_permissions(moderate_members=True)
    async def cmd_scan_user(ctx: commands.Context, member: discord.Member = None, limit: int = 50):
        """Analyze a user's recent messages in the channel: !scan_user @user [limit]"""
        if not member:
            await ctx.send("```\nUsage: !scan_user @user [limit]\n```")
            return

        limit = max(10, min(100, limit))
        user_messages = []
        async for msg in ctx.channel.history(limit=150):
            if msg.author.id == member.id and msg.content.strip() and not msg.content.startswith(bot.command_prefix):
                user_messages.append(msg.content)
                if len(user_messages) >= limit:
                    break

        if not user_messages:
            await ctx.send(f"```\nNo recent text messages found for user {member.name} in this channel.\n```")
            return

        scores = []
        for text in user_messages:
            res = run_full_nlp_pipeline(text)
            scores.append(max(res["predictions"].values()))

        avg_score = sum(scores) / len(scores)
        peak_score = max(scores)

        lines = [
            f"[USER BEHAVIORAL PROFILE: {member.name}]",
            f"  Sampled Messages : {len(user_messages)}",
            f"  Average Toxicity : {avg_score * 100:.1f}%",
            f"  Peak Toxicity    : {peak_score * 100:.1f}%",
            f"  Risk Profile     : {'CRITICAL (AUTOBAN CANDIDATE)' if peak_score >= CONFIG['autoban_threshold'] else ('ELEVATED' if peak_score >= CONFIG['threshold'] else 'LOW / SAFE')}",
            f"  Prior Infractions: {len(USER_INFRACTIONS[member.id])}",
        ]
        await ctx.send("```\n" + "\n".join(lines) + "\n```")

    @bot.command(name="unban")
    @commands.has_permissions(administrator=True)
    async def cmd_unban(ctx: commands.Context, user_id: int = None, *, reason: str = "Pardoned by Administrator"):
        """Unban a user by Discord User ID: !unban <user_id> [reason]"""
        if not user_id:
            await ctx.send("```\nUsage: !unban <user_id> [reason]\n```")
            return

        guild = ctx.guild
        if not guild:
            await ctx.send("```\nError: Command must be executed within a Discord server.\n```")
            return
        try:
            user = await bot.fetch_user(user_id)
            await guild.unban(user, reason=reason)
            await ctx.send(f"```\n[OK] User unbanned: {user.name} (ID: {user_id})\nReason: {reason}\n```")
        except discord.NotFound:
            await ctx.send(f"```\nError: User ID {user_id} was not found among banned users.\n```")
        except discord.Forbidden:
            await ctx.send("```\nError: Missing 'Ban Members' permission to execute unban.\n```")
        except Exception as e:
            await ctx.send(f"```\nError unbanning user: {e}\n```")

    @bot.command(name="stats")
    async def cmd_stats(ctx: commands.Context):
        """Show current moderation session statistics."""
        lines = [
            "[TOXIGUARD SESSION MODERATION METRICS]",
            f"  Messages Monitored : {SESSION_STATS['messages_scanned']}",
            f"  Messages Flagged   : {SESSION_STATS['messages_flagged']}",
            f"  Messages Clean     : {SESSION_STATS['messages_clean']}",
            f"  Timeouts Issued    : {SESSION_STATS['timeouts_issued']}",
            f"  Bans Issued        : {SESSION_STATS['bans_issued']}",
            "",
            "[ACTIVE THRESHOLDS & POLICY]",
            f"  General Threshold  : {CONFIG['threshold'] * 100:.1f}%",
            f"  Auto-Timeout       : {CONFIG['timeout_threshold'] * 100:.1f}% ({CONFIG['timeout_duration_minutes']}m) [{'ENABLED' if CONFIG['timeout_enabled'] else 'DISABLED'}]",
            f"  Auto-Ban           : {CONFIG['autoban_threshold'] * 100:.1f}% [{'ENABLED' if CONFIG['autoban_enabled'] else 'DISABLED'}]",
            f"  Auto-Moderation    : {'ENABLED' if CONFIG['auto_moderate'] else 'DISABLED'}",
            "",
            "[TRIGGERED CATEGORY BREAKDOWN]",
        ]
        for cat, cnt in SESSION_STATS["categories_triggered"].items():
            lines.append(f"  {cat:<14} : {cnt}")
        await ctx.send("```\n" + "\n".join(lines) + "\n```")

    @bot.command(name="test_cases")
    async def cmd_test_cases(ctx: commands.Context):
        """Run standard test cases to verify pipeline detection and autoban triggers."""
        test_inputs = [
            ("Severe Attack (Auto-Ban Target)", "Shut up you disgusting pig, go die in a ditch, I will murder you."),
            ("Adversarial Leetspeak", "You are a st*pid id1ot and I will k1ll you."),
            ("Polysemous Praise (WSD)", "The guitarist was killing it on stage tonight."),
            ("Cross-Sentence Anaphora", "Alex shoved David. He is violent and should be banned."),
            ("Demographic Identity Neutral", "We attended an academic symposium on Muslim and Jewish history."),
            ("Clean Text", "Please submit your laboratory assignments by Friday afternoon.")
        ]
        lines = ["[BENCHMARK TEST SUITE: 25PEC4CS1 PIPELINE]"]
        for name, text in test_inputs:
            res = run_full_nlp_pipeline(text)
            preds = res["predictions"]
            max_p = max(preds.items(), key=lambda x: x[1])
            is_ban = max_p[1] >= CONFIG["autoban_threshold"]
            is_timeout = not is_ban and max_p[1] >= CONFIG["timeout_threshold"]
            is_flag = not is_ban and not is_timeout and max_p[1] >= CONFIG["threshold"]

            verdict = "AUTOBAN (>=85%)" if is_ban else ("TIMEOUT (>=70%)" if is_timeout else ("FLAGGED (>=50%)" if is_flag else "CLEAN (PASS)"))
            lines.append(f"- Scenario: {name}")
            lines.append(f"  Input   : \"{text}\"")
            lines.append(f"  Verdict : {verdict} ({max_p[0]}: {max_p[1]*100:.1f}%)")
            lines.append("")

        await ctx.send("```\n" + "\n".join(lines) + "\n```")

    # -------------------------------------------------------------------------------------
    # SLASH COMMANDS (discord.app_commands)
    # -------------------------------------------------------------------------------------

    @bot.tree.command(name="analyze", description="Run 6-stage toxicity classification on text")
    @app_commands.describe(text="The message or sentence to analyze")
    async def slash_analyze(interaction: discord.Interaction, text: str):
        result = run_full_nlp_pipeline(text)
        preds = result["predictions"]
        score_block = format_probabilities_block(preds)
        syllabus = result["syllabus_analysis"]
        xai = syllabus["module_6_ethics_and_xai"]["xai_token_attributions"]
        triggers = [t for t in xai if t["impact"] > 0]

        lines = [score_block, ""]
        if triggers:
            lines.append("[DETECTED TRIGGER TOKENS]")
            for t in triggers[:4]:
                lines.append(f"  * '{t['token']}' (Impact: +{t['impact']}) - {t['reason']}")
        else:
            lines.append("[DETECTED TRIGGER TOKENS]\n  None detected (clean text).")

        lines.append("\nRun /explain for full step-by-step pipeline reasoning.")
        await interaction.response.send_message(f"```\n" + "\n".join(lines) + "\n```")

    @bot.tree.command(name="explain", description="Explain how the 6-stage NLP pipeline made its decision")
    @app_commands.describe(text="The message to explain")
    async def slash_explain(interaction: discord.Interaction, text: str):
        result = run_full_nlp_pipeline(text)
        report = format_stage_explanation(text, result)
        chunks = [report[i:i + 1900] for i in range(0, len(report), 1900)]
        await interaction.response.send_message(f"```\n{chunks[0]}\n```")
        for chunk in chunks[1:]:
            await interaction.followup.send(f"```\n{chunk}\n```")

    @bot.tree.command(name="pipeline", description="View 25PEC4CS1 NLP Pipeline Theoretical Architecture")
    async def slash_pipeline(interaction: discord.Interaction):
        doc = format_pipeline_architecture_doc()
        chunks = [doc[i:i + 1900] for i in range(0, len(doc), 1900)]
        await interaction.response.send_message(f"```\n{chunks[0]}\n```")
        for chunk in chunks[1:]:
            await interaction.followup.send(f"```\n{chunk}\n```")

    @bot.tree.command(name="diagnose", description="Check bot setup, permissions and gateway intents")
    async def slash_diagnose(interaction: discord.Interaction):
        guild = interaction.guild
        member = guild.me if guild else None
        perms = interaction.channel.permissions_for(member) if member else None

        lines = [
            "=" * 64,
            "TOXIGUARD BOT CONFIGURATION & PERMISSION DIAGNOSTIC",
            "=" * 64,
            f"Bot Identity      : {bot.user.name} (ID: {bot.user.id})",
            f"Server Guild      : {guild.name if guild else 'DM'}",
            f"Message Content   : {'ENABLED (Active - Reading Chat)' if bot.intents.message_content else 'DISABLED (CRITICAL)'}",
            f"Server Members    : {'ENABLED' if bot.intents.members else 'DISABLED'}",
            f"Manage Messages   : {'OK' if perms and perms.manage_messages else 'MISSING'}",
            f"Ban Members       : {'OK' if perms and perms.ban_members else 'MISSING'}",
            f"Moderate Members  : {'OK' if perms and perms.moderate_members else 'MISSING'}",
            "",
            "[OAUTH2 BOT RE-INVITE URL]",
            f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=1099511753734&scope=bot%20applications.commands",
            "=" * 64
        ]
        await interaction.response.send_message(f"```\n" + "\n".join(lines) + "\n```")

    # -------------------------------------------------------------------------------------
    # CONTEXT MENU / APPS INTEGRATION (Right click message -> Apps -> 'Check Toxicity')
    # Works 100% of the time, even when Message Content Intent is disabled!
    # -------------------------------------------------------------------------------------

    @bot.tree.context_menu(name="Check Toxicity")
    async def context_check_toxicity(interaction: discord.Interaction, message: discord.Message):
        if not message.content.strip():
            await interaction.response.send_message("```\nError: Selected message has no text content.\n```", ephemeral=True)
            return

        result = run_full_nlp_pipeline(message.content)
        preds = result["predictions"]
        score_block = format_probabilities_block(preds)
        max_label, max_score = max(preds.items(), key=lambda x: x[1])

        action = "AUTOBAN (>=85%)" if max_score >= CONFIG["autoban_threshold"] else ("TIMEOUT (>=70%)" if max_score >= CONFIG["timeout_threshold"] else ("FLAGGED (>=50%)" if max_score >= CONFIG["threshold"] else "CLEAN (PASS)"))

        output_lines = [
            f"[MESSAGE TOXICITY ANALYSIS]",
            f"Author : {message.author.name} (ID: {message.author.id})",
            f"Text   : \"{message.content[:80]}\"",
            f"Action : {action}",
            "",
            score_block
        ]
        await interaction.response.send_message(f"```\n" + "\n".join(output_lines) + "\n```", ephemeral=True)

    @bot.tree.context_menu(name="Explain NLP Pipeline")
    async def context_explain_pipeline(interaction: discord.Interaction, message: discord.Message):
        if not message.content.strip():
            await interaction.response.send_message("```\nError: Selected message has no text content.\n```", ephemeral=True)
            return

        result = run_full_nlp_pipeline(message.content)
        report = format_stage_explanation(message.content, result, action_taken="CONTEXT_APP_INSPECTION")
        chunks = [report[i:i + 1900] for i in range(0, len(report), 1900)]
        await interaction.response.send_message(f"```\n{chunks[0]}\n```", ephemeral=True)
        for chunk in chunks[1:]:
            await interaction.followup.send(f"```\n{chunk}\n```", ephemeral=True)

    return bot


# =========================================================================================
# STANDALONE TERMINAL SIMULATION & CLI MODE
# =========================================================================================

def run_cli_simulation():
    print("\n" + "=" * 76)
    print("TOXIGUARD DISCORD BOT SIMULATION CONSOLE (OFFLINE MODE)")
    print("Course: 25PEC4CS1 • Natural Language Processing • Fr. CRCE")
    print("=" * 76)
    print(f"Policy: Flag >= {CONFIG['threshold']*100:.0f}% | Timeout >= {CONFIG['timeout_threshold']*100:.0f}% | Auto-Ban >= {CONFIG['autoban_threshold']*100:.0f}%")
    print("Commands available:")
    print("  !analyze <text>     - Multi-label classification with probability bars")
    print("  !explain <text>     - Full 6-stage step-by-step pipeline reasoning report")
    print("  !inspect <token>    - Morphological, lexical, and WordNet synset inspection")
    print("  !autoban <val|off>  - Configure auto-ban threshold (e.g., !autoban 0.85)")
    print("  !timeout <val|off>  - Configure auto-timeout threshold")
    print("  !diagnose           - Check simulated gateway intents & channel permissions")
    print("  !test_cases         - Run benchmark suite across adversarial & severity tiers")
    print("  !stats              - Session moderation statistics")
    print("  !pipeline           - Theoretical architecture documentation")
    print("  exit                - Quit simulation")
    print("=" * 76 + "\n")

    while True:
        try:
            line = input("discord-bot> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting simulation.")
            break

        if not line:
            continue
        if line.lower() in ("exit", "quit"):
            print("Simulation terminated.")
            break

        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "!analyze":
            if not arg:
                print("Error: Missing text. Usage: !analyze <text>")
                continue
            res = run_full_nlp_pipeline(arg)
            print(format_probabilities_block(res["predictions"]))

        elif cmd == "!explain":
            if not arg:
                print("Error: Missing text. Usage: !explain <text>")
                continue
            res = run_full_nlp_pipeline(arg)
            max_score = max(res["predictions"].values())
            action = "AUTOBAN" if max_score >= CONFIG["autoban_threshold"] else ("TIMEOUT" if max_score >= CONFIG["timeout_threshold"] else ("FLAG" if max_score >= CONFIG["threshold"] else "PERMIT"))
            print(format_stage_explanation(arg, res, action_taken=action))

        elif cmd == "!autoban":
            if not arg:
                print(f"Autoban: {'ENABLED' if CONFIG['autoban_enabled'] else 'DISABLED'} (Threshold: {CONFIG['autoban_threshold']*100:.1f}%)")
            elif arg.lower() in ("off", "disable"):
                CONFIG["autoban_enabled"] = False
                print("[OK] Auto-ban DISABLED.")
            elif arg.lower() in ("on", "enable"):
                CONFIG["autoban_enabled"] = True
                print(f"[OK] Auto-ban ENABLED at {CONFIG['autoban_threshold']*100:.1f}%.")
            else:
                try:
                    val = float(arg)
                    CONFIG["autoban_threshold"] = val
                    CONFIG["autoban_enabled"] = True
                    print(f"[OK] Auto-ban threshold set to {val*100:.1f}%.")
                except ValueError:
                    print("Usage: !autoban <0.50 - 0.99> OR !autoban off")

        elif cmd == "!timeout":
            if not arg:
                print(f"Timeout: {'ENABLED' if CONFIG['timeout_enabled'] else 'DISABLED'} (Threshold: {CONFIG['timeout_threshold']*100:.1f}%, Duration: {CONFIG['timeout_duration_minutes']}m)")
            else:
                try:
                    val = float(arg)
                    CONFIG["timeout_threshold"] = val
                    CONFIG["timeout_enabled"] = True
                    print(f"[OK] Timeout threshold set to {val*100:.1f}%.")
                except ValueError:
                    print("Usage: !timeout <0.50 - 0.90> OR !timeout off")

        elif cmd == "!diagnose":
            print("""
================================================================
TOXIGUARD BOT CONFIGURATION & PERMISSION DIAGNOSTIC (SIMULATED)
================================================================
Bot Identity      : ToxiGuard (Offline Simulator)
Message Content   : SIMULATED (Terminal reads raw user text input)
Auto-Ban Threshold: 85.0% (ENABLED)
Timeout Threshold : 70.0% (Duration: 15m)
General Threshold : 50.0%
================================================================
""")

        elif cmd == "!inspect":
            if not arg:
                print("Error: Missing token. Usage: !inspect <token>")
                continue
            token = arg.strip().split()[0]
            morph = analyze_morphology(token)
            lexicon_hits = TOXIC_LEXICON.get(token.lower(), [])
            res = run_full_nlp_pipeline(token)
            s2 = res["syllabus_analysis"]["module_2_word_level"]
            norm = s2["adversarial_edit_distance"][0] if s2["adversarial_edit_distance"] else {}
            wsd = res["syllabus_analysis"]["module_4_semantic_analysis"]["wordnet_lesk_wsd"]
            print(f"[TOKEN: '{token}']")
            print(f"  Normalized  : '{norm.get('normalized', token)}' ({norm.get('method', 'None')})")
            print(f"  Lemma       : '{morph.get('lemma', token)}'")
            print(f"  Stem        : '{morph.get('porter_stem', token)}'")
            print(f"  Morphology  : {morph.get('morphology_type', 'N/A')}")
            print(f"  Lexicon     : {', '.join(lexicon_hits) if lexicon_hits else 'Not in raw toxic lexicon'}")
            if wsd:
                print(f"  WordNet Sense: {wsd[0]['selected_synset']} ({wsd[0]['sense_type']}) - {wsd[0]['gloss']}")

        elif cmd == "!test_cases":
            test_inputs = [
                ("Severe Attack (Auto-Ban Target)", "Shut up you disgusting pig, go die in a ditch, I will murder you."),
                ("Adversarial Leetspeak", "You are a st*pid id1ot and I will k1ll you."),
                ("Polysemous Praise (WSD)", "The guitarist was killing it on stage tonight."),
                ("Cross-Sentence Anaphora", "Alex shoved David. He is violent and should be banned."),
                ("Demographic Identity Neutral", "We attended an academic symposium on Muslim and Jewish history."),
                ("Clean Text", "Please submit your laboratory assignments by Friday afternoon.")
            ]
            for name, text in test_inputs:
                res = run_full_nlp_pipeline(text)
                preds = res["predictions"]
                max_p = max(preds.items(), key=lambda x: x[1])
                is_ban = max_p[1] >= CONFIG["autoban_threshold"]
                is_timeout = not is_ban and max_p[1] >= CONFIG["timeout_threshold"]
                is_flag = not is_ban and not is_timeout and max_p[1] >= CONFIG["threshold"]

                verdict = "AUTOBAN (>=85%)" if is_ban else ("TIMEOUT (>=70%)" if is_timeout else ("FLAGGED (>=50%)" if is_flag else "CLEAN (PASS)"))
                print(f"[{name}]")
                print(f"  Input   : \"{text}\"")
                print(f"  Verdict : {verdict} ({max_p[0]}: {max_p[1]*100:.1f}%)\n")

        elif cmd == "!stats":
            print(f"Scanned: {SESSION_STATS['messages_scanned']} | Flagged: {SESSION_STATS['messages_flagged']} | Clean: {SESSION_STATS['messages_clean']} | Bans: {SESSION_STATS['bans_issued']} | Timeouts: {SESSION_STATS['timeouts_issued']}")

        elif cmd == "!pipeline":
            print(format_pipeline_architecture_doc())

        else:
            res = run_full_nlp_pipeline(line)
            max_score = max(res["predictions"].values())
            action = "AUTOBAN (>=85%)" if max_score >= CONFIG["autoban_threshold"] else ("TIMEOUT (>=70%)" if max_score >= CONFIG["timeout_threshold"] else ("FLAGGED" if max_score >= CONFIG["threshold"] else "CLEAN"))
            print(f"Action: {action}")
            print(format_probabilities_block(res["predictions"]))


def print_privileged_intents_guide():
    print("\n" + "=" * 80)
    print("[CRITICAL SETUP NOTICE] DISCORD PRIVILEGED GATEWAY INTENTS REQUIRED")
    print("=" * 80)
    print("Why is the bot not analyzing messages typed in chat?")
    print("1. Discord by default blocks bots from reading chat text unless you explicitly")
    print("   enable 'MESSAGE CONTENT INTENT' in the Discord Developer Portal.")
    print("2. Without this switch, Discord delivers empty text (\"\") to the bot.")
    print("\nHOW TO FIX IN 20 SECONDS:")
    print("  Step 1: Open: https://discord.com/developers/applications/")
    print("  Step 2: Select your Application -> Click 'Bot' in the left menu.")
    print("  Step 3: Scroll down to 'Privileged Gateway Intents'.")
    print("  Step 4: Toggle ON both switches:")
    print("          [x] MESSAGE CONTENT INTENT  (Required to read and analyze chat)")
    print("          [x] SERVER MEMBERS INTENT   (Required for autoban and timeout)")
    print("  Step 5: Click 'Save Changes' at the bottom of the page.")
    print("  Step 6: Restart the bot (uv run start.py).")
    print("=" * 80 + "\n")


def run_discord_gateway(token: str):
    """
    Connects to Discord Gateway with progressive intent fallback:
    1. Full Intents (Message Content + Server Members)
    2. Message Content only (Server Members disabled)
    3. Minimal (Slash & Context Menu Apps only)
    """
    intent_tiers = [
        ("Full Intents (Message Content + Server Members)", True, True),
        ("Fallback (Message Content only; Members disabled)", True, False),
        ("Minimal (Slash & Context Apps only; Privileged disabled)", False, False),
    ]

    for label, enable_content, enable_members in intent_tiers:
        try:
            intents = discord.Intents.default()
            intents.messages = True
            intents.guilds = True
            intents.message_content = enable_content
            intents.members = enable_members

            if not enable_content:
                print("\n" + "!" * 80)
                print("[WARNING] RUNNING WITHOUT MESSAGE CONTENT INTENT")
                print("Discord will censor message text. The bot will NOT be able to auto-moderate chat.")
                print("Enable 'MESSAGE CONTENT INTENT' in https://discord.com/developers/applications/ under Bot tab.")
                print("!" * 80 + "\n")

            print(f"[START] Connecting ToxiGuard Discord Bot ({label})...")
            active_bot = create_bot(intents)
            active_bot.run(token)
            return
        except discord.errors.PrivilegedIntentsRequired:
            print(f"[WARN] Discord Gateway rejected {label} (Privileged Intents disabled in portal).")
            continue
        except discord.errors.LoginFailure as e:
            print(f"[ERROR] Discord Login Failure: Invalid bot token ({e}).")
            print("[INFO] Please verify DISCORD_BOT_TOKEN in your .env file.")
            break
        except Exception as e:
            print(f"[ERROR] Discord Bot error: {e}")
            break

    # If all intent configurations failed
    print_privileged_intents_guide()
    print("[INFO] Web interface and Flask NLP API remain fully operational on http://127.0.0.1:5000.")
    print("[INFO] Launching interactive simulation console so bot commands can still be evaluated in terminal...\n")
    try:
        run_cli_simulation()
    except Exception:
        while True:
            time.sleep(3600)


def main():
    parser = argparse.ArgumentParser(description="ToxiGuard Discord Bot & NLP Pipeline Explainer")
    parser.add_argument("--token", type=str, default=None, help="Discord Bot Token (or set DISCORD_BOT_TOKEN in .env)")
    parser.add_argument("--simulate", action="store_true", help="Run interactive terminal simulation mode")
    parser.add_argument("--test", type=str, default=None, help="Directly test !analyze on a string")
    parser.add_argument("--explain", type=str, default=None, help="Directly test !explain on a string")
    parser.add_argument("--autoban-threshold", type=float, default=None, help="Override autoban threshold (e.g. 0.85)")

    args = parser.parse_args()

    if args.autoban_threshold:
        CONFIG["autoban_threshold"] = args.autoban_threshold

    if args.simulate:
        run_cli_simulation()
        return

    if args.test:
        res = run_full_nlp_pipeline(args.test)
        print(format_probabilities_block(res["predictions"]))
        return

    if args.explain:
        res = run_full_nlp_pipeline(args.explain)
        max_score = max(res["predictions"].values())
        action = "AUTOBAN" if max_score >= CONFIG["autoban_threshold"] else ("TIMEOUT" if max_score >= CONFIG["timeout_threshold"] else ("FLAG" if max_score >= CONFIG["threshold"] else "PERMIT"))
        print(format_stage_explanation(args.explain, res, action_taken=action))
        return

    token = args.token or os.environ.get("DISCORD_BOT_TOKEN")
    if not token or token.strip() in ("your_discord_bot_token_here", ""):
        print("[INFO] No valid DISCORD_BOT_TOKEN detected in environment or .env file.")
        print("[INFO] Launching interactive simulation mode for testing commands & autoban logic.")
        print("[INFO] (To run with real Discord, set DISCORD_BOT_TOKEN in .env or pass --token)\n")
        run_cli_simulation()
        return

    if not HAS_DISCORD:
        print("[ERROR] discord.py is not installed. Install via: uv add discord.py")
        sys.exit(1)

    run_discord_gateway(token)


if __name__ == "__main__":
    main()
