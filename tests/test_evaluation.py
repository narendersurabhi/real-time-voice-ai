from app.evaluation import calculate_wer


def test_calculate_wer_tracks_edit_counts() -> None:
    result = calculate_wer("hello there world", "hello world")

    assert result.deletions == 1
    assert result.insertions == 0
    assert result.substitutions == 0
    assert result.word_error_rate == round(1 / 3, 4)
