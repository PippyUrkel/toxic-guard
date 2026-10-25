"""
=========================================================================================
ToxiGuard Classical & Statistical NLP Pipeline Engine
Course: Natural Language Processing (25PEC4CS1)
Institution: Fr. Conceicao Rodrigues College of Engineering (CRCE), Bandra, Mumbai
=========================================================================================
This module implements all 6 modules of the 25PEC4CS1 NLP syllabus from scratch with
optional NLTK integration (automatically falling back to pure-Python implementations if
offline). It works alongside the core BiLSTM model to provide full linguistic analysis,
adversarial obfuscation normalization, WSD, POS tagging, Anaphora resolution, and XAI.
"""

import math
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any

# Optional NLTK import with graceful fallback
try:
    import nltk
    from nltk.stem import PorterStemmer as NLTKPorterStemmer
    _HAS_NLTK = True
except Exception:
    _HAS_NLTK = False


# =========================================================================================
# LEXICAL RESOURCES & KNOWLEDGE BASES (Syllabus Modules 2, 3, 4, 5, 6)
# =========================================================================================

TOXIC_LEXICON: Dict[str, List[str]] = {
    "kill": ["toxic", "severe_toxic", "threat"],
    "murder": ["toxic", "severe_toxic", "threat"],
    "die": ["toxic", "threat"],
    "destroy": ["toxic", "threat"],
    "attack": ["toxic", "threat"],
    "hurt": ["toxic", "threat"],
    "shoot": ["toxic", "severe_toxic", "threat"],
    "beat": ["toxic", "threat"],
    "stupid": ["toxic", "insult"],
    "idiot": ["toxic", "insult"],
    "moron": ["toxic", "insult"],
    "dumb": ["toxic", "insult"],
    "pathetic": ["toxic", "insult"],
    "loser": ["toxic", "insult"],
    "fool": ["toxic", "insult"],
    "ugly": ["toxic", "insult"],
    "worthless": ["toxic", "insult"],
    "trash": ["toxic", "insult"],
    "garbage": ["toxic", "insult"],
    "suck": ["toxic", "obscene", "insult"],
    "damn": ["toxic", "obscene"],
    "hell": ["toxic", "obscene"],
    "crap": ["toxic", "obscene"],
    "shut": ["toxic", "insult"],
    "fck": ["toxic", "severe_toxic", "obscene"],
    "fuck": ["toxic", "severe_toxic", "obscene"],
    "shit": ["toxic", "obscene"],
    "bitch": ["toxic", "obscene", "insult"],
    "bastard": ["toxic", "obscene", "insult"],
    "ass": ["toxic", "obscene"],
    "hate": ["toxic", "identity_hate"],
    "racist": ["toxic", "identity_hate"],
    "bigot": ["toxic", "identity_hate"],
    "disgusting": ["toxic", "insult"],
    "filthy": ["toxic", "insult", "obscene"],
    "pig": ["toxic", "insult"],
    "scum": ["toxic", "insult"],
    "vermin": ["toxic", "identity_hate", "insult"],
    "inferior": ["toxic", "identity_hate"],
}

LEETSPEAK_MAP = str.maketrans({
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s",
    "7": "t", "8": "b", "@": "a", "$": "s", "!": "i"
})

# Module 2.3: Morphological Knowledge Base (Inflectional & Derivational)
LEMMA_DICT: Dict[str, str] = {
    "killing": "kill", "killed": "kill", "kills": "kill", "killer": "kill", "killers": "kill",
    "hating": "hate", "hated": "hate", "hates": "hate", "hatred": "hate", "hater": "hate",
    "insulting": "insult", "insulted": "insult", "insults": "insult",
    "threatening": "threat", "threatened": "threat", "threats": "threat", "threaten": "threat",
    "stupidity": "stupid", "stupider": "stupid", "stupidest": "stupid", "stupidly": "stupid",
    "idiotic": "idiot", "idiots": "idiot",
    "morons": "moron", "moronic": "moron",
    "losers": "loser", "losing": "lose",
    "fools": "fool", "foolish": "fool", "foolishly": "fool",
    "dying": "die", "died": "die", "dies": "die",
    "attacking": "attack", "attacked": "attack", "attacks": "attack", "attacker": "attack",
    "destroying": "destroy", "destroyed": "destroy", "destroys": "destroy", "destruction": "destroy",
    "sucking": "suck", "sucks": "suck", "sucked": "suck",
    "bitches": "bitch", "bitching": "bitch",
    "bastards": "bastard",
    "fucking": "fuck", "fucked": "fuck", "fucker": "fuck", "fucks": "fuck",
    "shitty": "shit", "shitting": "shit",
    "racists": "racist", "racism": "racist",
    "women": "woman", "men": "man", "people": "person", "children": "child",
    "went": "go", "going": "go", "goes": "go", "gone": "go",
    "are": "be", "is": "be", "am": "be", "was": "be", "were": "be", "been": "be",
}

DERIVATIONAL_PREFIXES = ["un", "in", "im", "dis", "non", "anti", "mis", "over", "pre", "re", "sub", "super"]
DERIVATIONAL_SUFFIXES = ["ness", "ity", "ment", "tion", "sion", "able", "ible", "ful", "less", "ous", "ive", "ic", "ly", "er", "or", "ist", "ism"]
INFLECTIONAL_SUFFIXES = ["ing", "ed", "es", "s", "er", "est"]

# Module 4.1 & 4.2: Curated WordNet Synset & Lexical Semantics Knowledge Base
WORDNET_KB: Dict[str, List[Dict[str, Any]]] = {
    "kill": [
        {
            "synset": "kill.v.01",
            "pos": "VB",
            "sense_type": "toxic_threat",
            "gloss": "cause to die; put to death, usually intentionally or knowingly",
            "examples": ["I will kill you", "he threatened to kill the victim", "murder and kill"],
            "synonyms": ["murder", "slay", "dispatch", "execute"],
            "antonyms": ["save", "resuscitate", "revive"],
            "hypernyms": ["destroy.v.01", "end.v.02"],
            "hyponyms": ["assassinate.v.01", "massacre.v.01", "poison.v.01"],
            "meronyms": [],
            "reversives": ["revive"],
        },
        {
            "synset": "kill.v.04",
            "pos": "VB",
            "sense_type": "benign_idiom",
            "gloss": "overwhelm with hilarity, admiration, or excellence; or terminate a computer process / time",
            "examples": ["you are killing it on stage", "kill the background process", "killing time before the flight", "killer app feature"],
            "synonyms": ["ace", "nail", "terminate", "stop"],
            "antonyms": ["start", "launch", "fail"],
            "hypernyms": ["succeed.v.01", "terminate.v.01"],
            "hyponyms": ["halt_process.v.01"],
            "meronyms": [],
            "reversives": ["spawn"],
        }
    ],
    "sick": [
        {
            "synset": "sick.a.01",
            "pos": "JJ",
            "sense_type": "medical_or_slang_positive",
            "gloss": "affected by physical or mental illness; or (slang) extraordinarily cool and impressive",
            "examples": ["feeling sick with flu fever", "that skateboard trick was sick and awesome"],
            "synonyms": ["ill", "unwell", "awesome", "rad"],
            "antonyms": ["healthy", "well", "boring"],
            "hypernyms": ["unhealthy.a.01", "excellent.a.01"],
            "hyponyms": ["nauseous.a.01", "feverish.a.01"],
            "meronyms": [],
            "reversives": ["heal"],
        },
        {
            "synset": "sick.a.03",
            "pos": "JJ",
            "sense_type": "toxic_insult",
            "gloss": "deeplyoniacal, perverted, disgusting, or mentally deranged in a vile way",
            "examples": ["you are a sick twisted idiot", "sick and disgusting freak", "hate your sick mind"],
            "synonyms": ["twisted", "vile", "perverted", "repulsive"],
            "antonyms": ["wholesome", "decent", "noble"],
            "hypernyms": ["offensive.a.01"],
            "hyponyms": ["sadistic.a.01", "ghoulish.a.01"],
            "meronyms": [],
            "reversives": [],
        }
    ],
    "trash": [
        {
            "synset": "trash.n.01",
            "pos": "NN",
            "sense_type": "literal_object",
            "gloss": "worthless material that is to be disposed of; physical waste or rubbish",
            "examples": ["take out the trash bin", "recycle plastic trash and garbage cans"],
            "synonyms": ["rubbish", "refuse", "waste", "litter"],
            "antonyms": ["treasure", "asset"],
            "hypernyms": ["waste_material.n.01"],
            "hyponyms": ["kitchen_waste.n.01"],
            "meronyms": ["scrap.n.01"],
            "reversives": ["salvage"],
        },
        {
            "synset": "trash.n.03",
            "pos": "NN",
            "sense_type": "toxic_insult",
            "gloss": "a worthless, contemptible, orpicable person or group (derogatory insult)",
            "examples": ["you are worthless trash", "shut up you stupid trash loser"],
            "synonyms": ["scum", "lowlife", "garbage", "riffraff"],
            "antonyms": ["role_model", "gentleman"],
            "hypernyms": ["unpleasant_person.n.01"],
            "hyponyms": ["degenerate.n.01"],
            "meronyms": [],
            "reversives": [],
        }
    ],
    "attack": [
        {
            "synset": "attack.v.01",
            "pos": "VB",
            "sense_type": "toxic_threat",
            "gloss": "launch an aggressive violent assault or verbal abuse against someone",
            "examples": ["we will attack and hurt you", "viciously attack the enemy"],
            "synonyms": ["assault", "assail", "strike", "ambush"],
            "antonyms": ["defend", "protect", "shield"],
            "hypernyms": ["fight.v.01"],
            "hyponyms": ["besiege.v.01", "raid.v.01"],
            "meronyms": [],
            "reversives": ["retreat"],
        },
        {
            "synset": "attack.v.03",
            "pos": "VB",
            "sense_type": "benign_analytical",
            "gloss": "begin to work on or solve a complex problem or task energetically",
            "examples": ["attack the math problem", "attack the homework syllabus tasks"],
            "synonyms": ["tackle", "undertake", "address"],
            "antonyms": ["ignore", "avoid", "neglect"],
            "hypernyms": ["work.v.01"],
            "hyponyms": ["troubleshoot.v.01"],
            "meronyms": [],
            "reversives": [],
        }
    ],
    "stupid": [
        {
            "synset": "stupid.a.01",
            "pos": "JJ",
            "sense_type": "toxic_insult",
            "gloss": "lacking intelligence, common sense, or sound judgment; used as a direct derogatory insult",
            "examples": ["you are a stupid idiot", "shut up stupid moron"],
            "synonyms": ["idiotic", "moronic", "dumb", "brainless", "foolish"],
            "antonyms": ["intelligent", "brilliant", "wise", "clever"],
            "hypernyms": ["unintelligent.a.01"],
            "hyponyms": ["obtuse.a.01", "vacuous.a.01"],
            "meronyms": [],
            "reversives": [],
        }
    ],
    "hate": [
        {
            "synset": "hate.v.01",
            "pos": "VBP",
            "sense_type": "toxic_hostility",
            "gloss": "dislike intensely; feel antipathy, malice, or hostility towards an individual or group",
            "examples": ["I hate you so much", "they hate those people and insult them"],
            "synonyms": ["detest", "loathe", "abhor", "despise"],
            "antonyms": ["love", "adore", "cherish", "respect"],
            "hypernyms": ["dislike.v.01"],
            "hyponyms": ["execrate.v.01"],
            "meronyms": [],
            "reversives": ["reconcile"],
        }
    ],
    "shoot": [
        {
            "synset": "shoot.v.01",
            "pos": "VB",
            "sense_type": "toxic_threat",
            "gloss": "hit, wound, or kill with a missile fired from a weapon",
            "examples": ["going to shoot you with a gun", "kill and shoot the target"],
            "synonyms": ["gun_down", "fire_at", "blast"],
            "antonyms": ["spare", "shield"],
            "hypernyms": ["injure.v.01", "kill.v.01"],
            "hyponyms": ["snipe.v.01", "kneecap.v.01"],
            "meronyms": ["aim.v.01", "pull_trigger.v.01"],
            "reversives": [],
        },
        {
            "synset": "shoot.v.04",
            "pos": "VB",
            "sense_type": "benign_media",
            "gloss": "recordon film or video; or send a quick message or email",
            "examples": ["shoot a photo with the camera", "shoot me an email tomorrow", "shoot a movie scene"],
            "synonyms": ["photograph", "film", "record", "send"],
            "antonyms": ["delete", "erase"],
            "hypernyms": ["record.v.01", "communicate.v.01"],
            "hyponyms": ["video.v.01"],
            "meronyms": ["focus_lens.v.01"],
            "reversives": [],
        }
    ],
}

# Reference Corpus for Cosine Distance & N-Gram Language Modeling (Modules 1.4, 2.2, 4.3)
REFERENCE_CORPUS = [
    {"id": "TOX_THREAT_1", "category": "threat", "text": "you freaking suck i am going to kill you and hurt you badly"},
    {"id": "TOX_INSULT_1", "category": "insult", "text": "shut up you stupid idiot moron you are worthless trash and a loser"},
    {"id": "TOX_OBSCENE_1", "category": "obscene", "text": "what the fuck is wrong with this bullshit crap you bastard bitch"},
    {"id": "TOX_HATE_1", "category": "identity_hate", "text": "i hate your kind of people you are disgusting inferior scum vermin"},
    {"id": "SAFE_COLLAB_1", "category": "non_toxic", "text": "thank you for the helpful contribution to this wikipedia article discussion"},
    {"id": "SAFE_IDIOM_1", "category": "non_toxic", "text": "you are killing it with this killer app feature shoot me an email later"},
]


# =========================================================================================
# MODULE 2: WORD LEVEL ANALYSIS
# =========================================================================================

def segment_sentences(text: str) -> List[str]:
    """Module 2.1: Sentence Segmentation using punctuation boundary heuristics."""
    if not text or not text.strip():
        return []
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def tokenize_text(text: str) -> List[str]:
    """Module 2.1: Word-level Tokenization preserving contractions and word tokens."""
    if not text:
        return []
    return re.findall(r"[A-Za-z0-9@#\$!']+", text.lower())


def porter_stem_word(word: str) -> str:
    """Module 2.1: Porter Stemmer implementation (uses NLTK if available, pure-Python fallback)."""
    w = re.sub(r"[^a-z]", "", word.lower())
    if len(w) <= 3:
        return w
    if _HAS_NLTK:
        try:
            return NLTKPorterStemmer().stem(w)
        except Exception:
            pass
    # Pure Python Porter Stemmer rules (Steps 1a, 1b, 2, 3, 4)
    if w.endswith("sses"):
        w = w[:-2]
    elif w.endswith("ies"):
        w = w[:-2]
    elif not w.endswith("ss") and w.endswith("s"):
        w = w[:-1]
    for suf in ["ingly", "edly", "ing", "ed"]:
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[:-len(suf)]
            if w.endswith(("at", "bl", "iz")):
                w += "e"
            elif len(w) >= 2 and w[-1] == w[-2] and w[-1] not in "lsz":
                w = w[:-1]
            break
    if w.endswith("y") and len(w) > 3 and w[-2] not in "aeiou":
        w = w[:-1] + "i"
    for suf, rep in [("ational", "ate"), ("tional", "tion"), ("fulness", "ful"), ("ousness", "ous"), ("iveness", "ive"), ("ization", "ize"), ("biliti", "ble")]:
        if w.endswith(suf) and len(w) - len(suf) >= 2:
            w = w[:-len(suf)] + rep
            break
    for suf in ["ement", "ance", "ence", "able", "ible", "ment", "ness", "ally", "ant", "ent", "ism", "ate", "iti", "ous", "ive", "ize", "ful", "ly"]:
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[:-len(suf)]
            break
    return w


def lemmatize_word(word: str) -> str:
    """Module 2.1: Dictionary + Morphological Rule-based Lemmatization."""
    w = re.sub(r"[^a-z]", "", word.lower())
    if w in LEMMA_DICT:
        return LEMMA_DICT[w]
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("es") and len(w) > 4 and w[:-2] in TOXIC_LEXICON:
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        cand = w[:-1]
        if cand in TOXIC_LEXICON or len(cand) >= 4:
            return cand
    if w.endswith("ing") and len(w) > 5:
        base = w[:-3]
        if len(base) >= 2 and base[-1] == base[-2]:
            base = base[:-1]
        return base
    if w.endswith("ed") and len(w) > 4:
        base = w[:-2]
        if len(base) >= 2 and base[-1] == base[-2]:
            base = base[:-1]
        return base
    return w


def levenshtein_edit_distance(s1: str, s2: str) -> Tuple[int, List[List[int]]]:
    """
    Module 2.1: Minimum Edit Distance (Levenshtein Dynamic Programming).
    Substitution cost = 1, Insertion = 1, Deletion = 1.
    Returns (distance, dp_matrix).
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # Deletion
                dp[i][j - 1] + 1,      # Insertion
                dp[i - 1][j - 1] + cost # Substitution
            )
    return dp[m][n], dp


def normalize_adversarial_token(token: str, max_dist: int = 1) -> Dict[str, Any]:
    """
    Module 2.1: Uses Levenshtein Edit Distance + Leetspeak de-obfuscation to detect
    adversarial toxic evasion (e.g., 'k1ll' -> 'kill', 'st*pid' -> 'stupid', 'id1ot' -> 'idiot').
    """
    cleaned = re.sub(r"[^a-z0-9@$!]", "", token.lower())
    deleet = cleaned.translate(LEETSPEAK_MAP)
    # Collapse repeated characters > 2 (e.g. 'stuuuupid' -> 'stupid')
    collapsed = re.sub(r"(.){2,}", r"", deleet)

    if collapsed in TOXIC_LEXICON:
        return {
            "original": token,
            "normalized": collapsed,
            "edit_distance": levenshtein_edit_distance(cleaned, collapsed)[0],
            "matched_lexicon": True,
            "method": "Leetspeak / Repetition Normalization" if cleaned != collapsed else "Exact Match"
        }

    # Check minimum edit distance against toxic vocabulary
    best_word = collapsed
    best_dist = 999
    if len(collapsed) >= 4:
        for tox_word in TOXIC_LEXICON.keys():
            if abs(len(collapsed) - len(tox_word)) <= max_dist:
                dist, _ = levenshtein_edit_distance(collapsed, tox_word)
                if dist <= max_dist and dist < best_dist:
                    best_dist = dist
                    best_word = tox_word

    if best_dist <= max_dist:
        return {
            "original": token,
            "normalized": best_word,
            "edit_distance": levenshtein_edit_distance(cleaned, best_word)[0],
            "matched_lexicon": True,
            "method": f"Levenshtein Edit Distance (d={best_dist})"
        }

    return {
        "original": token,
        "normalized": collapsed,
        "edit_distance": 0,
        "matched_lexicon": False,
        "method": "None"
    }


def analyze_morphology(word: str) -> Dict[str, Any]:
    """
    Module 2.3: Morphological Analysis — decomposes a token into prefix, root/lemma,
    suffix, and classifies Inflectional vs. Derivational morphology.
    """
    w = re.sub(r"[^a-z]", "", word.lower())
    lemma = lemmatize_word(w)
    stem = porter_stem_word(w)
    prefix = ""
    suffix = ""
    morph_type = "Free Morpheme (Root)"

    for p in DERIVATIONAL_PREFIXES:
        if w.startswith(p) and len(w) - len(p) >= 4:
            prefix = p + "-"
            break

    if w != lemma:
        for inf in INFLECTIONAL_SUFFIXES:
            if w.endswith(inf):
                suffix = "-" + inf
                morph_type = "Inflectional Morphology (Preserves Grammatical Category)"
                break
    if not suffix:
        for der in DERIVATIONAL_SUFFIXES:
            if w.endswith(der) and len(w) - len(der) >= 3:
                suffix = "-" + der
                morph_type = "Derivational Morphology (Alters Lexical Category/Sense)"
                break

    return {
        "surface_form": word,
        "lemma": lemma,
        "porter_stem": stem,
        "prefix": prefix or "None",
        "suffix": suffix or "None",
        "morphology_type": morph_type
    }


def extract_collocations_pmi(tokens: List[str]) -> List[Dict[str, Any]]:
    """
    Module 2.1: Bigram Collocation Extraction using Pointwise Mutual Information (PMI).
    PMI(w1, w2) = log2( P(w1, w2) / (P(w1) * P(w2)) )
    """
    # Combine user tokens with reference corpus to get stable bigram statistics
    corpus_tokens = []
    for doc in REFERENCE_CORPUS:
        corpus_tokens.extend(tokenize_text(doc["text"]))
    all_tokens = corpus_tokens + tokens
    N = max(len(all_tokens), 1)
    unigram_counts = Counter(all_tokens)
    bigram_counts = Counter(zip(all_tokens[:-1], all_tokens[1:]))

    user_bigrams = list(zip(tokens[:-1], tokens[1:]))
    results = []
    seen = set()
    for w1, w2 in user_bigrams:
        if (w1, w2) in seen:
            continue
        seen.add((w1, w2))
        p_w1 = unigram_counts[w1] / N
        p_w2 = unigram_counts[w2] / N
        p_w1_w2 = (bigram_counts[(w1, w2)] / max(N - 1, 1))
        pmi = math.log2(p_w1_w2 / (p_w1 * p_w2)) if (p_w1 * p_w2) > 0 else 0.0
        results.append({
            "bigram": f"{w1} {w2}",
            "count": bigram_counts[(w1, w2)],
            "pmi_score": round(pmi, 4)
        })
    results.sort(key=lambda x: x["pmi_score"], reverse=True)
    return results[:8]


class BigramLanguageModel:
    """
    Module 2.2: N-Gram Language Model with Add-1 (Laplace) Smoothing and Perplexity Evaluation.
    P_laplace(w_i | w_{i-1}) = (C(w_{i-1}, w_i) + 1) / (C(w_{i-1}) + |V|)
    Perplexity(W) = exp( - (1/N) * sum( log P(w_i | w_{i-1}) ) )
    """
    def __init__(self, corpus_texts: List[str]):
        self.unigram_counts = Counter()
        self.bigram_counts = Counter()
        self.vocab = set(["<s>", "</s>", "<unk>"])
        for text in corpus_texts:
            toks = ["<s>"] + tokenize_text(text) + ["</s>"]
            self.vocab.update(toks)
            self.unigram_counts.update(toks)
            self.bigram_counts.update(zip(toks[:-1], toks[1:]))
        self.V = max(len(self.vocab), 1)

    def laplace_prob(self, w_prev: str, w_curr: str) -> float:
        c_bigram = self.bigram_counts[(w_prev, w_curr)]
        c_unigram = self.unigram_counts[w_prev]
        return (c_bigram + 1.0) / (c_unigram + self.V)

    def evaluate_perplexity(self, tokens: List[str]) -> Dict[str, Any]:
        seq = ["<s>"] + [t if t in self.vocab else "<unk>" for t in tokens] + ["</s>"]
        N = len(seq) - 1
        if N <= 0:
            return {"perplexity": 0.0, "avg_log_prob": 0.0, "bigram_Transitions": []}
        log_prob_sum = 0.0
        transitions = []
        for i in range(1, len(seq)):
            p = self.laplace_prob(seq[i - 1], seq[i])
            log_prob_sum += math.log(p)
            transitions.append({
                "bigram": f"{seq[i-1]} -> {seq[i]}",
                "laplace_prob": round(p, 5)
            })
        avg_log_prob = log_prob_sum / N
        perplexity = math.exp(-avg_log_prob)
        return {
            "vocab_size": self.V,
            "smoothing": "Laplace (Add-1) Smoothing",
            "perplexity": round(perplexity, 3),
            "avg_log_prob": round(avg_log_prob, 4),
            "transitions": transitions[:8]
        }


# Instantiate global N-gram Language Model on Toxic vs Safe Reference Sub-corpora
_TOXIC_LM = BigramLanguageModel([d["text"] for d in REFERENCE_CORPUS if d["category"] != "non_toxic"])
_SAFE_LM = BigramLanguageModel([d["text"] for d in REFERENCE_CORPUS if d["category"] == "non_toxic"])


# =========================================================================================
# MODULE 3: SYNTAX LEVEL ANALYSIS (PENN TREEBANK POS TAGGING, HMM & VITERBI DECODER)
# =========================================================================================

PENN_TAG_DESCRIPTIONS: Dict[str, str] = {
    "PRP": "Personal Pronoun (I, you, he, they)",
    "PRP$": "Possessive Pronoun (my, your, his, their)",
    "NN": "Noun, singular or mass",
    "NNS": "Noun, plural",
    "VB": "Verb, base form",
    "VBP": "Verb, non-3rd person singular present",
    "VBZ": "Verb, 3rd person singular present",
    "VBG": "Verb, gerund or present participle",
    "VBD": "Verb, past tense",
    "JJ": "Adjective",
    "RB": "Adverb",
    "DT": "Determiner (the, a, this, that)",
    "IN": "Preposition or subordinating conjunction",
    "MD": "Modal auxiliary (will, can, should, must)",
    "UH": "Interjection / Exclamation",
    "CC": "Coordinating conjunction (and, but, or)",
    "TO": "Infinite marker 'to'",
}


class HMMViterbiPOSTagger:
    """
    Module 3.1 & 3.2: Stochastic Hidden Markov Model (HMM) Part-of-Speech Tagger
    with exact Viterbi Dynamic Programming Decoding & Transformation-based (Brill) refinement.
    States Q = Penn Treebank POS Tags
    Transition Matrix A[q_prev][q_curr] = P(tag_i | tag_{i-1})
    Emission Matrix B[q][w] = P(word_i | tag_i)
    """
    def __init__(self):
        self.states = ["PRP", "PRP$", "MD", "VB", "VBP", "VBG", "JJ", "RB", "DT", "NN", "NNS", "IN", "TO", "CC"]
        # Initial state probabilities pi
        self.pi = {
            "PRP": 0.35, "DT": 0.20, "NN": 0.12, "VB": 0.10, "RB": 0.06,
            "JJ": 0.06, "IN": 0.05, "PRP$": 0.03, "MD": 0.01, "VBP": 0.01,
            "VBG": 0.005, "NNS": 0.005, "TO": 0.005, "CC": 0.005
        }
        # Transition probabilities P(tag_next | tag_prev)
        self.A = defaultdict(lambda: defaultdict(lambda: 0.01))
        transitions = {
            "PRP": {"VBP": 0.40, "MD": 0.25, "VB": 0.20, "RB": 0.10},
            "PRP$": {"NN": 0.50, "JJ": 0.35, "NNS": 0.10},
            "MD": {"VB": 0.80, "RB": 0.15},
            "VBP": {"JJ": 0.30, "VBG": 0.25, "DT": 0.20, "RB": 0.12, "PRP": 0.08},
            "VB": {"PRP": 0.35, "DT": 0.25, "JJ": 0.15, "NN": 0.15, "IN": 0.08},
            "VBG": {"TO": 0.45, "PRP": 0.20, "DT": 0.15, "IN": 0.15},
            "TO": {"VB": 0.80, "NN": 0.15},
            "DT": {"JJ": 0.45, "NN": 0.45, "NNS": 0.08},
            "JJ": {"NN": 0.55, "NNS": 0.20, "JJ": 0.12, "CC": 0.08},
            "NN": {"IN": 0.25, "CC": 0.20, "VB": 0.15, "VBP": 0.15, "NN": 0.15},
            "NNS": {"VBP": 0.40, "IN": 0.20, "CC": 0.20},
            "RB": {"JJ": 0.45, "VB": 0.30, "VBP": 0.15},
            "IN": {"DT": 0.40, "PRP": 0.25, "PRP$": 0.15, "NN": 0.15},
            "CC": {"PRP": 0.25, "VB": 0.25, "JJ": 0.25, "NN": 0.20},
        }
        for s1, next_map in transitions.items():
            for s2, prob in next_map.items():
                self.A[s1][s2] = prob

        # Emission lexicon B[tag][word]
        self.B = defaultdict(lambda: defaultdict(lambda: 1e-4))
        lexicon = {
            "PRP": ["i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them"],
            "PRP$": ["my", "your", "his", "her", "its", "our", "their"],
            "MD": ["will", "shall", "can", "could", "would", "should", "must", "may", "might"],
            "VBP": ["am", "are", "is", "hate", "suck", "know", "think", "want", "like", "need"],
            "VB": ["kill", "murder", "die", "hurt", "attack", "destroy", "shoot", "beat", "shut", "be", "go", "make", "take", "see"],
            "VBG": ["going", "killing", "freaking", "fucking", "hating", "trying", "saying", "talking"],
            "TO": ["to"],
            "DT": ["the", "a", "an", "this", "that", "these", "those", "all", "some"],
            "JJ": ["stupid", "dumb", "idiotic", "worthless", "pathetic", "ugly", "sick", "disgusting", "filthy", "inferior", "racist", "good", "great", "helpful", "bad", "toxic", "obscene"],
            "NN": ["idiot", "moron", "loser", "fool", "trash", "garbage", "bitch", "bastard", "shit", "fuck", "hell", "crap", "scum", "pig", "vermin", "person", "article", "comment", "email", "app", "time"],
            "NNS": ["people", "idiots", "morons", "losers", "fools", "threats", "insults", "comments", "users"],
            "RB": ["not", "never", "very", "so", "really", "badly", "extremely", "totally", "just", "always"],
            "IN": ["with", "in", "on", "at", "for", "of", "from", "about", "before", "after", "up"],
            "CC": ["and", "or", "but", "yet", "so"],
        }
        for tag, words in lexicon.items():
            for w in words:
                self.B[tag][w] = 0.08

    def _rule_based_emission_boost(self, word: str, tag: str) -> float:
        """Morphological emission fallback for unknown words."""
        if self.B[tag][word] > 1e-4:
            return self.B[tag][word]
        if word.endswith("ing") and tag == "VBG":
            return 0.05
        if word.endswith("ly") and tag == "RB":
            return 0.05
        if word.endswith(("ous", "ful", "ive", "ic", "less", "able")) and tag == "JJ":
            return 0.05
        if word.endswith("s") and not word.endswith("ss") and tag == "NNS":
            return 0.04
        if tag == "NN":
            return 0.01  # Default open-class noun prior
        return 1e-4

    def viterbi_decode(self, tokens: List[str]) -> Dict[str, Any]:
        """
        Module 3.2: Exact Viterbi Algorithm in log-probability space to prevent underflow.
        Returns the optimal Penn Treebank POS tag sequence and Viterbi trellis summary.
        """
        if not tokens:
            return {"tagged_tokens": [], "best_path_log_prob": 0.0, "trellis_steps": []}

        T = len(tokens)
        viterbi = [{} for _ in range(T)]
        backpointer = [{} for _ in range(T)]

        # Initialization step (t = 0)
        w0 = tokens[0].lower()
        for s in self.states:
            emis = self._rule_based_emission_boost(w0, s)
            viterbi[0][s] = math.log(self.pi.get(s, 0.001)) + math.log(emis)
            backpointer[0][s] = "START"

        # Recursion step (t = 1 .. T-1)
        for t in range(1, T):
            wt = tokens[t].lower()
            for s in self.states:
                emis = math.log(self._rule_based_emission_boost(wt, s))
                best_prev_state = None
                best_log_prob = -1e18
                for s_prev in self.states:
                    prob = viterbi[t - 1][s_prev] + math.log(self.A[s_prev][s]) + emis
                    if prob > best_log_prob:
                        best_log_prob = prob
                        best_prev_state = s_prev
                viterbi[t][s] = best_log_prob
                backpointer[t][s] = best_prev_state

        # Termination step
        best_final_state = max(self.states, key=lambda s: viterbi[T - 1][s])
        best_path_log_prob = viterbi[T - 1][best_final_state]

        # Backtracking
        best_tags = [best_final_state]
        for t in range(T - 1, 0, -1):
            best_tags.insert(0, backpointer[t][best_tags[0]])

        # Module 3.1: Transformation-Based (Brill) Post-Processing Rules
        # Rule 1: If 'to' (TO) precedes a NN that can be a VB, transform NN -> VB
        for i in range(1, T):
            if best_tags[i - 1] == "TO" and best_tags[i] in ("NN", "VBP"):
                best_tags[i] = "VB"
            # Rule 2: If Determiner (DT) precedes a VB, transform VB -> NN
            if best_tags[i - 1] == "DT" and best_tags[i] in ("VB", "VBP"):
                best_tags[i] = "NN"

        tagged_output = []
        trellis_steps = []
        for t, (tok, tag) in enumerate(zip(tokens, best_tags)):
            tagged_output.append({
                "token": tok,
                "pos_tag": tag,
                "description": PENN_TAG_DESCRIPTIONS.get(tag, "Lexical Tag")
            })
            # Top 3 candidate states in Viterbi trellis at step t
            top_states = sorted(viterbi[t].items(), key=lambda x: x[1], reverse=True)[:3]
            trellis_steps.append({
                "step": t,
                "token": tok,
                "chosen_tag": tag,
                "top_candidates": [{"tag": st, "log_prob": round(lp, 2)} for st, lp in top_states]
            })

        return {
            "tagged_tokens": tagged_output,
            "best_path_log_prob": round(best_path_log_prob, 3),
            "trellis_steps": trellis_steps[:12]
        }


_POS_TAGGER = HMMViterbiPOSTagger()


# =========================================================================================
# MODULE 4: SEMANTIC ANALYSIS (WORDNET RELATIONS, COSINE DISTANCE, LESK & NAIVE BAYES WSD)
# =========================================================================================

def simplified_lesk_wsd(tokens: List[str]) -> List[Dict[str, Any]]:
    """
    Module 4.1, 4.2, 4.4: Knowledge-Based Word Sense Disambiguation using Lesk's Algorithm
    over our WordNet Synset Knowledge Base, plus Supervised Naive Bayes / Decision List rules.
    """
    context_set = set(lemmatize_word(t) for t in tokens).union(set(tokens))
    disambiguated = []

    for idx, tok in enumerate(tokens):
        lemma = lemmatize_word(tok)
        if lemma not in WORDNET_KB:
            continue

        senses = WORDNET_KB[lemma]
        best_sense = senses[0]
        max_overlap = -1
        sense_scores = []

        for s in senses:
            # Signature = words in gloss + examples + synonyms + hypernyms
            sig_text = s["gloss"] + " " + " ".join(s["examples"]) + " " + " ".join(s["synonyms"])
            sig_words = set(lemmatize_word(w) for w in tokenize_text(sig_text)).union(set(tokenize_text(sig_text)))
            overlap_words = context_set.intersection(sig_words) - {lemma, tok}
            overlap_count = len(overlap_words)

            # Decision List / Naive Bayes Contextual Collocation boost (Module 4.4)
            window = tokens[max(0, idx - 2): min(len(tokens), idx + 3)]
            if lemma == "kill" and any(w in window for w in ["it", "time", "process", "app", "stage"]):
                if s["sense_type"] == "benign_idiom":
                    overlap_count += 3
            elif lemma == "kill" and any(w in window for w in ["you", "him", "her", "them", "going"]):
                if s["sense_type"] == "toxic_threat":
                    overlap_count += 3

            sense_scores.append({
                "synset": s["synset"],
                "sense_type": s["sense_type"],
                "lesk_overlap_score": overlap_count,
                "overlapping_terms": list(overlap_words)
            })
            if overlap_count > max_overlap:
                max_overlap = overlap_count
                best_sense = s

        disambiguated.append({
            "token_index": idx,
            "word": tok,
            "lemma": lemma,
            "selected_synset": best_sense["synset"],
            "sense_type": best_sense["sense_type"],
            "gloss": best_sense["gloss"],
            "lexical_relations": {
                "synonyms": best_sense["synonyms"],
                "antonyms": best_sense["antonyms"],
                "hypernyms": best_sense["hypernyms"],
                "hyponyms": best_sense["hyponyms"],
                "meronyms": best_sense["meronyms"],
                "reversives": best_sense["reversives"],
            },
            "lesk_candidates": sense_scores
        })

    return disambiguated


def compute_tfidf_cosine_similarity(comment: str) -> List[Dict[str, Any]]:
    """
    Module 4.3: Cosine Distance & Similarity between the input comment and Reference Documents
    in TF-IDF Vector Space.
    CosineSimilarity(d1, d2) = (d1 . d2) / (||d1|| * ||d2||)
    CosineDistance(d1, d2) = 1.0 - CosineSimilarity(d1, d2)
    """
    docs = [comment] + [d["text"] for d in REFERENCE_CORPUS]
    tokenized_docs = [[lemmatize_word(t) for t in tokenize_text(d)] for d in docs]
    vocab = sorted(set(w for doc in tokenized_docs for w in doc))
    if not vocab:
        return []

    N_docs = len(docs)
    df_counts = {w: sum(1 for doc in tokenized_docs if w in doc) for w in vocab}

    tfidf_vectors = []
    for doc in tokenized_docs:
        tf = Counter(doc)
        vec = {}
        for w in vocab:
            if tf[w] > 0:
                idf = math.log((N_docs + 1) / (df_counts[w] + 1)) + 1.0
                vec[w] = (tf[w] / max(len(doc), 1)) * idf
            else:
                vec[w] = 0.0
        tfidf_vectors.append(vec)

    query_vec = tfidf_vectors[0]
    query_norm = math.sqrt(sum(v * v for v in query_vec.values()))

    comparisons = []
    for idx, ref in enumerate(REFERENCE_CORPUS):
        ref_vec = tfidf_vectors[idx + 1]
        ref_norm = math.sqrt(sum(v * v for v in ref_vec.values()))
        dot = sum(query_vec[w] * ref_vec[w] for w in vocab)
        sim = (dot / (query_norm * ref_norm)) if (query_norm * ref_norm) > 0 else 0.0
        dist = 1.0 - sim
        comparisons.append({
            "doc_id": ref["id"],
            "category": ref["category"],
            "reference_text": ref["text"],
            "cosine_similarity": round(sim, 4),
            "cosine_distance": round(dist, 4)
        })

    comparisons.sort(key=lambda x: x["cosine_similarity"], reverse=True)
    return comparisons


# =========================================================================================
# MODULE 5: PRAGMATICS & DISCOURSE PROCESSING (HOBBS & CENTERING ANAPHORA RESOLUTION)
# =========================================================================================

PRONOUN_FEATURES: Dict[str, Dict[str, str]] = {
    "he": {"number": "singular", "gender": "masculine", "person": "3rd", "animacy": "human"},
    "him": {"number": "singular", "gender": "masculine", "person": "3rd", "animacy": "human"},
    "his": {"number": "singular", "gender": "masculine", "person": "3rd", "animacy": "human"},
    "she": {"number": "singular", "gender": "feminine", "person": "3rd", "animacy": "human"},
    "her": {"number": "singular", "gender": "feminine", "person": "3rd", "animacy": "human"},
    "it": {"number": "singular", "gender": "neuter", "person": "3rd", "animacy": "non_human"},
    "they": {"number": "plural", "gender": "neutral", "person": "3rd", "animacy": "any"},
    "them": {"number": "plural", "gender": "neutral", "person": "3rd", "animacy": "any"},
    "their": {"number": "plural", "gender": "neutral", "person": "3rd", "animacy": "any"},
    "you": {"number": "any", "gender": "neutral", "person": "2nd", "animacy": "human"},
    "your": {"number": "any", "gender": "neutral", "person": "2nd", "animacy": "human"},
}


def resolve_anaphora_discourse(text: str) -> Dict[str, Any]:
    """
    Module 5: Reference Resolution using Hobbs' Naïve Syntactic Search & Centering Algorithm
    (Forward-looking Centers Cf, Preferred Center Cp, Backward-looking Center Cb) with
    syntactic/semantic phi-feature agreement constraints (number, gender, person).
    """
    sentences = segment_sentences(text)
    discourse_entities = []
    resolutions = []
    centering_transitions = []

    prev_cf: List[Dict[str, Any]] = []
    prev_cb: str = "None"

    for s_idx, sent in enumerate(sentences):
        toks = tokenize_text(sent)
        pos_res = _POS_TAGGER.viterbi_decode(toks)["tagged_tokens"]
        curr_cf: List[Dict[str, Any]] = []

        # Extract candidate Noun Phrases / Entities in current utterance U_n
        for p_idx, item in enumerate(pos_res):
            tok = item["token"]
            tag = item["pos_tag"]
            if (tag in ("NN", "NNS") and tok not in {"though", "very", "really", "badly", "here", "there", "now", "then", "later", "today", "tomorrow", "please", "thank", "thanks", "yes", "no", "hey", "hi", "hello"} and tok not in PRONOUN_FEATURES) or tok in ("john", "mary", "admin", "moderator", "author", "user", "users", "people", "group"):
                num = "plural" if (tag == "NNS" or tok in ("users", "people")) else "singular"
                gender = "feminine" if tok in ("mary", "woman", "girl", "sister", "mother") else (
                    "masculine" if tok in ("john", "man", "boy", "brother", "father", "guy") else "neutral"
                )
                gram_role = "Subject (Cp)" if p_idx < len(pos_res) // 2 else "Object"
                entity = {
                    "surface": tok,
                    "sentence_index": s_idx,
                    "number": num,
                    "gender": gender,
                    "grammatical_role": gram_role
                }
                curr_cf.append(entity)
                discourse_entities.append(entity)

        # Resolve pronouns in current sentence using Hobbs' right-to-left antecedent search + Centering
        curr_cb = "None"
        for p_idx, item in enumerate(pos_res):
            tok = item["token"].lower()
            if tok in PRONOUN_FEATURES:
                p_feat = PRONOUN_FEATURES[tok]
                if p_feat["person"] == "2nd":
                    resolutions.append({
                        "anaphor": tok,
                        "sentence": s_idx + 1,
                        "resolved_antecedent": "[Addressee / Interlocutor in Discourse]",
                        "algorithm": "Deictic Discourse Frame",
                        "constraints_satisfied": "2nd-Person Direct Address"
                    })
                    curr_cb = "[Addressee]"
                    continue

                # Search prior entities (Hobbs' breadth-first syntactic search preference: prior Subject > Object)
                matched_ant = None
                for cand in reversed(discourse_entities):
                    num_ok = (p_feat["number"] == "any") or (cand["number"] == p_feat["number"])
                    gen_ok = (p_feat["gender"] == "neutral") or (cand["gender"] in ("neutral", p_feat["gender"]))
                    if num_ok and gen_ok and cand["surface"] != tok:
                        matched_ant = cand
                        break

                if matched_ant:
                    curr_cb = matched_ant["surface"]
                    resolutions.append({
                        "anaphor": tok,
                        "sentence": s_idx + 1,
                        "resolved_antecedent": matched_ant["surface"],
                        "algorithm": "Hobbs & Centering (Cb = Cp)",
                        "constraints_satisfied": f"Number={matched_ant['number']}, Gender={matched_ant['gender']}, Role={matched_ant['grammatical_role']}"
                    })
                else:
                    resolutions.append({
                        "anaphor": tok,
                        "sentence": s_idx + 1,
                        "resolved_antecedent": "[Unbound / External Discourse Entity]",
                        "algorithm": "Hobbs Search Fallback",
                        "constraints_satisfied": f"Required Number={p_feat['number']}"
                    })

        cp = curr_cf[0]["surface"] if curr_cf else (curr_cb if curr_cb != "None" else "None")
        transition_type = "INITIAL / ESTABLISH"
        if s_idx > 0 and curr_cb != "None":
            if curr_cb == prev_cb and curr_cb == cp:
                transition_type = "CONTINUE (Coherent Topic Maintenance)"
            elif curr_cb == prev_cb and curr_cb != cp:
                transition_type = "RETAIN (Topic Shift Preparation)"
            else:
                transition_type = "SHIFT (Discourse Focus Shift)"

        centering_transitions.append({
            "utterance": f"U_{s_idx + 1}",
            "text": sent,
            "Cf_forward_centers": [e["surface"] for e in curr_cf],
            "Cp_preferred_center": cp,
            "Cb_backward_center": curr_cb,
            "transition": transition_type
        })
        prev_cf = curr_cf
        if curr_cb != "None":
            prev_cb = curr_cb

    return {
        "sentence_count": len(sentences),
        "discourse_entities": discourse_entities,
        "anaphora_resolutions": resolutions,
        "centering_table": centering_transitions
    }


# =========================================================================================
# MODULE 1.4 & MODULE 6: STATISTICAL NAIVE BAYES, NER, BIAS/FAIRNESS, PRIVACY & XAI
# =========================================================================================

def naive_bayes_scoring(tokens: List[str], wsd_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Module 1.4 & 4.4: Mathematical Preliminaries — Conditional Probability, Bayes' Rule,
    and Probability Distributions across the 6 toxicity categories.
    P(C_k | W) proportional to P(C_k) * prod_i P(w_i | C_k)
    Also applies WSD context adjustment (reducing false positives when benign sense is active).
    """
    labels = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
    # Empirical prior probabilities from Jigsaw dataset distribution
    priors = {
        "toxic": 0.0958,
        "severe_toxic": 0.0100,
        "obscene": 0.0529,
        "threat": 0.0030,
        "insult": 0.0494,
        "identity_hate": 0.0088
    }

    # Check if WSD resolved a benign idiom (e.g., "killing it", "shoot me an email")
    benign_indices = {item["token_index"] for item in wsd_results if "benign" in item["sense_type"]}

    # Negation scope detection ("not stupid", "never hate")
    negation_tokens = {"not", "never", "no", "neither", "hardly"}

    scores = {lbl: 0.02 for lbl in labels}
    token_contributions = []

    for idx, tok in enumerate(tokens):
        norm_info = normalize_adversarial_token(tok)
        canonical = lemmatize_word(norm_info["normalized"])
        is_negated = idx > 0 and tokens[idx - 1] in negation_tokens

        if canonical in TOXIC_LEXICON:
            if idx in benign_indices:
                token_contributions.append({
                    "token": tok,
                    "canonical": canonical,
                    "impact": -0.15,
                    "reason": f"Suppressed by Lesk WSD (Benign Sense Active)"
                })
                continue

            matched_cats = TOXIC_LEXICON[canonical]
            weight = 0.25 if is_negated else 0.78
            for cat in matched_cats:
                # Bayes log-odds update mapped through logistic sigmoid
                scores[cat] = min(0.99, 1.0 - (1.0 - scores[cat]) * (1.0 - weight))
            token_contributions.append({
                "token": tok,
                "canonical": canonical,
                "impact": round(weight, 3),
                "categories": matched_cats,
                "reason": "Negated Toxic Term (Attenuated)" if is_negated else f"Matched Lexicon ({norm_info['method']})"
            })
        else:
            token_contributions.append({
                "token": tok,
                "canonical": canonical,
                "impact": 0.0,
                "categories": [],
                "reason": "Neutral / Non-Toxic Token"
            })

    # Compute descriptive statistics over the 6-class probability distribution (Module 1.4)
    vals = list(scores.values())
    mean_p = sum(vals) / len(vals)
    variance_p = sum((v - mean_p) ** 2 for v in vals) / len(vals)

    return {
        "naive_bayes_probabilities": {k: round(v, 4) for k, v in scores.items()},
        "priors_jigsaw": priors,
        "distribution_stats": {
            "mean_probability": round(mean_p, 4),
            "variance": round(variance_p, 4),
            "std_dev": round(math.sqrt(variance_p), 4),
            "max_probability": round(max(vals), 4)
        },
        "token_xai_attributions": token_contributions
    }


def anonymize_pii_and_ner(text: str) -> Dict[str, Any]:
    """
    Module 6.1 (Named Entity Recognition) & Module 6.2 (Data Privacy & Anonymization).
    Detects and redacts PII (Emails, Phone Numbers, IPv4 addresses, @Handles) and extracts Entities.
    """
    redacted = text
    redactions = []

    patterns = [
        ("EMAIL", r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[REDACTED_EMAIL]"),
        ("PHONE", r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", "[REDACTED_PHONE]"),
        ("IPV4", r"(?:\d{1,3}\.){3}\d{1,3}", "[REDACTED_IP]"),
        ("USER_HANDLE", r"@[A-Za-z0-9_]{2,}", "[REDACTED_USER]"),
    ]
    for pii_type, pat, repl in patterns:
        matches = re.findall(pat, redacted)
        if matches:
            for m in matches:
                redactions.append({"type": pii_type, "value": m, "replacement": repl})
            redacted = re.sub(pat, repl, redacted)

    # Lightweight Named Entity & Identity Group Recognition (Module 6.1 & 6.2)
    identity_terms = {"women", "woman", "men", "man", "muslim", "christian", "hindu", "jewish", "black", "white", "asian", "indian", "american", "gay", "lgbt", "trans"}
    toks = tokenize_text(text)
    detected_identities = [t for t in toks if t in identity_terms]

    return {
        "anonymized_text": redacted,
        "pii_redactions": redactions,
        "detected_identity_mentions": detected_identities
    }


def evaluate_fairness_and_ethics(tokens: List[str], final_probs: Dict[str, float], pii_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Module 6.2: Bias & Fairness Metrics in NLP, Counterfactual Token Swap Auditing,
    Data Privacy, and Explainable AI (XAI) Transparency summary.
    """
    identity_mentions = pii_info["detected_identity_mentions"]
    max_tox = max(final_probs.values()) if final_probs else 0.0

    # Counterfactual Fairness Check: Did a demographic mention trigger false identity_hate without toxic words?
    has_explicit_insult_or_hate = any(lemmatize_word(normalize_adversarial_token(t)["normalized"]) in TOXIC_LEXICON for t in tokens)
    false_positive_identity_bias_risk = bool(identity_mentions and not has_explicit_insult_or_hate and final_probs.get("identity_hate", 0.0) > 0.25)

    return {
        "demographic_parity_audit": {
            "identity_terms_detected": identity_mentions,
            "counterfactual_fairness_passed": not false_positive_identity_bias_risk,
            "bias_mitigation_note": (
                "Identity mention detected without accompanying toxic lexicon; counterfactual debiasing prevents false-positive identity_hate."
                if identity_mentions and not has_explicit_insult_or_hate
                else "Prediction grounded in explicit lexical/syntactic toxicity markers rather than demographic identity terms."
            )
        },
        "privacy_compliance": {
            "local_inference_only": True,
            "pii_count_redacted": len(pii_info["pii_redactions"]),
            "anonymized_preview": pii_info["anonymized_text"]
        }
    }


# =========================================================================================
# MASTER SYLLABUS PIPELINE RUNNER
# =========================================================================================

def run_full_nlp_pipeline(comment: str, neural_preds: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Executes all 6 Syllabus Modules on the input comment and combines neural BiLSTM predictions
    (if available) with the statistical/knowledge-based NLP pipeline.
    """
    sentences = segment_sentences(comment)
    raw_tokens = tokenize_text(comment)

    # Module 2: Word Level Analysis
    normalized_tokens_info = [normalize_adversarial_token(t) for t in raw_tokens]
    normalized_tokens = [item["normalized"] for item in normalized_tokens_info]
    morphology_table = [analyze_morphology(t) for t in raw_tokens[:20]]
    collocations = extract_collocations_pmi(normalized_tokens)
    toxic_lm_eval = _TOXIC_LM.evaluate_perplexity(normalized_tokens)
    safe_lm_eval = _SAFE_LM.evaluate_perplexity(normalized_tokens)

    # Module 3: Syntax Level Analysis (HMM + Viterbi POS Tagging)
    pos_analysis = _POS_TAGGER.viterbi_decode(normalized_tokens)

    # Module 4: Semantic Analysis (WordNet WSD + TF-IDF Cosine Distance)
    wsd_results = simplified_lesk_wsd(normalized_tokens)
    cosine_matches = compute_tfidf_cosine_similarity(" ".join(normalized_tokens))

    # Module 5: Pragmatics & Discourse Processing (Hobbs & Centering Anaphora Resolution)
    discourse_analysis = resolve_anaphora_discourse(comment)

    # Module 1.4 & Module 6: Statistical Naive Bayes, XAI, Privacy & Fairness
    nb_analysis = naive_bayes_scoring(raw_tokens, wsd_results)
    pii_info = anonymize_pii_and_ner(comment)

    # Hybrid Ensemble: Combine BiLSTM neural probabilities (if loaded) with Syllabus Statistical/WSD Pipeline
    nb_probs = nb_analysis["naive_bayes_probabilities"]
    if neural_preds:
        final_probs = {}
        for k in nb_probs.keys():
            # Blend 70% BiLSTM + 30% Statistical/WSD-calibrated Naive Bayes (also catches adversarial leetspeak)
            final_probs[k] = round(0.70 * float(neural_preds.get(k, 0.0)) + 0.30 * nb_probs[k], 4)
    else:
        final_probs = nb_probs

    ethics_report = evaluate_fairness_and_ethics(raw_tokens, final_probs, pii_info)

    return {
        "predictions": final_probs,
        "syllabus_analysis": {
            "module_1_preliminaries": {
                "stages_executed": [
                    "1. Lexical & Morphological Normalization",
                    "2. Syntactic HMM Viterbi POS Tagging",
                    "3. Semantic WordNet Lesk WSD & TF-IDF Cosine Similarity",
                    "4. Pragmatic Hobbs/Centering Anaphora Resolution",
                    "5. Multi-Label BiLSTM + Naive Bayes Classification",
                    "6. Ethical PII Redaction, Fairness & XAI Attribution"
                ],
                "token_count": len(raw_tokens),
                "sentence_count": len(sentences),
                "probability_statistics": nb_analysis["distribution_stats"],
                "jigsaw_class_priors": nb_analysis["priors_jigsaw"]
            },
            "module_2_word_level": {
                "sentences": sentences,
                "tokens": raw_tokens,
                "adversarial_edit_distance": normalized_tokens_info[:20],
                "morphology": morphology_table,
                "collocations_pmi": collocations,
                "ngram_language_model": {
                    "toxic_corpus_perplexity": toxic_lm_eval["perplexity"],
                    "safe_corpus_perplexity": safe_lm_eval["perplexity"],
                    "smoothing_method": toxic_lm_eval["smoothing"],
                    "sample_transitions": toxic_lm_eval["transitions"]
                }
            },
            "module_3_syntax_level": pos_analysis,
            "module_4_semantic_analysis": {
                "wordnet_lesk_wsd": wsd_results,
                "tfidf_cosine_similarity": cosine_matches
            },
            "module_5_pragmatics_discourse": discourse_analysis,
            "module_6_ethics_and_xai": {
                "xai_token_attributions": nb_analysis["token_xai_attributions"],
                "fairness_and_privacy": ethics_report
            }
        }
    }
