# AGENTS.md

## Project Technical Stack

- Python app code: Streamlit, OpenAI Python SDK, Tkinter, OpenCV, NumPy, Pillow, Matplotlib, Ultralytics YOLO.
- Frontend/static UI: plain HTML, CSS, and vanilla JavaScript in `index.html`.
- JavaScript tooling: Node.js, npm, ESLint, Prettier.
- Local model assets: YOLO `.pt` weights stored in the project root.
- Development environment: Windows PowerShell; VSCode is configured to use `D:\ml\envs\yolo-env\python.exe`.

## Code Style

- Keep Python code explicit and small-function oriented, following the style already used in `app.py` and `detect_compare.py`.
- Use clear constants for model names, paths, API endpoints, class IDs, colors, and repeated UI text.
- Prefer `pathlib.Path` for filesystem paths in Python.
- Keep generated files such as detection outputs out of source control.
- For JavaScript and HTML, follow the existing Prettier configuration:
  - single quotes
  - 2-space indentation
  - no semicolons
- Run `npm run lint` and `npm run format:check` after changing JavaScript, HTML, or config files.

## AI Coding Rules

- Read the relevant source and config files before editing.
- Keep changes scoped to the user's request. Do not rewrite unrelated UI, model logic, dependencies, or generated assets.
- Preserve existing public behavior unless the user explicitly asks for a behavior change.
- Do not remove local model weights, sample images, result images, or user-created files unless explicitly requested.
- Be careful with encoding. Some source text currently appears corrupted; do not spread corrupted strings into new documentation or code. If fixing text encoding, do it as a separate, intentional change.
- Use structured APIs for file paths, image loading, model inference, and LLM calls instead of brittle string manipulation.
- For DeepSeek/OpenAI-compatible calls, keep API keys out of source files and logs.
- For YOLO changes, verify that the expected `.pt` weight files exist and that class filtering still matches the intended target class.
- For UI changes, check that controls remain usable on both desktop and narrow screens.
- Document new runtime dependencies in `requirements.txt` or `package.json`.

## Prohibited Actions

- Do not commit secrets, API keys, `.env` files, logs, generated result images, or model export artifacts.
- Do not download or replace YOLO weights without user approval.
- Do not introduce network calls during app startup except where the user explicitly triggers LLM or model functionality.
- Do not silently change the DeepSeek endpoint, model name, or prompt-grounding behavior.
- Do not add heavyweight frameworks to `index.html`; it is intended to remain a standalone static page.
- Do not run destructive Git commands such as `git reset --hard` or file deletion commands unless the user explicitly asks for them.
- Do not modify files outside the current project directory for this repository task.
- Do not delete any comments unless the user explicitly requests it.
- Do not make changes beyond the specific scope described in the user's request, even if other improvements are possible.
- When in doubt about the scope of a change, ask the user before proceeding.
