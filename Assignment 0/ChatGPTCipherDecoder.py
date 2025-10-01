#!/usr/bin/env python3
"""
Improved Aristocrat (simple substitution) solver with enhanced crib handling.
"""

import random
import math
import collections
import re
from copy import deepcopy

# --------- User: paste your ciphertext here ----------
ciphertext = """WUOCWCIML FZOC IZVVZMXOCL. MFCR MCBB LMUVXCL, ACDZNLC MFCR ZVC IUM GNLM ZAUNM VCZVVZIEXIE CDUIUWXDL ZIY JUBXMXDL. MFCR ZBLU VCZVVZIEC WCZIXIE. ZIY MFCR'VC IUM GNLM ZAUNM VCYXLMVXANMXIE MFC EUUYL. MFCR'VC ZAUNM TXENVXIE UNM PFZM XL EUUY."""

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# ----------------- crib set (hardcoded) -----------------
HARD_CRIBS = ["THE", "AND", "THIS", "THAT", "IS", "YOU", "I'M", "WE'RE", "CAN'T", "DON'T"]

# ----------------- utilities -----------------
def normalize_ciphertext(ct):
    ct = ct.replace("’", "'").replace("`", "'")
    ct = re.sub(r"\s+", " ", ct)
    return ct.strip()

def letters_only(s):
    return ''.join([c for c in s.upper() if c.isalpha()])

# ----------------- key / translation functions -----------------
def random_key():
    letters = list(ALPHABET)
    shuffled = letters[:]
    random.shuffle(shuffled)
    return dict(zip(ALPHABET, shuffled))

def key_to_trans_table(key):
    trans = {}
    for c in ALPHABET:
        trans[ord(c)] = ord(key[c])
        trans[ord(c.lower())] = ord(key[c].lower())
    return trans

def decrypt_with_key(cipher, key):
    table = key_to_trans_table(key)
    return cipher.translate(table)

# Swap two ciphertext->plaintext mappings (mutate)
def mutate_key_random(key):
    new = key.copy()
    a, b = random.sample(ALPHABET, 2)
    new[a], new[b] = new[b], new[a]
    return new

def mutate_key_guided(key):
    if random.random() < 0.6:
        choices = list(ALPHABET)
        a = random.choice(choices)
        b = random.choice(choices)
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
BIGRAM_COUNTS = {
    "TH": 20000, "HE": 18000, "IN": 12000, "ER": 11000, "AN": 10000, "RE": 9000,
    "ND": 8000, "AT": 7500, "ON": 7000, "NT": 6800, "HA": 6500, "ES": 6400,
    "ST": 6300, "EN": 6200, "ED": 6100, "OR": 6000, "TI": 5900, "TE": 5800,
    "NG": 5700, "OF": 5600, "IT": 5500, "IS": 5400, "AL": 5300, "AR": 5200,
    "AS": 5100, "OR": 5000, "SE": 4800, "LE": 4700, "SA": 4600, "VE": 4500,
}
TOTAL_BIGRAMS = sum(BIGRAM_COUNTS.values())
BIGRAM_FLOOR = 0.01

def letters_only(s):
    return ''.join([c for c in s.upper() if c.isalpha()])

def bigram_score(text):
    txt = letters_only(text)
    if len(txt) < 2:
        return -9999.0
    score = 0.0
    for i in range(len(txt)-1):
        bg = txt[i:i+2]
        count = BIGRAM_COUNTS.get(bg, BIGRAM_FLOOR)
        score += math.log(count) - math.log(TOTAL_BIGRAMS)
    return score

# Crib scoring: reward presence of hardcoded cribs
def crib_bonus(text):
    bonus = 0
    for crib in HARD_CRIBS:
        # regex match for whole word
        matches = re.findall(rf'\b{crib}\b', text.upper())
        bonus += 500 * len(matches)  # strong boost per occurrence
    return bonus

def combined_fitness(text):
    return bigram_score(text) + crib_bonus(text)

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

# Run multiple restarts
def run_restarts(cipher, restarts=60, steps=4000, top_n=6):
    results = []
    for r in range(restarts):
        k0 = random_key()
        key, score, plain = simulated_anneal(cipher, initial_key=k0, steps=steps)
        results.append((score, plain, key))

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

# ----------------- main -----------------
def main():
    ct = normalize_ciphertext(ciphertext)
    print("Ciphertext:")
    print(ct)

    print("\nRunning solver with hardcoded cribs...\n")
    results = run_restarts(ct, restarts=60, steps=4000, top_n=8)

    for i, (score, plain, key) in enumerate(results, 1):
        print(f"--- Candidate #{i}  (score={score:.2f}) ---")
        print(plain)
        print()

if __name__ == "__main__":
    main()