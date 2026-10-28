# Mobile research console

The console offers four-step policy replay, seven recorded experiment reports,
scripted security/utility checks, JSON downloads and interview explanations.
All amounts and records are synthetic. It makes no model API calls, needs no
database, and has no paid backend or dependency installation.

Source: `web/`. Export with `python scripts/build_mobile.py`. The exporter calls
the real Python demo/check functions and copies the saved reports without
changing their bytes. The browser displays those outputs; it does not recreate
the authorization engine in JavaScript. Real-model failures stay visible.

The site uses a private Sites preview; sign in with the same ChatGPT account.
Hosting configuration is separate from the GitHub research repository. Changes
pushed to GitHub alone do not automatically republish the Sites preview.

Publication URL will be added after deployment is verified.

## Verification

Checked in Chromium at a 390×844 mobile viewport and a 1280×900 desktop viewport:
replay decisions, back/restart, section buttons, measured outcome counts, all
seven original report downloads, JavaScript errors and horizontal overflow.
This browser check is separate from the Python engine's automated tests and
the saved real-model evaluation.

## Remaining work

This is a recorded demo interface. Live inference, live document ingestion,
clean benchmark competence and held-out evaluations remain unfinished.
