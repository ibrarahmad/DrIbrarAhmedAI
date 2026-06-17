# Security Policy

The builds in this repo deal with AI agents, tools, and real hosts — security is
the whole point, so we take it seriously here too.

## Reporting a vulnerability

If you find a security issue in any script or instruction in this repo
(for example, a command that leaks a secret, weakens a host, or runs untrusted
code), **please report it privately first**:

- Use GitHub's **[Private vulnerability reporting](https://github.com/ibrarahmad/DrIbrarAhmedAI/security/advisories/new)**, or
- Reach out via the channel **[@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)**.

Please **do not** open a public issue for a security problem until it has been
addressed.

## What to include

- The file and line(s) involved.
- How it can be exploited or what it exposes.
- A suggested fix, if you have one.

## Scope

This repo ships **companion scripts and docs**, not a hosted service. Findings
about the third-party tools the videos demonstrate (e.g. OpenClaw) should be
reported to those projects directly — but tell us too if our scripts make the
risk worse.

## Good habits these builds follow

- Bind web UIs to **loopback**, reach them over an **SSH tunnel**.
- **Allowlist** tools; let risky actions **ask first**.
- Keep secrets out of git (see [.gitignore](.gitignore)).
- Vet every third-party skill before installing it.

Thank you for keeping the community safe. 🛡
