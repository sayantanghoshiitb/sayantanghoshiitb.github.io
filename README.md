# Sayantan Ghosh — standalone photography website

The website is built locally without WordPress. Publications has been removed. The project preserves 87 remaining migrated routes and adds `/wildlife/` (88 routes, plus a 404 document).

## Preview

Run `python scripts/serve.py`, then open http://127.0.0.1:4174/ or http://127.0.0.1:4174/wildlife/ . This is a static preview; it does not sync data in the background.

## Rebuild

Use Python 3.12 and install `requirements.txt` into a virtual environment. Run `python scripts/build.py`. The build replaces `dist/`, so edit source files in `content/`, `src/`, `data/` and `public/` rather than editing generated pages.

`dist/` contains the deployable site. Page titles now replace the generic exterior title on individual destination posts; visible post dates/bylines are removed, while dates remain in structured metadata. All shared footers say © 2026 www.sayantanghosh.com.

On the first page opened in each browser session, a white animated “Welcome to / Sayantan Ghosh Photography” loader waits for all 15 homepage gallery images, or the initially visible eager images on a direct visit to another page. Failed image requests do not block it; lazy images below the fold still load as the visitor scrolls. The wildlife page contains 643 countable species from the official life-list CSV, with verified public API photos for 285 species. A photo-only switch is enabled initially; turning it off shows all names. Photo URLs are assigned only when they approach the viewport. The SVG map supports world → country → state/region zoom, back controls and keyboard activation. Purple shading represents distinct species observed, not checklist/individual-bird counts.

Country and regional totals come from the public JSON API. Individual species' known country/state memberships combine first sightings from the export and public photo locations. These are incomplete until a complete observation-history export is imported. The filter count therefore says "known sightings" for regional results. A region's headline total can exceed the number of matching cards. We never invent complete region histories from a single world first-sighting record.

See [GitHub Pages deployment](docs/GITHUB-PAGES.md) for the monthly workflow and domain setup.
