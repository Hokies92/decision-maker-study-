#!/usr/bin/env python3
"""p5_build_text_views.py — scripted text views of the open-ended answers (no hand judgment).

Input: 05_open_ended/corpus.csv (non-answers and refusals excluded from every view).
Outputs (05_open_ended/views/):
    sentiment.csv, sentiment_by_question.csv     M13 VADER (Hutto & Gilbert 2014): compound, pos, neu, neg per answer
    word_freq.csv                                M14 word counts by question and frame (stop words removed)
    keyness_<a>_vs_<b>.csv                       M14 log-likelihood G2 (Dunning 1993): best vs worst — Q22/Q23, Q24/Q25, all
    collocations.csv                             M14 bigrams with count ≥ 3 and pointwise mutual information (Church & Hanks 1990)
    word_network.graphml, word_network_edges.csv M14 words co-occurring in an answer (top 80 words, ≥ 3 shared answers)
    topics.csv, answer_topics.csv                M15 NMF on TF-IDF (Lee & Seung 1999), k = 8, deterministic init
    summary.md
Usage: python3 -I scripts/p5_build_text_views.py
"""
import math
import re
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

import pandas as pd

D = Path("05_open_ended")
OUT = D / "views"
K_TOPICS = 8
TOKEN = re.compile(r"[a-z][a-z'&\-]+")


def stop_words():
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    return set(ENGLISH_STOP_WORDS) | {"don't", "doesn't", "they're", "it's", "i'm", "i've", "can't", "won't", "didn't", "isn't",
                                      "the", "and", "they", "them", "their", "are", "very", "just", "really"}


def tokens(t, sw):
    return [w.strip("'-") for w in TOKEN.findall(t.lower()) if w.strip("'-") not in sw and len(w.strip("'-")) > 1]


def g2(a, b, na, nb):
    """Dunning log-likelihood for a word with counts a (corpus A) and b (corpus B)."""
    e1, e2 = na * (a + b) / (na + nb), nb * (a + b) / (na + nb)
    ll = 0.0
    if a:
        ll += a * math.log(a / e1)
    if b:
        ll += b * math.log(b / e2)
    return 2 * ll


def keyness(ca, cb, label_a, label_b, min_count=3):
    na, nb = sum(ca.values()), sum(cb.values())
    rows = []
    for w in sorted(set(ca) | set(cb)):
        a, b = ca.get(w, 0), cb.get(w, 0)
        if a + b < min_count:
            continue
        rows.append({"word": w, f"count_{label_a}": a, f"count_{label_b}": b, "g2": round(g2(a, b, na, nb), 3),
                     "leans": label_a if a / na > b / nb else label_b})
    return pd.DataFrame(rows).sort_values(["g2", "word"], ascending=[False, True], kind="stable")


def main() -> int:
    import networkx as nx
    from sklearn.decomposition import NMF
    from sklearn.feature_extraction.text import TfidfVectorizer
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    OUT.mkdir(parents=True, exist_ok=True)
    c = pd.read_csv(D / "corpus.csv", dtype=str, keep_default_na=False)
    c = c[(c.non_answer == "False") & (c.refusal == "False")].copy()
    sw = stop_words()
    c["tokens"] = c.text.map(lambda t: tokens(t, sw))

    # M13 sentiment
    sia = SentimentIntensityAnalyzer()
    s = c.text.map(sia.polarity_scores)
    sent = pd.DataFrame({"answer_id": c.answer_id, "item": c.item, "frame": c.frame,
                         "compound": [x["compound"] for x in s], "pos": [x["pos"] for x in s],
                         "neu": [x["neu"] for x in s], "neg": [x["neg"] for x in s]})
    sent.to_csv(OUT / "sentiment.csv", index=False, lineterminator="\n", float_format="%.4f")
    by_q = sent.groupby("item").compound.agg(answers="size", mean="mean", median="median",
                                             share_positive=lambda x: (x >= 0.05).mean(),
                                             share_negative=lambda x: (x <= -0.05).mean()).round(4)
    by_q.reset_index().to_csv(OUT / "sentiment_by_question.csv", index=False, lineterminator="\n")

    # M14 frequency
    freq = []
    for (item, frame), g in c.groupby(["item", "frame"], sort=True):
        for w, n in Counter(w for t in g.tokens for w in t).most_common(40):
            freq.append({"item": item, "frame": frame, "word": w, "count": n})
    pd.DataFrame(freq).to_csv(OUT / "word_freq.csv", index=False, lineterminator="\n")

    # M14 keyness
    cnt = {i: Counter(w for t in c[c.item == i].tokens for w in t) for i in ["Q22", "Q23", "Q24", "Q25"]}
    kq = {"Q22_vs_Q23": keyness(cnt["Q22"], cnt["Q23"], "Q22", "Q23"),
          "Q24_vs_Q25": keyness(cnt["Q24"], cnt["Q25"], "Q24", "Q25"),
          "best_vs_worst": keyness(cnt["Q22"] + cnt["Q24"], cnt["Q23"] + cnt["Q25"], "best", "worst")}
    for k, df in kq.items():
        df.to_csv(OUT / f"keyness_{k}.csv", index=False, lineterminator="\n")

    # M14 collocations (bigrams within answers, stop words kept out)
    uni = Counter(w for t in c.tokens for w in t)
    bi = Counter((a, b) for t in c.tokens for a, b in zip(t, t[1:]))
    N = sum(uni.values())
    col = [{"bigram": f"{a} {b}", "count": n, "pmi": round(math.log2(n * N / (uni[a] * uni[b])), 3)}
           for (a, b), n in bi.items() if n >= 3]
    pd.DataFrame(col).sort_values(["count", "pmi", "bigram"], ascending=[False, False, True], kind="stable") \
        .to_csv(OUT / "collocations.csv", index=False, lineterminator="\n")

    # M14 word co-occurrence network
    top = [w for w, _ in uni.most_common(80)]
    topset = set(top)
    co = Counter()
    for t in c.tokens:
        for a, b in combinations(sorted(set(t) & topset), 2):
            co[(a, b)] += 1
    G = nx.Graph()
    for w in top:
        G.add_node(w, count=uni[w])
    edges = [{"a": a, "b": b, "answers": n} for (a, b), n in sorted(co.items()) if n >= 3]
    for e in edges:
        G.add_edge(e["a"], e["b"], answers=e["answers"])
    nx.write_graphml(G, OUT / "word_network.graphml")
    pd.DataFrame(edges).to_csv(OUT / "word_network_edges.csv", index=False, lineterminator="\n")

    # M15 topics
    docs = c.tokens.map(" ".join)
    keep = docs.str.len() > 0
    vec = TfidfVectorizer(min_df=3, token_pattern=r"[^ ]+")
    X = vec.fit_transform(docs[keep])
    nmf = NMF(n_components=K_TOPICS, init="nndsvd", random_state=0, max_iter=500)
    W = nmf.fit_transform(X)
    terms = vec.get_feature_names_out()
    topics = []
    for k, comp in enumerate(nmf.components_):
        idx = comp.argsort()[::-1][:10]
        topics.append({"topic": k + 1, "top_terms": ", ".join(terms[i] for i in idx),
                       "answers_primary": int((W.argmax(axis=1) == k).sum())})
    pd.DataFrame(topics).to_csv(OUT / "topics.csv", index=False, lineterminator="\n")
    at = pd.DataFrame({"answer_id": c.answer_id[keep].values, "item": c.item[keep].values,
                       "topic": W.argmax(axis=1) + 1, "weight": W.max(axis=1).round(4)})
    at.loc[at.weight == 0, "topic"] = 0
    at.to_csv(OUT / "answer_topics.csv", index=False, lineterminator="\n")

    def top_lean(df, side, n=12):
        x = df[df.leans == side].head(n)
        return ", ".join(f"{w} ({g:.1f})" for w, g in zip(x.word, x.g2))
    bw = kq["best_vs_worst"]
    md = ["# Text views", "", "Generated by `scripts/p5_build_text_views.py`. Substantive answers only "
          f"({len(c)} of 1,697; non-answers and refusals excluded). No hand judgment in these views.", "",
          "## Sentiment (VADER compound, −1 to +1)", "", "| Question | Answers | Mean | Share positive | Share negative |",
          "|---|---|---|---|---|"]
    for i, r in by_q.iterrows():
        md.append(f"| {i} | {int(r.answers)} | {r['mean']:+.2f} | {r.share_positive:.0%} | {r.share_negative:.0%} |")
    md += ["", "## Words that separate best from worst (log-likelihood G2; Q22 + Q24 vs Q23 + Q25)", "",
           "**Best:** " + top_lean(bw, "best"), "", "**Worst:** " + top_lean(bw, "worst"), "",
           "## Topics (NMF, k = 8) — a cross-check for the hand-built themes", "", "| Topic | Top terms | Answers |", "|---|---|---|"]
    for t in topics:
        md.append(f"| {t['topic']} | {t['top_terms']} | {t['answers_primary']} |")
    md += ["", f"Word network: {G.number_of_nodes()} words, {G.number_of_edges()} links (`word_network.graphml`). "
           f"Collocations: {len(col)} bigrams seen ≥ 3 times (`collocations.csv`).", ""]
    (OUT / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print(f"answers={len(c)} topics={K_TOPICS} network={G.number_of_nodes()}/{G.number_of_edges()} bigrams={len(col)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
