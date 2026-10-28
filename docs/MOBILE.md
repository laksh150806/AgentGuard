# Mobile research console

The console offers four-step policy replay, seven recorded experiment reports,
scripted security/utility checks, JSON downloads and interview explanations.
All amounts and records are synthetic. It makes no model API calls, needs no
database, and has no paid backend or dependency installation.

Source: `web/`. Export with `python scripts/build_mobile.py`. The exporter calls
the real Python demo/check functions and copies the saved reports without
changing their bytes. The browser displays those outputs; it does not recreate
the authorization engine in JavaScript. Real-model failures stay visible.

## Public Render deployment

[Open AgentGuard](https://agentguard-laksh.onrender.com) — no sign-in required.

- Hosting: Render Static Site, `agentguard-laksh`.
- Repository: `laksh150806/AgentGuard`, branch `main`.
- Automatic deployment: enabled for commits to `main`.
- Build: `python3 scripts/build_mobile.py --output artifacts/render-static`.
- Publish directory: `artifacts/render-static`.
- Environment: `SKIP_INSTALL_DEPS=true`, `PYTHON_VERSION=3.12.8`.
- No backend, model API, database or paid compute instance is provisioned.
- Render's free included bandwidth and build-minute allowances apply; usage
  beyond workspace allowances can incur charges under Render's billing policy.

The earlier private ChatGPT Sites snapshot remains separate and does not
receive GitHub auto-deploys.

## Verification

Checked in Chromium at a 390×844 mobile viewport and a 1280×900 desktop viewport:
replay decisions, back/restart, section buttons, measured outcome counts, all
seven original report downloads, JavaScript errors and horizontal overflow.
This browser check is separate from the Python engine's automated tests and
the saved real-model evaluation.

## Remaining work

This is a recorded demo interface. Live inference, live document ingestion,
clean benchmark competence and held-out evaluations remain unfinished.
