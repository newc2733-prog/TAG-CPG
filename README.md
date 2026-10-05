# TAG Trauma Handbook

Phone-friendly handbook of the Royal London Hospital Trauma Anaesthesia Group clinical practice guidelines (version 2, 2025).

Open it at https://newc2733-prog.github.io/TAG-CPG/

## What is here

- `index.html`, `sw.js`, `manifest.webmanifest`, `fig/`, `fonts/`, `icons/`: the published app. GitHub Pages serves these from the `main` branch.
- `source/`: the text of each guideline (`source/content/*.md`) and the scripts that rebuild the app.
- `How to publish.txt`: plain-language notes on hosting, sharing and updating.

## Updating

Edit the guideline text in `source/content`, then in the `source` folder run `python3 build.py` and `python3 package.py` (needs Python 3 with `markdown` and `beautifulsoup4`). Copy the contents of `source/app/handbook` over the files at the top of this repository and commit. Phones show a "New version ready" button the next time the app is opened with signal.

This is a prototype transcribed from the PDFs. Check the controlled copy before relying on a dose or number.
