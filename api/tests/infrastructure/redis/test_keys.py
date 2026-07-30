from app.infrastructure.redis.keys import build_key


def test_build_key_joins_parts_with_colon() -> None:
    assert build_key("student", "otp", "42") == "student:otp:42"


def test_build_key_single_part() -> None:
    assert build_key("student") == "student"


def test_build_key_no_parts_is_empty_string() -> None:
    assert build_key() == ""
