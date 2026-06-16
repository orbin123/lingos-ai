"""Unit tests for the A2Z evaluator — pure function tests, no DB needed."""


from app.modules.challenges.a2z_game.evaluator import (
    extract_valid_words,
    grade,
    normalize_token,
    starts_with_letter,
)


# ── normalize_token ──────────────────────────────────────────────────


class TestNormalizeToken:
    def test_strips_trailing_punctuation(self):
        assert normalize_token("apple,") == "apple"

    def test_strips_leading_punctuation(self):
        assert normalize_token("'hello'") == "hello"

    def test_lowercases(self):
        assert normalize_token("Apple") == "apple"

    def test_strips_multiple_punctuation(self):
        assert normalize_token("...word!!!") == "word"

    def test_empty_after_strip(self):
        assert normalize_token("...") == ""

    def test_empty_string(self):
        assert normalize_token("") == ""

    def test_preserves_hyphens_mid_word(self):
        # Hyphens are in string.punctuation, so they get stripped at edges
        # but internal hyphens stay if there's text around them.
        # "well-known" → strips nothing → "well-known"
        assert normalize_token("well-known") == "well-known"

    def test_parentheses_stripped(self):
        assert normalize_token("(test)") == "test"


# ── starts_with_letter ───────────────────────────────────────────────


class TestStartsWithLetter:
    def test_uppercase_match(self):
        assert starts_with_letter("Apple", "A") is True

    def test_lowercase_match(self):
        assert starts_with_letter("apple", "A") is True

    def test_lowercase_letter_param(self):
        assert starts_with_letter("Apple", "a") is True

    def test_no_match(self):
        assert starts_with_letter("banana", "A") is False

    def test_empty_word(self):
        assert starts_with_letter("", "A") is False


# ── extract_valid_words ──────────────────────────────────────────────


class TestExtractValidWords:
    def test_basic_extraction(self):
        transcript = "apple anchor artist"
        result = extract_valid_words(transcript, "A")
        assert result == ["apple", "anchor", "artist"]

    def test_with_punctuation(self):
        transcript = "apple, anchor; artist"
        result = extract_valid_words(transcript, "A")
        assert result == ["apple", "anchor", "artist"]

    def test_deduplication(self):
        transcript = "banana Banana BANANA"
        result = extract_valid_words(transcript, "B")
        assert result == ["banana"]

    def test_filters_non_matching(self):
        transcript = "the apple orange"
        result = extract_valid_words(transcript, "A")
        assert result == ["apple"]

    def test_empty_transcript(self):
        assert extract_valid_words("", "A") == []

    def test_whitespace_only(self):
        assert extract_valid_words("   ", "A") == []

    def test_none_matching(self):
        transcript = "dog cat elephant"
        result = extract_valid_words(transcript, "Z")
        assert result == []

    def test_multiple_s_words(self):
        transcript = "school super"
        result = extract_valid_words(transcript, "S")
        assert result == ["school", "super"]

    def test_stt_noise_filtered(self):
        """Filler words not starting with target letter are filtered."""
        transcript = "um uh so snake"
        result = extract_valid_words(transcript, "S")
        # "so" starts with S and has length 2 (passes min_length=2)
        # "snake" starts with S
        assert "snake" in result
        assert "so" in result
        assert "um" not in result
        assert "uh" not in result

    def test_min_length_filters_single_char(self):
        """Single-char tokens (like 'a') are filtered by default min_length=2."""
        transcript = "a an apple"
        result = extract_valid_words(transcript, "A")
        # "a" → length 1, filtered
        # "an" → length 2, starts with A, kept
        # "apple" → length 5, starts with A, kept
        assert "a" not in result
        assert "an" in result
        assert "apple" in result

    def test_custom_min_length(self):
        transcript = "so sun super"
        result = extract_valid_words(transcript, "S", min_length=3)
        assert "so" not in result
        assert "sun" in result
        assert "super" in result

    def test_preserves_first_seen_order(self):
        transcript = "cherry cat car cherry cat"
        result = extract_valid_words(transcript, "C")
        assert result == ["cherry", "cat", "car"]

    def test_mixed_case_dedup(self):
        """Words that normalize to the same form are deduped."""
        transcript = "Ball BALL ball"
        result = extract_valid_words(transcript, "B")
        assert result == ["ball"]


# ── grade ────────────────────────────────────────────────────────────


class TestGrade:
    def test_pass_exact_threshold(self):
        transcript = " ".join([f"a{i}word" for i in range(10)])
        # All these tokens start with 'a', length > 2
        result = grade(transcript, "A", target_words=10)
        assert result["passed"] is True
        assert result["valid_word_count"] == 10
        assert result["target_words"] == 10

    def test_fail_below_threshold(self):
        transcript = "apple anchor"
        result = grade(transcript, "A", target_words=10)
        assert result["passed"] is False
        assert result["valid_word_count"] == 2

    def test_pass_above_threshold(self):
        words = ["mountain", "music", "market", "mirror", "metal",
                 "magic", "mango", "maple", "march", "mask", "matter"]
        transcript = " ".join(words)
        result = grade(transcript, "M", target_words=10)
        assert result["passed"] is True
        assert result["valid_word_count"] == 11

    def test_empty_transcript_fails(self):
        result = grade("", "A", target_words=1)
        assert result["passed"] is False
        assert result["valid_word_count"] == 0
        assert result["valid_words"] == []

    def test_result_shape(self):
        result = grade("ball bat", "B", target_words=5)
        assert "valid_words" in result
        assert "valid_word_count" in result
        assert "target_words" in result
        assert "passed" in result
        assert isinstance(result["valid_words"], list)
