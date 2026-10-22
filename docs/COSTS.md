# Zero-cost operating policy

The user has a zero-spend constraint. Preserve this across future work.

## Current version

- Python standard library only; no runtime package installation or model download.
- Tests, demo and checks run locally without network requests.
- All data is synthetic and all refunds are simulated.
- No paid APIs, cloud services, hosted runners, databases or automated schedules.
- No GitHub Actions workflows are enabled. Checks run before a milestone push.
- Use GitHub's free repository hosting; do not enable paid extras.

## Future AI experiments

- Prefer a local model on existing hardware. Inspect RAM, GPU and disk before
  choosing a model. Check its license and distinguish free weights from paid hosting.
- A local model has no provider API bill, but still uses existing electricity,
  hardware, download bandwidth and storage. Do not promise it will run on every laptop.
- Free hosted tiers have quotas and may change; they are not required by the
  project. Never add payment details or silently fall back to a paid provider.
- If suitable free compute is unavailable, keep the working scripted foundation
  and report the model benchmark as pending rather than fabricate results.
- Any future change requiring money needs the user's explicit authorization.

## GitHub updates

During active development, run local checks, review the diff, commit a meaningful
milestone, and push to the authorized repository. This does not create a background
service or promise autonomous development while the assistant is inactive.
Keep tokens, local model files, private data and generated traces out of Git.
