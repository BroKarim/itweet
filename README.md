# iTweet: GitHub Trending to Tweet Drafts

iTweet is a CLI tool to fetch trending sources (starting with GitHub Trending) and generate tweet drafts using OpenRouter.

## 📦 Installation

### 1. Requirements
- Python 3.8+

### 2. Setup (venv)
```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### 3. Install (editable dev)
```bash
./venv/bin/pip install -e .
```

## 🛠 Usage

Default (GitHub Trending today):
```bash
itweet github
```

Custom options:
```bash
itweet github --since daily --lang python
```

## 🤖 AI Drafts
AI draft generation will use OpenRouter. We will store the API key locally (similar to iWish) once implemented.

## 📄 License
This project is open-source and licensed under the MIT License.
