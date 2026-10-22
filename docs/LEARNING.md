# Own and explain the core

Start with `core.py`, then the corresponding tests, then `experiments.py`.

Be able to answer these questions before using this as an interview project:

1. Why is the customer identity supplied by the host instead of the model?
2. Why does a normal prompt such as "follow the refund policy" not enforce a boundary?
3. Why do we use integer paise instead of floating-point rupees?
4. How can split requests or concurrent calls bypass a naive per-request cap?
5. What is idempotency, and why must an existing ID reject a changed payload?
6. Why must document access labels survive content updates?
7. What attacks remain possible when a model obeys every tool permission?
8. Why do these scripted results say nothing about a real model's susceptibility?
9. Why are legitimate completion and attacker success measured separately?
10. Why would a second process or application restart invalidate this in-memory ledger?

Suggested hands-on exercise: implement an order-specific approval requirement
in a branch, write behavior tests first, and evaluate legitimate tasks lost by
the new rule. Explain every line you change and the remaining failure modes.

Track AI assistance honestly according to university and hackathon rules. Do
not claim to have independently written AI-assisted components or invented
existing security techniques. Your understanding, experiments, design choices,
and analysis are the work you must defend.
