# iTweet: GitHub Trending to Tweet Drafts

iTweet is a CLI tool to fetch trending sources (starting with GitHub Trending) and generate tweet drafts using OpenRouter.

## 📦 Installation

### 1. Requirements
- Python 3.8+

### 2. Install from GitHub (recommended)
```bash
pip install git+https://github.com/BroKarim/itweet.git
```

### 3. Setup (venv) - Alternative method
```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/pip install -e .
```

## 🔑 OpenRouter API Key
On first run with AI features, iTweet will ask for your OpenRouter API key.
- It is saved locally in `~/.itweet_config.json`.
- You can also set `OPENROUTER_API_KEY` in your environment.
- Default model: `google/gemini-2.5-flash`.

## 🛠 Usage


### 1) List GitHub Trending (today)
```bash
itweet github
```

### 2) Filter by period and language
```bash
itweet github --since daily --lang python
```

### 3) Choose tweet output language
```bash
# default is English
itweet github --tweets --tweet-lang Indonesian
```
Notes:
- You can use common names or aliases like `Indonesian`, `Bahasa Indonesia`, `id`, `Malay`, `Melayu`, `ms`.
- If the input is unknown, the raw value will be passed to the model as-is.

### 4) Limit and pick
```bash
# consider top 20, AI picks 4 repos
itweet github --limit 20 --pick 4
```

### 5) Only list (skip AI)
```bash
itweet github --list-only
```

### 6) Generate tweet drafts
```bash
# single tweet per repo (default tone: informative)
itweet github --tweets

# casual tone + shorter max length
itweet github --tweets --tone casual --max-chars 240
```

### 7) Generate thread drafts
```bash
itweet github --tweets --thread
```

### 8) Save output
```bash
# save tweets to text file
itweet github --tweets --output my_tweets.txt

# also save as JSON
itweet github --tweets --json
```

## ⚙️ Options (GitHub)
```text
--since        daily | weekly | monthly   (default: daily)
--lang         filter by language (optional)
--tweet-lang   output language for generated tweets (default: English)
--limit        how many repos to consider (default: 25)
--pick         how many repos AI picks (default: 4)
--readme-chars max README chars to fetch (default: 6000)
--list-only    skip AI selection and README fetch
--tweets       generate tweet drafts
--thread       generate short thread (2-3 tweets) per repo
--tone         tweet tone (default: informative)
--max-chars    max chars per tweet (default: 280)
--output       write tweets to file (txt)
--json         also save tweets to JSON
```

## ✅ Roadmap 
- [ ] Improve prompt quality (more natural).
- [ ] Add non-GitHub sources (Hacker News).
- [ ] Add non-GitHub sources (daily.dev).
- [ ] Simplify CLI command / UX.

## 📄 License
This project is open-source and licensed under the MIT License.
