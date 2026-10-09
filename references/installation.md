# Install and use Lit Review v2

This folder is the installable Skill package. It needs Python 3.10 or newer for the optional scripts and has no third-party Python dependencies. Literature search, publisher access, and PDF reading depend on the tools available to the assistant at use time; this package does not bundle a search API or full-text downloader.

## Install on Windows

Copy the entire `lit-review-v2` folder into your user Skill directory, so the resulting path is:

```text
%USERPROFILE%\.codex\skills\lit-review-v2\SKILL.md
```

When using the installable ZIP, extract its contents into a folder named `lit-review-v2` before copying or loading it. The archive contains the Skill files at its root for compatibility with direct folder copies.

Open a new Codex chat or refresh the app's Skill list after copying. Invoke with `$lit-review-v2`.

## Script commands

Create a blank project:

```powershell
python .\scripts\init_review_project.py --output "D:\review-project" --topic "your topic" --start-year <start-year> --end-year <end-year> --cutoff-date <YYYY-MM-DD>
```

The topic, year range, cutoff date, document types and screening criteria come from the current review request; the values above are placeholders, not fixed Skill settings. Replace `D:\review-project` with the local directory where the review project should be stored.

Run structural and citation lint after filling the project:

```powershell
python .\scripts\review_lint.py "D:\review-project"
```

The lint script writes `review_lint_report.json` in the project. It checks schemas, row relationships, reference mapping, citations, and selected evidence annotations. It cannot verify whether a paper's factual result, citation metadata, or evidence locator is true; those require source inspection.

The bundled ZIP in `examples/` is an existing audio-review project. It is a sample output, not an additional Skill or a script dependency.
