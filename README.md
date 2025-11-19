# wappalyzer-url-scanner

**A production-grade Python CLI** to batch-scan URLs with **Wappalyzer** and export **JSON Lines**.
It prefers the **official Wappalyzer API** for accuracy and stability, with a safe fallback to the
`python-Wappalyzer` library when no API key is available.

> Why API first? Maintained, stable, and better for JS-heavy sites. It provides structured responses,
> authentication, and proper rate limiting. The Python fallback is provided for convenience but may be
> less accurate on dynamic sites.

![CI](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/ci.yml?branch=main)

## Features
- API-first detection with retry + rate limiting
- Robust error handling (invalid URL, timeouts, API errors, rate limit)
- Clean, modular code (src/ layout, type hints, docstrings, logging)
- CLI with JSONL/TXT output formats
- Unit tests with `pytest` (mocked client) and CI via GitHub Actions

## Quickstart
```bash
git clone https://github.com/OWNER/REPO.git
cd wappalyzer-url-scanner
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env  # set WAPPALYZER_API_KEY if using API
python -m src.wappalyzer_scanner.cli -i data/URL.txt -o data/Result.txt -f jsonl
```

## CLI Usage
```bash
python -m src.wappalyzer_scanner.cli --input data/URL.txt --output data/Result.txt --format jsonl
# or
python -m wappalyzer_scanner --input data/URL.txt --output data/Result.txt --format jsonl
```
**Options:**
- `--input/-i` : input file path (one URL per line)
- `--output/-o`: output file path
- `--format/-f`: `jsonl` | `txt` (default: `jsonl`)
- `--method`   : `api` | `python` | `auto` (default: `auto`)
- `--live`     : API live=true (synchronous shallow scan)
- `--recursive`: API recursive=true (async crawl; not recommended for this CLI)
- `--max-workers`: thread pool size (default: 4)
- `--timeout`  : HTTP timeout in seconds (default: 20)
- `--rate`     : API rate limit (RPS, default: 5)
- `--no-verify-ssl`: disable TLS verification (NOT recommended)
- `--log-level`: INFO/DEBUG/WARN/ERROR
- `--verbose/-v`: shortcut for DEBUG logging

## Output (JSONL)
Each line is a JSON object like:
```json
{"url": "https://example.com", "status": "success", "error": null, "technologies": [{"name": "Nginx", "categories": ["Web Servers"]}]}
```

## Project Structure
```
wappalyzer-url-scanner/
├─ README.md
├─ LICENSE
├─ .gitignore
├─ requirements.txt
├─ requirements-dev.txt
├─ pyproject.toml
├─ .env.example
├─ data/
│  ├─ URL.txt
│  └─ Result.sample.txt
├─ src/
│  └─ wappalyzer_scanner/
│     ├─ __init__.py
│     ├─ cli.py
│     ├─ config.py
│     ├─ reader.py
│     ├─ utils.py
│     ├─ writer.py
│     ├─ wappalyzer_client.py
│     └─ scanner.py
├─ tests/
│  ├─ test_reader.py
│  ├─ test_scanner.py
│  └─ test_writer.py
└─ .github/
   └─ workflows/
      └─ ci.yml
```

## Testing
```bash
pytest -q
# with coverage in pyproject.toml:
pytest -q --cov=src --cov-report=term-missing
```

## CI/CD
GitHub Actions workflow runs on push/PR for `main` and `develop` across Python 3.10/3.11.
It installs deps, lints with `ruff`, and runs `pytest`. The badge at the top shows its status.

## Security
- Keep `WAPPALYZER_API_KEY` in `.env` or repository secrets. Never commit secrets.
- TLS verification is ON by default; use `--no-verify-ssl` only when you know what you’re doing.

## License
MIT — see `LICENSE`.

## Roadmap
- CSV/Parquet outputs
- Async httpx client
- Domain-level caching / deduplication
- Database sinks (SQLite/Postgres)
