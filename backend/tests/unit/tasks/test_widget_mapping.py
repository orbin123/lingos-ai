from app.modules.sessions.widget_mapping import normalize_widget_key


def test_error_spotting_widget_normalizes_to_chat_widget_key() -> None:
    assert normalize_widget_key("ErrorSpotting") == "error_spotting"
    assert normalize_widget_key("error_spotting") == "error_spotting"


def test_error_correction_widget_normalizes_to_chat_widget_key() -> None:
    assert normalize_widget_key("ErrorCorrection") == "error_correction"
    assert normalize_widget_key("error_correction") == "error_correction"
