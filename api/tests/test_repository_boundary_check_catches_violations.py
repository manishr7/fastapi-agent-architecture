"""Proves the check in test_architecture_boundaries.py actually catches a
violation, rather than just asserting it would. Imports the exact same
compiled pattern the real check uses — not a re-implementation that could
silently drift from it — and feeds it deliberately bad source text. No bad
code is ever written into app/modules/*/repositories/ itself; the violation
only ever exists as a string in this test.
"""

from tests.test_architecture_boundaries import FORBIDDEN_CALL

_VIOLATIONS = [
    "await self._session.commit()",
    "await self._session.rollback()",
    "session.commit()",
    "await self.session.rollback()",
]

_NOT_VIOLATIONS = [
    "await self._session.execute(text('SELECT 1'))",
    "await self._session.flush()",
]


def test_forbidden_call_pattern_flags_known_violations() -> None:
    for source in _VIOLATIONS:
        assert FORBIDDEN_CALL.search(source), f"Expected this to be flagged: {source!r}"


def test_forbidden_call_pattern_ignores_unrelated_repository_code() -> None:
    for source in _NOT_VIOLATIONS:
        assert not FORBIDDEN_CALL.search(source), f"False positive on: {source!r}"


def test_forbidden_call_pattern_has_a_known_false_positive_on_comments() -> None:
    # Documented, accepted limitation: this is a substring match on raw
    # source text, not an AST check, so it can't distinguish a real call
    # from a comment mentioning one — as long as the comment contains the
    # same `.commit(`/`.rollback(` shape. Asserted explicitly here rather
    # than left as a claim in prose, so if this ever silently stops being
    # true (e.g. someone upgrades the check to an AST-based one), this test
    # starts failing and the docstring above needs updating too.
    #
    # A bare mention without the leading dot — e.g. "never call commit()
    # directly" — does NOT match; verified while writing this test, and
    # covered by test_forbidden_call_pattern_ignores_unrelated_repository_code
    # style reasoning. The false positive specifically requires the dot.
    commented_out = "# never call session.commit() directly, use the use case"

    assert FORBIDDEN_CALL.search(commented_out)
