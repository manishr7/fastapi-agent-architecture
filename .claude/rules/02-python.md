---
description: Python language standards, coding conventions, naming rules, type hints, and general coding practices for application code under api/app/ (not tests — see 17-testing.md).
globs: api/app/infrastructure/**/*.py, api/app/scripts/**/*.py, api/app/shared/**/*.py, api/app/**/__init__.py
paths:
  - "api/app/infrastructure/**/*.py"
  - "api/app/scripts/**/*.py"
  - "api/app/shared/**/*.py"
  - "api/app/**/__init__.py"
alwaysApply: false
---

# Python Coding Standards

This project targets **Python 3.12**.

Always use Python 3.12 language features where appropriate.

Avoid writing code compatible with older Python versions unless explicitly required.

---

# General Principles

Code MUST prioritize:

- Readability
- Explicitness
- Simplicity
- Correctness
- Maintainability

over

- Cleverness
- Shortness
- Metaprogramming
- Hidden behavior

---

# Type Hints

Every public function MUST have complete type hints.

Example

```python
def create_user(username: str, email: str) -> User:
    ...
```

Never omit return types.

Never use untyped collections.

Good

```python
list[str]
dict[str, int]
set[int]
```

Bad

```python
list
dict
set
```

---

# Optional Types

Use

```python
str | None
```

Never use

```python
Optional[str]
```

unless required for compatibility.

---

# Union Types

Use

```python
int | str
```

instead of

```python
Union[int, str]
```

---

# Generic Types

Always use built-in generic syntax.

Good

```python
list[str]
dict[str, User]
tuple[int, str]
```

Never use

```python
List
Dict
Tuple
```

from typing.

---

# Any

Avoid Any.

Only use Any when no meaningful type exists.

Every use of Any should be intentional.

---

# Casting

Avoid unnecessary casts.

If casting is required, use

```python
typing.cast()
```

Never silence typing errors by abusing casts.

---

# Variable Naming

Variables should clearly describe purpose.

Good

```python
user

current_user

school_id

created_at
```

Bad

```python
x

obj

tmp

value

data1
```

---

# Boolean Naming

Boolean variables should read naturally.

Good

```python
is_active

has_permission

can_delete

should_retry
```

Bad

```python
active

permission

delete

retry
```

---

# Constants

Constants belong at module level.

Use

```python
MAX_PAGE_SIZE = 100

DEFAULT_TIMEOUT = 30
```

Never hardcode repeated values.

---

# Magic Numbers

Avoid unexplained numbers.

Bad

```python
if retries > 7:
```

Good

```python
MAX_RETRIES = 7
```

---

# Functions

Every function should perform one task.

Prefer

20–40 lines.

Avoid

100+ line functions.

Split complex logic.

---

# Parameters

Limit parameters.

Prefer

5 or fewer.

If more are required,

create an object.

---

# Keyword Arguments

Prefer keyword arguments.

Good

```python
create_user(
    username=username,
    email=email,
)
```

---

# Return Statements

Prefer early returns.

Avoid deeply nested conditions.

Good

```python
if not user:
    return None

return user
```

---

# Nesting

Maximum nesting depth

3

Refactor beyond this.

---

# Comprehensions

Use comprehensions only when readable.

Good

```python
names = [user.name for user in users]
```

Avoid nested comprehensions.

---

# Lambda

Avoid lambda.

Prefer named functions.

Use lambda only for trivial expressions.

---

# Exceptions

Catch only expected exceptions.

Never write

```python
except Exception:
```

unless re-raising or translating.

Never silently ignore exceptions.

Never use

```python
pass
```

inside except.

---

# Context Managers

Always use context managers.

Good

```python
with open(...) as file:
```

Never manually close resources.

---

# Mutable Defaults

Never use mutable default arguments.

Bad

```python
def f(items=[]):
```

Good

```python
def f(items: list[str] | None = None):
```

---

# Dataclasses

Prefer dataclasses for simple domain models.

Example

```python
@dataclass(slots=True)
class User:
    ...
```

Enable slots unless mutation requirements prevent it.

---

# Enums

Use Enum for fixed values.

Never use string literals repeatedly.

---

# Strings

Prefer f-strings.

Good

```python
f"User {user.id}"
```

Avoid

```python
"%s" % value

"{}".format(value)
```

---

# Path Handling

Always use pathlib.

Never use os.path.

Good

```python
Path("logs")
```

---

# Imports

Imports belong at the top.

Import order

1 Standard library

2 Third-party

3 Local

One import per line.

Avoid wildcard imports.

Never

```python
from x import *
```

---

# Circular Imports

Avoid circular imports.

If encountered,

reconsider architecture.

---

# Comments

Comments explain WHY.

Code explains WHAT.

Never write obvious comments.

Bad

```python
# increment counter

counter += 1
```

---

# Docstrings

Public classes

Public functions

Public modules

should have concise docstrings.

Private helpers generally do not require them.

---

# Logging

Never use print().

Use the project logging system.

Logging belongs in infrastructure.

---

# Assertions

Assertions are for developer errors.

Never use assertions for validating user input.

---

# Globals

Avoid mutable global state.

Configuration is the only acceptable global state.

---

# Environment Variables

Never read environment variables directly throughout the codebase.

Configuration should be centralized.

---

# Randomness

Never use random where deterministic behavior is required.

Use secrets for security-sensitive randomness.

---

# Time

Always use timezone-aware datetime objects.

Never use naive datetime values.

Always store UTC internally.

---

# UUID

Prefer UUID when globally unique identifiers are required.

Do not generate UUIDs unnecessarily.

---

# Collections

Prefer

dict

set

list

over custom structures.

Choose the simplest collection that satisfies requirements.

---

# Iteration

Prefer direct iteration.

Good

```python
for user in users:
```

Avoid

```python
for i in range(len(users)):
```

unless index is required.

---

# Sorting

Prefer

```python
sorted()
```

over mutating collections unless mutation is intentional.

---

# Copying

Avoid unnecessary deep copies.

Understand shallow vs deep copy semantics.

---

# Equality

Use

```python
is None
```

Never

```python
== None
```

Likewise

```python
is True
```

and

```python
is False
```

should rarely be needed.

---

# File Organization

One public class per file.

One primary responsibility per file.

Avoid files exceeding approximately 300 lines.

---

# Public API

Keep public interfaces small.

Everything else should remain private.

Prefix internal helpers with

```python
_
```

---

# Ruff Compliance

All generated code MUST pass Ruff.

Avoid generating code that requires lint suppression.

Suppress warnings only with clear justification.

---

# Performance

Readable code first.

Optimize only after profiling.

Avoid premature optimization.

---

# Security

Never use eval().

Never use exec().

Never build code dynamically.

Never deserialize untrusted input.

---

# AI Code Generation Rules

Generated code MUST be fully typed.

Generated code MUST use Python 3.12 syntax.

Generated code MUST follow Ruff conventions.

Generated code MUST avoid unnecessary abstraction.

Generated code MUST avoid duplicated logic.

Generated code MUST produce deterministic behavior.

Generated code MUST be production-ready.

---

# Cursor and Claude MUST NEVER

Generate print() debugging.

Generate wildcard imports.

Generate mutable default arguments.

Generate bare except clauses.

Generate unused variables.

Generate unused imports.

Generate commented-out code.

Generate dead code.

Generate placeholder implementations.

Generate TODO comments instead of working implementations.

Generate functions exceeding 100 lines without justification.

Generate cryptic variable names.

Generate deeply nested control flow.

Generate unnecessary inheritance.

Generate global mutable state.

Generate dynamic monkey patching.

Generate code relying on implementation side effects.

---

# Final Principle

Python code should be obvious.

A competent Python developer should understand any file within minutes without requiring external explanation.

Readable code is the highest form of optimization.