# Kaggle handoff — organizer template fallback (not yet submitted)

**Competition:** https://www.kaggle.com/competitions/physical-engineerings-last-exam/writeups

**Suggested title:** PLE Official Starter Baseline — Pi on Claude Opus 5.5

**Subtitle:** Reproducibility review of the unchanged, organizer-provided PLE engineering-agent baseline

**Public project link (repo):** https://github.com/samertall/ple-aegis-harness

**Source / exact entry:** https://github.com/samertall/ple-aegis-harness/tree/official-template-baseline

**Exact 40-character commit SHA:** `22c26a93a9e4974b16e4351faab0e860ff9fb24f`

**Copy-ready writeup:** https://github.com/samertall/ple-aegis-harness/blob/main/docs/KAGGLE_OFFICIAL_BASELINE_WRITEUP.md

**Independent validation evidence:** https://github.com/samertall/ple-aegis-harness/actions/runs/44251894365

**Original source:** https://github.com/physical-engineerings-last-exam/submission-template

## Status accurately verified

- The original template's 29 dev-task artifacts are preserved at the exact original commit SHA.
- Current PLE `kit validate`: passed.
- Current PLE `kit artifacts`: passed, with 28 usable folders and 1 empty; older dev-set manifest version warning.
- Current PLE `kit build`: passed after using full source history.
- Full live `kit check`: NOT run using an authorized Claude inference endpoint.
- Original historical manifest mean reward ~0.4912; not current regrade and not an Aegis measured result.
- Kaggle Writeup: NOT CREATED, SAVED, or SUBMITTED by this tooling; account status not verified.

## Final submission action in an authenticated Kaggle session

1. Open the competition's Writeups tab and click **New Writeup**, or open your existing draft if one is available.
2. Enter the title/subtitle above. Select an eligible competition track as displayed by Kaggle.
3. Paste the full body from `docs/KAGGLE_OFFICIAL_BASELINE_WRITEUP.md`. If you already drafted an Aegis writeup, do NOT silently substitute this baseline's Claude results for Aegis's Gemini harness; use a separate accurate entry or revise the old draft explicitly.
4. Add the public repository link as the Project Link and explicitly show the exact entry commit SHA.
5. Save, inspect the preview, and click **Submit**. Confirm the interface says **Submitted**, not Draft.

Submitting a stock organizer baseline may be permissible (per the official template README), but its lack of novelty may make it uncompetitive. It is not evidence the participant built Pi or independently measured a 29-task score.

**Do not claim success until the Kaggle account reports Submitted or an official confirmation/receipt exists.**
