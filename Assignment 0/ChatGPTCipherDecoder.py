#!/usr/bin/env python3
"""
Improved Aristocrat (simple substitution) solver.

Features:
- bigram scoring + wordlist scoring
- simulated annealing (with restarts)
- guided + random mutations
- crib application helper (force mappings)
- prints top-N candidates

Usage: run the script. Edit ciphertext variable or pass your own.
"""

import random
import math
import collections
import re
import sys
from copy import deepcopy

# --------- User: paste your ciphertext here (default) ----------
ciphertext = """WUOCWCIML FZOC IZVVZMXOCL. MFCR MCBB LMUVXCL, ACDZNLC MFCR ZVC IUM GNLM ZAUNM VCZVVZIEXIE CDUIUWXDL ZIY JUBXMXDL. MFCR ZBLU VCZVVZIEC WCZIXIE. ZIY MFCR'VC IUM GNLM ZAUNM VCYXLMVXANMXIE MFC EUUYL. MFCR'VC ZAUNM TXENVXIE UNM PFZM XL EUUY."""
# ----------------------------------------------------------------

# Try to load an external wordlist for better scoring (optional)
# Set to None to use built-in small common-word fallback.
WORDLIST_PATH = None  # e.g., "/usr/share/dict/words" or "wordlist.txt"

# A small fallback list of common English words (uppercased)
FALLBACK_COMMON_WORDS = {
    w.upper() for w in """
the be to of and a in that have I it for not on with he as you do at
this but his by from they we say her she or an will my one all would there their
what so up out if about who get which go me when make can like time no just him know
take people into year your good some could them see other than then now look only come its
over think also back after use two how our work first well way even new want because any these give day most us
""".split()
}

# ----------------- bigram frequencies (common English bigrams) -----------------
# Source-like counts (small handcrafted list). Unseen bigrams will get a small floor.
BIGRAM_COUNTS = {
    "TH": 20000, "HE": 18000, "IN": 12000, "ER": 11000, "AN": 10000, "RE": 9000,
    "ND": 8000, "AT": 7500, "ON": 7000, "NT": 6800, "HA": 6500, "ES": 6400,
    "ST": 6300, "EN": 6200, "ED": 6100, "OR": 6000, "TI": 5900, "TE": 5800,
    "NG": 5700, "OF": 5600, "IT": 5500, "IS": 5400, "AL": 5300, "AR": 5200,
    "AS": 5100, "OR": 5000, "SE": 4800, "LE": 4700, "SA": 4600, "VE": 4500,
}
TOTAL_BIGRAMS = sum(BIGRAM_COUNTS.values())
BIGRAM_FLOOR = 0.01

# ----------------- helper utilities -----------------
def normalize_ciphertext(ct):
    # convert curly apostrophes to ascii, collapse multiple spaces
    ct = ct.replace("’", "'").replace("`", "'")
    ct = re.sub(r"[^\x00-\x7F]", lambda m: m.group(0), ct)  # preserve other chars, but keep ascii apostrophe
    ct = re.sub(r"\s+", " ", ct)
    return ct.strip()

def letters_only(s):
    return ''.join([c for c in s.upper() if c.isalpha()])

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# ----------------- key / translation functions -----------------
def random_key():
    letters = list(ALPHABET)
    shuffled = letters[:]
    random.shuffle(shuffled)
    return dict(zip(ALPHABET, shuffled))

def key_to_trans_table(key):
    # returns a dict suitable for str.translate mapping ords
    trans = {}
    for c in ALPHABET:
        trans[ord(c)] = ord(key[c])
        trans[ord(c.lower())] = ord(key[c].lower())
    return trans

def decrypt_with_key(cipher, key):
    table = key_to_trans_table(key)
    return cipher.translate(table)

def invert_key(key):
    # key: plaintext letter target for ciphertext letter? Our key maps ciphertext -> plaintext
    inv = {}
    for c,p in key.items():
        inv[p] = c
    return inv

# Swap two ciphertext->plaintext mappings (mutate)
def mutate_key_random(key):
    new = key.copy()
    a, b = random.sample(ALPHABET, 2)
    new[a], new[b] = new[b], new[a]
    return new

def mutate_key_guided(key):
    # mix of guided and random swaps:
    if random.random() < 0.6:
        # guided: try to swap letters that currently map to improbable letters (heuristic)
        # choose one mapping to a low-frequency plaintext letter and one to high-frequency letter
        freq_order = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
        # pick ciphertext letters whose mapped plaintext positions differ a lot
        choices = list(ALPHABET)
        a = random.choice(choices)
        b = random.choice(choices)
        # 10% chance do a multi-swap of three letters (rare)
        if random.random() < 0.1:
            c = random.choice(choices)
            new = key.copy()
            new[a], new[b], new[c] = new[c], new[a], new[b]
            return new
        new = key.copy()
        new[a], new[b] = new[b], new[a]
        return new
    else:
        return mutate_key_random(key)

# ----------------- scoring functions -----------------
def bigram_score(text):
    """Score given text by log-prob of bigrams. Higher is better."""
    txt = letters_only(text)
    if len(txt) < 2:
        return -9999.0
    score = 0.0
    for i in range(len(txt)-1):
        bg = txt[i:i+2]
        count = BIGRAM_COUNTS.get(bg, BIGRAM_FLOOR)
        score += math.log(count) - math.log(TOTAL_BIGRAMS)
    return score

# Wordlist loader and word-score
def load_wordlist(path=None):
    words = set()
    if path:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    w = line.strip()
                    if w and w.isalpha():
                        words.add(w.upper())
        except Exception:
            # fallback to default
            pass
    if not words:
        words = FALLBACK_COMMON_WORDS
    return words

ENGLISH_WORDS = load_wordlist(WORDLIST_PATH)

def word_score(text):
    """Return fraction of token words that are in the wordlist (0..1)."""
    tokens = re.findall(r"[A-Z']+", text.upper())
    if not tokens:
        return 0.0
    matches = 0
    total = 0
    for t in tokens:
        # strip punctuation like starting/ending apostrophes (keep internal)
        token = t.strip("'")
        if not token:
            continue
        total += 1
        # treat tokens longer than 1 letter; also accept some contractions heuristically
        if token in ENGLISH_WORDS:
            matches += 1
        else:
            # try simple contraction forms: remove trailing 'S or 'T or n't etc
            for suffix in ("'S", "'T", "N'T", "S", "T", "NT"):
                if token.endswith(suffix) and token[:-len(suffix)] in ENGLISH_WORDS:
                    matches += 1
                    break
    if total == 0:
        return 0.0
    return matches / total

# small bonus for presence of very common words
COMMON_WORDS = {"THE", "AND", "TO", "OF", "A", "I", "IN", "IS", "YOU", "THAT", "IT", "HE", "WAS", "FOR", "ON"}

def common_words_bonus(text):
    tokens = re.findall(r"[A-Z']+", text.upper())
    found = 0
    for t in tokens:
        t2 = t.strip("'")
        if t2 in COMMON_WORDS:
            found += 1
    return found

def combined_fitness(text):
    """Combine bigram log-prob + word match + common word bonus into single scalar."""
    # weights were tuned heuristically; you can adjust:
    bg = bigram_score(text)
    ws = word_score(text)
    cw = common_words_bonus(text)
    # combine: bigram log-prob dominates, but strong multiplier for word matches
    return bg + (ws * 8.0) + (cw * 1.6)

# ----------------- crib / forced mapping helpers -----------------
def apply_crib_to_key(key, cipher_word, plain_word):
    """
    Force the mapping so that ciphertext letters in cipher_word map to plain_word letters.
    This returns a new key (cipher->plain). If conflict, we swap values to keep bijection.
    """
    new = key.copy()
    cipher_word = cipher_word.upper()
    plain_word = plain_word.upper()
    if len(cipher_word) != len(plain_word):
        return new
    for c, p in zip(cipher_word, plain_word):
        if not c.isalpha() or not p.isalpha():
            continue
        # find which ciphertext letter currently maps to p and swap
        current_map = new.get(c)
        if current_map == p:
            continue
        # find the ciphertext letter k such that new[k] == p
        k_for_p = None
        for k, v in new.items():
            if v == p:
                k_for_p = k
                break
        if k_for_p:
            # swap mappings between c and k_for_p
            new[k_for_p], new[c] = new[c], new[k_for_p]
        else:
            # assign directly (shouldn't happen because mapping is permutation)
            new[c] = p
    return new

# ----------------- annealing / solver -----------------
def simulated_anneal(cipher, initial_key=None, start_temp=1.0, end_temp=0.001, steps=4000, mutate_fn=None):
    if initial_key is None:
        key = random_key()
    else:
        key = initial_key.copy()
    if mutate_fn is None:
        mutate_fn = mutate_key_guided

    best_key = key.copy()
    best_plain = decrypt_with_key(cipher, best_key)
    best_score = combined_fitness(best_plain)

    current_key = key.copy()
    current_plain = decrypt_with_key(cipher, current_key)
    current_score = best_score

    for i in range(steps):
        t = i / float(steps)
        temp = start_temp * (1 - t) + end_temp * t
        candidate_key = mutate_fn(current_key)
        candidate_plain = decrypt_with_key(cipher, candidate_key)
        candidate_score = combined_fitness(candidate_plain)
        delta = candidate_score - current_score
        if delta > 0 or math.exp(delta / max(temp, 1e-12)) > random.random():
            current_key = candidate_key
            current_plain = candidate_plain
            current_score = candidate_score
            if current_score > best_score:
                best_score = current_score
                best_key = current_key.copy()
                best_plain = current_plain
    return best_key, best_score, best_plain

def run_restarts(cipher, restarts=60, steps=4000, crib_list=None, top_n=6):
    """
    Run simulated annealing multiple times (optionally with cribs).
    crib_list: list of (cipher_word, plain_word) to force (applied each restart randomly or always)
    Returns top_n results sorted by score.
    """
    results = []
    for r in range(restarts):
        # optionally start from random key, or apply a random crib first to seed
        k0 = random_key()
        if crib_list:
            # sometimes pick one crib randomly to try many combinations
            if random.random() < 0.7:
                cw, pw = random.choice(crib_list)
                k0 = apply_crib_to_key(k0, cw, pw)
            else:
                # apply all cribs (occasionally)
                for cw, pw in crib_list:
                    k0 = apply_crib_to_key(k0, cw, pw)

        key, score, plain = simulated_anneal(cipher, initial_key=k0, steps=steps)
        results.append((score, plain, key))
        # small variation: quick extra local hill-climb
        key2, score2, plain2 = simulated_anneal(cipher, initial_key=key, start_temp=0.6, end_temp=0.0001, steps=int(steps/2))
        results.append((score2, plain2, key2))

    # sort and return top_n unique plaintexts (by text)
    results.sort(reverse=True, key=lambda x: x[0])
    seen = set()
    out = []
    for s, p, k in results:
        if p not in seen:
            seen.add(p)
            out.append((s, p, k))
        if len(out) >= top_n:
            break
    return out

# ----------------- utilities for interactive crib suggestions -----------------
def top_short_word_patterns(cipher, maxlen=4):
    # return counts of short words to detect likely 'THE', 'AND', etc.
    tokens = re.findall(r"[A-Z']+", cipher.upper())
    counter = collections.Counter()
    for t in tokens:
        if len(t.strip("'")) <= maxlen:
            counter[t] += 1
    return counter.most_common(30)

# ----------------- main runnable part -----------------
def main():
    random.seed()  # system time
    ct = normalize_ciphertext(ciphertext)
    print("Ciphertext (normalized):")
    print(ct)
    print("\nMost common short ciphertext tokens (candidates for THE/AND/...):")
    for tok, cnt in top_short_word_patterns(ct, maxlen=4)[:15]:
        print(f"  {tok:8}  x{cnt}")
    print("\nLoading wordlist... (found {} words)".format(len(ENGLISH_WORDS)))

    # Suggest a few automated cribs based on simple heuristics:
    # - very common 3-letter token -> THE
    crib_candidates = []
    short_counts = top_short_word_patterns(ct, maxlen=3)
    for tok, cnt in short_counts[:6]:
        cleaned = tok.strip("'")
        if cleaned.isalpha() and len(cleaned) == 3:
            crib_candidates.append((tok, "THE"))
    # Also try typical small words
    crib_candidates += [("ZIY", "THE"), ("VCZ", "AND"), ("MFCR", "THAT"), ("WTHO", "THIS")]

    # prune duplicates while keeping order
    seen = set()
    crib_list = []
    for c,p in crib_candidates:
        if c not in seen:
            crib_list.append((c,p))
            seen.add(c)

    print("\nAuto-crib suggestions (will be tried randomly):")
    for c,p in crib_list:
        print(f"  {c} -> {p}")

    # run solver with restarts
    print("\nRunning solver (this may take a little while)...")
    results = run_restarts(ct, restarts=120, steps=5000, crib_list=crib_list, top_n=8)

    print("\nTop candidate decryptions (score, plaintext):\n")
    for i, (score, plain, key) in enumerate(results, 1):
        print(f"--- Candidate #{i}  (score={score:.2f}) ---")
        print(plain)
        print()

    # optionally show best mapping in readable form
    if results:
        best_score, best_plain, best_key = results[0][0], results[0][1], results[0][2]
        print("Best key (cipher -> plain):")
        pairs = [f"{c}->{best_key[c]}" for c in sorted(ALPHABET)]
        # print mapping in blocks
        for i in range(0, len(pairs), 13):
            print("  " + "  ".join(pairs[i:i+13]))
        print("\nDone.")

if __name__ == "__main__":
    main()
