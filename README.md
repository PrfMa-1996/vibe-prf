# Vibe Coding

This project contains small AI and computer-vision tools for model evaluation and knowledge-base question answering.

## Purpose

The repository is used to experiment with:

- A Streamlit knowledge-base Q&A assistant backed by the DeepSeek chat API.
- A Tkinter desktop tool that compares YOLOv5n, YOLOv8n, and YOLOv10n cup-detection performance.
- A static browser checklist for assessing object-detection model trustworthiness before deployment.

## Features

### Knowledge Q&A Assistant

`app.py` starts a Streamlit chat app. Users can upload `.txt` or `.md` documents, enter a DeepSeek API key, and ask questions against the uploaded text. The app injects the uploaded content as a system prompt so answers stay grounded in the provided knowledge base.

### YOLO Detection Comparison

`detect_compare.py` opens a file picker, runs the same image through these local model weights, and compares their inference behavior:

- `yolov5nu.pt`
- `yolov8n.pt`
- `yolov10n.pt`

The script measures average inference time, counts detected cup objects, records the highest-confidence detection, saves annotated images as `result_*.jpg`, prints a terminal table, and shows a Tkinter report window with image previews and a timing chart.

### Trustworthiness Checklist

`index.html` is a standalone static web page for reviewing an object-detection model across accuracy, robustness, fairness, explainability, and security. It supports checklist completion, star ratings, summary scoring, and exporting a report in a new browser tab.

## Project Structure

```text
.
├── app.py                 # Streamlit knowledge-base chat app
├── detect_compare.py      # YOLO model comparison desktop app
├── index.html             # Static trustworthiness assessment checklist
├── requirements.txt       # Python runtime dependencies
├── package.json           # Node.js lint/format tooling
├── eslint.config.js       # ESLint configuration
├── .prettierrc            # Prettier formatting configuration
├── .gitignore             # Git ignore rules
├── .vscode/               # VSCode settings & extension recommendations
├── two_cups.jpg           # Sample image for detection
└── README.md              # This file
```

> **Note**: YOLO model weights (`*.pt`) and generated result images are not committed to Git. Download the required weights (`yolov5nu.pt`, `yolov8n.pt`, `yolov10n.pt`) from the [Ultralytics GitHub releases](https://github.com/ultralytics/assets/releases) and place them in the project root before running `detect_compare.py`.

## Install Dependencies

### Python

Create and activate a Python environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The workspace currently points VSCode at `D:\ml\envs\yolo-env\python.exe`, so you can also use that existing environment if it already contains the packages in `requirements.txt`.

### Node.js Tooling

Install JavaScript development dependencies:

```powershell
npm install
```

## Usage

### Run the Streamlit Q&A App

```powershell
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal. Upload a `.txt` or `.md` knowledge file, enter a DeepSeek API key, and ask questions in the chat input.

### Run the YOLO Comparison Tool

```powershell
python detect_compare.py
```

Select an image file in the file picker. The script loads the YOLO weights from the project directory, runs detection, writes annotated `result_*.jpg` files, and opens the visual comparison report.

### Open the Static Checklist

Open `index.html` directly in a browser. No build step or server is required.

### Lint and Format

```powershell
npm run lint
npm run format:check
npm run format
```

`npm test` currently runs the lint task.

## Notes

- `app.py` uses the OpenAI Python SDK with `base_url="https://api.deepseek.com/v1"` and model `deepseek-chat`.
- The Streamlit uploader only reads `.txt` and `.md` content. The UI allows `.pdf`, but PDF text extraction is not implemented.
- Some existing Chinese UI strings in source files appear to have encoding corruption. Preserve file behavior when editing, and normalize text only as an intentional cleanup.
