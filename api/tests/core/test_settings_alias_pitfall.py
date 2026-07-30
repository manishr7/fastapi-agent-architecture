"""Deliberate illustration of a pydantic-settings footgun — not a
reenactment of a historical bug. `Settings` fields use `Field(alias=...)`
without `populate_by_name`, so only the alias (the env var name) is
accepted as a constructor kwarg. Passing the Python attribute name instead
is not an error: `extra="ignore"` (`app/core/config.py`) silently drops it,
and the field quietly keeps its default instead of being overridden.

These two tests exist side by side on purpose: the first manufactures the
mistake and shows the assertion "passing" for the wrong reason; the second
makes the same override using the correct alias, so the contrast is
visible in one file instead of asserted in prose.
"""

from app.core.config import Settings


def test_wrong_kwarg_name_is_silently_ignored_not_an_override() -> None:
    # Intent: override debug to True. Mistake: `debug` is the Python
    # attribute name, not the alias (`DEBUG`) that Settings actually binds
    # constructor kwargs to — so this kwarg is silently dropped rather than
    # raising, and `debug` quietly keeps its default value.
    settings = Settings(_env_file=None, debug=True)

    # This "passes" — but only because it's checking the untouched
    # default (False), not because the override above took effect. Swap
    # the assertion to `is True` and it fails, which is the actual point:
    # the silent drop is invisible unless you go looking for it.
    assert settings.debug is False


def test_correct_alias_kwarg_actually_overrides() -> None:
    # Same intent, correct kwarg: DEBUG is the alias Settings binds to,
    # so this genuinely overrides the field.
    settings = Settings(_env_file=None, DEBUG=True)

    assert settings.debug is True
