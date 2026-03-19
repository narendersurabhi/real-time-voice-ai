from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WordErrorRateResult:
    reference: str
    hypothesis: str
    substitutions: int
    insertions: int
    deletions: int
    word_error_rate: float


def calculate_wer(reference: str, hypothesis: str) -> WordErrorRateResult:
    reference_words = _tokenize(reference)
    hypothesis_words = _tokenize(hypothesis)

    rows = len(reference_words) + 1
    cols = len(hypothesis_words) + 1
    dp = [[(0, 0, 0, 0) for _ in range(cols)] for _ in range(rows)]

    for i in range(1, rows):
        cost, subs, ins, dels = dp[i - 1][0]
        dp[i][0] = (cost + 1, subs, ins, dels + 1)

    for j in range(1, cols):
        cost, subs, ins, dels = dp[0][j - 1]
        dp[0][j] = (cost + 1, subs, ins + 1, dels)

    for i in range(1, rows):
        for j in range(1, cols):
            if reference_words[i - 1] == hypothesis_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
                continue

            sub_cost, sub_s, sub_i, sub_d = dp[i - 1][j - 1]
            del_cost, del_s, del_i, del_d = dp[i - 1][j]
            ins_cost, ins_s, ins_i, ins_d = dp[i][j - 1]

            candidates = [
                (sub_cost + 1, sub_s + 1, sub_i, sub_d),
                (ins_cost + 1, ins_s, ins_i + 1, ins_d),
                (del_cost + 1, del_s, del_i, del_d + 1),
            ]
            dp[i][j] = min(candidates, key=lambda item: item[0])

    total_cost, substitutions, insertions, deletions = dp[-1][-1]
    denominator = max(1, len(reference_words))
    return WordErrorRateResult(
        reference=reference,
        hypothesis=hypothesis,
        substitutions=substitutions,
        insertions=insertions,
        deletions=deletions,
        word_error_rate=round(total_cost / denominator, 4),
    )


def _tokenize(text: str) -> list[str]:
    return [token for token in text.lower().split() if token]
