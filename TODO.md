1. Define project goals, scope, and core CLI flows (initial focus: GitHub Trending). ✅
2. Set up baseline package metadata (name, version, entrypoint) and dev tooling.✅
3. Design CLI UX (main menu, source selection, time range, language filter).✅
4. Implement config models and validation (defaults, enums, error messages).✅
5. Build GitHub Trending scraper service (requests + BeautifulSoup) with defensive parsing.✅
6. Add selector logic to rank/limit repos and normalize fields for prompts.❌
7. Create prompt builder for tweet generation (single tweet vs thread, tone, length).✅
8. Integrate OpenRouter client with API key management.✅
9. Implement output writer (stdout + save to file, optional JSON).✅
10. Add logging/verbose mode and friendly CLI errors.✅
11. Write minimal README usage and examples.✅
12. Add tests for fetch/parse, selector, and prompt formatting.✅

Optional improvements:
1. Add more sources (Hacker News, Dev.to, blog RSS).
2. Cache results and avoid re-scraping within a time window.
3. Allow manual overrides (pick specific repos, custom prompt hints).
4. Support scheduled runs (cron) and auto-save drafts.


command saat ini :
itweet github --since daily --lang python