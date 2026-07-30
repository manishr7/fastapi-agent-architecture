_SEPARATOR = ":"


def build_key(*parts: str) -> str:
    """Join key segments with the project's namespacing convention.

    Domain-specific key names (e.g. "student", "otp") belong to the owning
    module, not here — this only fixes the separator so every module's keys
    share one predictable shape (mirrors ORM model ownership: each module
    owns its own names, infra only provides the shared mechanism).
    """
    return _SEPARATOR.join(parts)
