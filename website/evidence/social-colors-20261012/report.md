# Color social icons - 2026-10-12

Status: LOCAL_ACCEPTED_NOT_PUBLISHED. Owner: 01a123a8-16ae-76f0-85c9-8e017dd95758.

Ten shared SVG marks now use brand colors rather than gray/78% opacity. TikTok/Douyin use original three-layer contours with a light center on dark backgrounds. Instagram uses the existing camera shape on an app-style gradient. X stays white. Color treatments are local adaptations; not every file is an official download. Source and CC0 notices are retained in assets/social-icons/LICENSE.md and upstream/.

Size: 22 to 24 CSS px. The original 44 px link width, hover translation, keyboard focus, mobile names and reduced-motion behavior remain. No runtime icon CDN/image requests or dependency additions.

Build: 84 HTML / 38 projects. All page HTML is byte-identical to baseline except ten inline SVGs and the social CSS hash. Links, roles, case facts and body text unchanged. Motion, gallery, previous local About and case-reading improvements preserved. Static HTTP/privacy/link checks, 42 bilingual pairs, SEO and disabled indexing pass. Six malicious SVG fixtures reject scripts, events, foreignObject, external paint/href and unscoped gradient IDs.

Actual browser: desktop 10 visible marks at 24 px with 44x44 hit areas; keyboard Tab gives 2 px purple focus and a label; Instagram hover retains its gradient and upward movement. Chinese 390 px and English 320 px simulated viewports show two rows of five with labels, 44x52 hit areas, no horizontal page overflow. Reduced motion remains opaque with no transform. Overrides cleared; temporary QA tab closed. No real-phone or external-profile reachability acceptance claimed.

Evidence: desktop.jpg/footer.jpg show the complete viewport including the footer; mobile.jpg shows actual 390x844 rendering. Both clip APIs returned the wrong crop despite viewport/document coordinates, so final proof uses complete viewport images. No browser/system configuration was changed to work around it.

Test harness: initial exec of check.py missed scripts on sys.path; adding the known script directory made the original checks pass without modifying assertions. A Chinese stdin document write failed before execution; apply_patch wrote the documentation. Static script date/version are historical constants, not this receipt's date/release identifier.

No deployment, server, ERP, ICP, domain, HTTPS or automation work. Online record remains 20261012-143006-seo-geo (not rechecked this turn). Source snapshots, external artwork/license, diff, check results and screenshots retained for review/recovery; no cleanup.
