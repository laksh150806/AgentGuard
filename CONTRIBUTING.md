# Development

Python 3.11+ is required. No third-party runtime dependencies are needed.

```bash
python scripts/check.py
python scripts/run.py demo
python scripts/run.py check
git diff --check
```

Before committing, review `git status` and the diff. Stage only intended source,
test and documentation files. Never commit `.env` files, credentials, downloaded
models, real customer data, or generated reports with sensitive contents.

Keep a meaningful commit history and push tested milestones to the configured
origin during active work. Do not force-push or overwrite unrelated remote work.
Local checks are intentional: this project has a zero-spend constraint and does
not enable hosted CI or paid deployment by default.

Preserve experiment honesty. A mock, scripted proposal, failed run, missing
benchmark or unimplemented baseline must remain visibly labeled.
