# Security Policy

## Reporting a vulnerability

Email **lucian@metricasboss.com.br** with details and, if possible, a minimal
reproduction. Please do not open a public issue for security problems.

We aim to acknowledge within a few days. There is no bug-bounty program.

## Scope

redink is a local CLI. The security-relevant surfaces are:

- **API keys** — `OPENROUTER_API_KEY`, `LANGSMITH_API_KEY`, and optional
  `KAGGLE_KEY` live in `.env`, which is gitignored. Never commit `.env`, and be
  careful pasting keys into shared terminals or recordings.
- **Outbound requests** — redink sends paper text and derived queries to
  third-party services (see [Data & privacy](README.md#data--privacy) in the
  README). Review that section before feeding it confidential material.
- **Fetched content** — papers and figures are fetched from arXiv/ar5iv,
  GitHub, and dataset portals. Content is parsed, never executed.

## Not in scope

Prompt-injection via reviewed papers (a malicious paper steering the model's
findings) is a known limitation of LLM review, not a vulnerability we can fully
close. Treat findings as advisory, not authoritative.
