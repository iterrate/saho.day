# saho.day

Website for Saho, an open, federated learning platform built by Iterrate (OPC) Private Limited. Served by GitHub Pages from the `docs/` folder. Built the same way as [iterrate.in](https://github.com/iterrate/iterrate.in).

- Page texts, header, footer and the federation picture live in `src/build.py`. Edit them there, then run `python3 src/build.py` to regenerate `docs/*.html`, `docs/sitemap.xml` and `docs/robots.txt`.
- Type straight quotes in `build.py`; the build turns them into curly ones.
- Styles: `docs/style.css` (light, dark, print and high-contrast), shared with iterrate.in plus a saho.day section at the end.
- Malayalam text: wrap it in `lang="ml"`. The Noto Sans Malayalam font is only downloaded on pages that contain Malayalam.
- `docs/404.html` is shown by GitHub for any missing address. `docs/CNAME` sets the custom domain; `docs/.nojekyll` stops GitHub running Jekyll.
- SVG files must not carry a C2PA content-credentials block (`<metadata><c2pa:manifest>…`); strip it before committing.

## Fonts

Crimson Pro and Noto Sans Malayalam are under the SIL Open Font Licence 1.1.
