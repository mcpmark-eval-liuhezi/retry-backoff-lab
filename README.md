# retry-backoff-lab
Hardening retry behavior of the HTTP client: jittered exponential backoff, metrics, and docs

## References

Issues on public repositories where maintainers discuss retry storms, thundering herds, or introducing exponential backoff:

- `UJameel/northwind-atlas` issue #1 — "Paddle webhook retry storm hammers /billing/webhook": failed webhooks retried every 2s with no backoff; maintainers call for exponential backoff before the migration PR can merge. https://github.com/UJameel/northwind-atlas/issues/1
- `smokeylenz1-commits/stellar-nintendo-crest` issue #28 — "fix(indexer): add full jitter and randomized backoff to Soroban RPC retries": uniform retry patterns create a thundering herd effect that exacerbates node overload; proposes full jitter backoff `random(0, min(CAP, BASE * 2^attempt))` with a 500ms base and 30s cap. https://github.com/smokeylenz1-commits/stellar-nintendo-crest/issues/28
- `GPP-Woo/GPP-publicatiebank` issue #502 — "Add jitter to sentry_exponential_backoff": jitter proposed for tasks scheduled en masse to avoid stampeding-herd effects when many failed tasks all hammer the resource at once after the underlying issue is resolved. https://github.com/GPP-Woo/GPP-publicatiebank/issues/502

Source file in a public repository implementing backoff with jitter:

- `dagdelenemre/nopanic` — `src/nopanic/backoff.py`: implements capped exponential growth with full jitter (`uniform(0, min(cap, base * factor**n))`) as the recommended default for anything that talks to a shared service, explicitly to avoid retry stampedes; also ships `decorrelated_jitter`. https://github.com/dagdelenemre/nopanic/blob/2c81bc4feea384b6cbc6bf5377a4af11ae61c9a5/src/nopanic/backoff.py
