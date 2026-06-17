# Contributing

Thanks for helping improve the **[@DrIbrarAhmedAI](https://www.youtube.com/@DrIbrarAhmedAI)**
companion repo! 🙌

## Ways to help

- 🐛 **Report a bug** — a script fails, a command changed, a step is unclear.
- 📝 **Improve docs** — fix typos, clarify a step, add a missing prerequisite.
- ✨ **Suggest improvements** — a cleaner or safer way to do something.

## Opening an issue

Include:

- Which **build folder** / video it relates to.
- Your **OS** and relevant tool versions (`node -v`, etc.).
- The **command you ran** and the **full output / error**.

## Pull requests

1. Fork the repo and create a branch: `git checkout -b fix/clear-description`.
2. Keep changes focused — one fix or feature per PR.
3. For shell scripts, keep them POSIX-friendly and run `shellcheck` if you can.
4. **Never commit secrets** — tokens, API keys, `.env` files. They're gitignored
   for a reason.
5. Describe *what* changed and *why* in the PR.

## Style

- Match the style of the surrounding files.
- Scripts should print each command before running it and fail loudly
  (`set -euo pipefail`).
- Prefer safe defaults: loopback binds, allowlists, ask-on-miss.

That's it — thank you! ⭐
