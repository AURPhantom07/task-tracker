# AI Collaboration Disclosure

I used AI assistance (GitHub Copilot / ChatGPT) to:
- Draft initial code structure for models, CLI, and storage.
- Suggest ADR formats and examples.
- Generate boilerplate for argparse and JSON handling.

**Prompts used (examples):**
- "Write a dataclass for a Task with title, priority, due, done, and subtasks."
- "How to implement a recursive function to find a task by title?"
- "Give me an ADR template for persistence format."

**What I kept:** The generated code was adapted to fit my design; I kept the core logic but adjusted validation, dunders, and serialization to match my exact requirements.

**What I rejected:** Some AI suggestions used external libraries (e.g., `click`) – I replaced them with `argparse`. Also, the AI initially didn't include `__hash__`; I added it myself.

**Validation:** I tested every command manually, ran unit tests (not shown), and verified that all edge cases (empty file, bad date, missing parent) are handled. I also reviewed the ADL to ensure each decision reflects my own reasoning.