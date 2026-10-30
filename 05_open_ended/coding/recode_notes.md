# Second coder's notes (P5.S06)

Authored record. The blind second coder (a separate agent, coder `claude-recode`) coded the 200 answers in `recode_sample.csv` from `coding_frame.md` v1.1 alone. It opened only the frame, the sample and the validator script (`scripts/p5_expand_codes.py`, to learn the file format). It did not open `codes.csv`, any other codes file, the index, the views, `STATE.md` or git history. Its output validated (`recode_compact.psv` → `recode.csv`, 200 answers, 979 code rows). It judged 105 of 200 not codable.

Below are the places where it found the frame unclear, in its own report, condensed. Provenance: INFERRED (the coder's judgment). They are candidates for the frame. None was applied to the main codes in this step, because changing the frame after measuring and re-scoring without a fresh blind coder would make the check circular.

| # | Where the frame was unclear | What the second coder did | Effect on agreement |
|---|---|---|---|
| 1 | **L26 (judging sales teams):** no rule for when it applies | Put L26 on every codable Q22 and Q23 answer, reading the question as the concept | The largest single source of lexicon disagreement — 29 answers. Without L26, lexicon presence alpha moves from 0.72 to 0.83 (sensitivity row in `consistency_report.md`) |
| 2 | Very short strings: non-answer or unintelligible? | "n", "MOst", runs of dots or commas, "ka" (read as German *k.A.*, "no information") → N-NONANSWER; "e", "w", "ik", "Or", "9999", "D E F", "shaf" → N-UNINTELLIGIBLE | A few codability disagreements; both codes mean not codable, so findings are unaffected |
| 3 | An evaluation with no reason ("none - all ok"; "most a disappointing, but… names are not relevant"; "is not it - are rapidly eliminated") | N-NONANSWER; "lacking everything" coded (RELATIONSHIP, −, salesperson) with no behaviour code | — |
| 4 | A vendor name plus a role, no reason ("IBM, IT specialist") | N-ROLE-ONLY; the frame covers names-only and role-only, not both | — |
| 5 | Valence on factual Q24 reasons ("he is the one who is detailing the products") | 0 (neutral), not the usual + for a best-relationship answer | — |
| 6 | No behaviour code fits: "time" (respect for the customer's time?), "too glib and american", "the easy going one only on the nerves", "Individualism", "good knowledge" (product or business?), "Value" | Left empty, or nearest code (B-HONEST −, B-PROFESSIONAL −, B-PERSONAL +, B-COMPETENT +, B-PRICE +) | Behaviour primary alpha still 0.81 |
| 7 | One answer states a criterion and criticises vendors ("Performs up to their marketed commitment. Most hype and do not perform.") | Behaviour + for the criterion, valence − for the criticism | — |
| 8 | Mostly negative answer with one positive ("low price, poor reliability", the frame's own V-MIXED example) | ± (mixed) | — |
| 9 | Q7 "please specify" answers about the respondent's own meeting policy ("Never - I work at home") | ACCESS, attribution O (own company) | — |

Two of these match frame-gap candidates already raised by the main coders: respecting the decision-maker's time (#6) and the vendor's relevance to the customer. They are weighed together in P5.S07 and listed for Scott at the gate review.
