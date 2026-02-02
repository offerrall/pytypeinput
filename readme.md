# pytypeinput 0.1.5

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/pytypeinput.svg)](https://pypi.org/project/pytypeinput/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-727%20passed-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Extract structured metadata from Python type hints.**

</div>

---

pytypeinput analyzes Python type hints and extracts structured metadata. Use this metadata to build UIs, CLIs, config editors, or anything that needs input specifications.
```python
from dataclasses import dataclass
from pytypeinput import Field, Annotated, analyze_dataclass

@dataclass
class User:
    username: Annotated[str, Field(min_length=3, max_length=20)]
    age: Annotated[int, Field(ge=18, le=120)]
    bio: str | None = None

# Extract metadata
params = analyze_dataclass(User)
# Use it to build: HTML forms, CLIs, GUIs, validators...
```

## Design Goals

- **Single source of truth** - Define once with type hints, use everywhere (forms, CLIs, validation)
- **Minimal code** - Maximum features with minimum boilerplate
- **Type-safe** - Full IDE autocomplete and type checking
- **Pure Python** - Build UIs with Python code, not templates or DSLs

## Installation
Core only:
```bash
pip install pytypeinput
```
With HTML renderer:
```bash
pip install pytypeinput[html]
```

**Requirements:** Python 3.10+ • Pydantic 2.0+

## Documentation

**[Complete Documentation](https://offerrall.github.io/pytypeinput)** with interactive examples

**Type System:**
- **[Basic Types](https://offerrall.github.io/pytypeinput/basic-types/)**: `int`, `float`, `str`, `bool`, `date`, `time`
- **[Special Types](https://offerrall.github.io/pytypeinput/special-types/)**: `Email`, `Color`, `File`, `ImageFile`, etc.
- **[Lists](https://offerrall.github.io/pytypeinput/lists/)**: `list[Type]` with item and list-level validation
- **[Optionals](https://offerrall.github.io/pytypeinput/optionals/)**: `Type | None` with toggle switches
- **[Choices](https://offerrall.github.io/pytypeinput/choices/)**: `Literal`, `Enum`, `Dropdown(func)`
- **[Constraints](https://offerrall.github.io/pytypeinput/constraints/)**: `Field(min=, max=, pattern=)` for validation
- **[Type Composition](https://offerrall.github.io/pytypeinput/composition/)**: Build complex types from simple ones
- **[UI Metadata](https://offerrall.github.io/pytypeinput/ui-metadata/)**: Custom labels, descriptions, placeholders, sliders, etc.

**Renderers:**
- **[HTML Renderer](https://offerrall.github.io/pytypeinput/html-renderer/)** - Generate forms with client-side validation

**Reference:**
- **[API Reference](https://offerrall.github.io/pytypeinput/api/)** - Complete API documentation

## What pytypeinput does

✅ Extracts metadata from type hints  
✅ Works with functions, dataclasses, Pydantic models, classes  
✅ Optional HTML renderer with client-side validation  
✅ Framework-agnostic  

❌ No server-side validation  
❌ No form submission handling

**pytypeinput is a building block, not a complete solution.**

> **Validation:** Type hints validated when extracting metadata. HTML forms validate client-side. Server-side is your responsibility (use Pydantic with same type hints).

## Contributing

Found a bug or have a suggestion? [Open an issue](https://github.com/offerrall/pytypeinput/issues)

## License

MIT • [Beltrán Offerrall](https://github.com/offerrall)