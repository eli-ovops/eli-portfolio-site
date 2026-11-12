> Inactive local experiment as of 2026-10-17: user restored the original GSAP stacked-card gallery. Current pages do not load this island; the main static build no longer bundles it. Source, dependencies and lockfile remain preserved. The instructions below describe the earlier trial. To rebuild that preserved trial bundle manually, run `npm run build` inside this directory.

# Homepage FlexCarousel island

The site remains statically generated. This isolated React island runs only on the two homepages.

Setup: `npm run setup:carousel` from the website root.
Build: `python3 scripts/build.py` (bundles the island before generating pages).

`components/FlexCarousel.jsx` and `.css` exactly match the official JS-CSS registry.
Do not patch the upstream files for website behavior. `index.jsx` owns case selection,
return restoration, translated controls, image viewer links and fallback behavior.
The requested liquid/rise configuration is preserved. Desktop host height is 560px;
phones use 420px and leave vertical wheel scrolling to the page.

Exact registry and SHA-256 evidence:
`../../evidence/flex-carousel-official-local-20261017/source-verification.json`.
Dependencies are pinned by package-lock.json. No runtime CDN or example stock images.
