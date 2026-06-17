# TOOLS

> What the agent is allowed to use. This is an **allowlist** — if it is not
> listed here (and allowed in config), the agent must ask first.
>
> Mirror this with the real gate:
>   openclaw tools allow <server>.<tool>

## allowed
- `shell.read`     — read-only inspection (ls, cat, status). No writes.
- `zapier.search`  — look up items for the daily brief. Read-only.

## ask-first (gated)
- `zapier.delete_data` — destructive. Always ASK.
- anything not listed above.

## never
- `rm -rf`, `DROP`, mass delete, or anything that exfiltrates secrets.

> Reality check: 33,000+ ClawHub skills exist and ~12% have carried malware.
> Vet every skill before adding it here.
