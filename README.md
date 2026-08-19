# Repo moved to [b-fg/CV.typ](https://github.com/b-fg/CV.typ)

This repository is now archived and the ported to typst.

## Curriculum Vitae

[![](https://img.shields.io/badge/CV-download-blue)](https://github.com/b-fg/CV.tex/releases/latest/download/main.pdf) [![CI](https://github.com/b-fg/CV.tex/workflows/CI/badge.svg)](https://github.com/b-fg/CV.tex/actions)

My CV created with $\LaTeX$. Download the [CV](https://github.com/b-fg/CV.tex/releases/latest/download/main.pdf) or run `make` to compile it (output in `build/main.pdf`).

## Workflow

- `main` only tracks sources (`main.tex`, `main.bib`, `res.cls`, `apalike-refs.bst`, the scholar script, and the CI config). Build outputs are git-ignored.
- CI (on push, weekly, or manually) refreshes the Google Scholar metrics, compiles the PDF, and uploads `main.pdf` + `scholar_data.json` as assets of the rolling [`latest` release](https://github.com/b-fg/CV.tex/releases/latest). CI never commits to `main`, so a local clone never falls behind after pushing.
- Stable download link: <https://github.com/b-fg/CV.tex/releases/latest/download/main.pdf>.
- `get_scholar_data.py` fetches the metrics (SerpAPI in CI, scraping locally) and falls back to `.scholar_cache/scholar_data.json`, and then to the JSON published on the release, so fresh clones build offline-ish too.
