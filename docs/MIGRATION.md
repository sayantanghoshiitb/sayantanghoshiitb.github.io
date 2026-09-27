# Migration record — 27 September 2026

## Scope and completeness

Source: https://sayantanghosh.com/

Discovery combined 43 public pages, 34 public posts, sitemap category/author/format archives, and six additional pagination routes. All 88 discovered routes were fetched and their rendered content inspected by the migration parser. The build adds `/wildlife/`. Draft/private pages and administrative/database features are outside the public crawl and have not been exported.

`content/pages.json` is the complete route inventory. `build-report.json` records indexing decisions. All existing routes remain accessible locally; unused template/demo/empty pages and archive duplicates are marked `noindex,follow` to avoid promoting thin duplicate content. Review this policy before publishing, particularly if an old page has existing search value.

## Assets

All 502 referenced assets on the primary domain are local. Five resized Bangkok image URLs returned 404 on the live site. The matching originals found through the media API were used instead:

- IMG_3269
- IMG_3264
- IMG_3265
- IMG_3266
- IMG_3271

221 additional image resources from `sayantantravels.files.wordpress.com` were localized. The resulting set contains 717 raster images; the other primary assets include publication archives/video. Original files remain available for lightbox/download use; responsive WebP variants serve page views. Repeated source sizes can be separate image files, so 717 is an asset count, not a claim of 717 unique photographs.

One external **theme-demo** image (`modernthemes.net/.../tonya.png`) was unavailable. Its demo-page location has a visible unavailable-image note. No replacement stock image was invented.

## Visual and functional limitations

- Page content and URLs are preserved, with shared geometry recreated from inspected dimensions. A complete automated pixel-difference certification across all routes has not been performed.
- Gallery placement uses a small custom masonry layout. Five-pixel gaps and the source breakpoints are retained; widths avoid the original layout's overflow. This can shift photos by several pixels compared with the original.
- Mobile navigation preserves the menu hierarchy but uses accessible expand/collapse controls instead of the theme's sliding drawer animation.
- The lightbox uses a native dialog with previous/next and Escape support. Its controls are intentionally simple and are not a visual copy of Magnific Popup.
- Small-screen heading sizes are reduced to prevent overflow.
- Existing comment text is retained when present. WordPress login links and comment submission UI are removed. There is no comment backend, WordPress login, account system, or checkout implementation.
- Old demo/commerce shortcode text is preserved where it was already rendered as text. These routes should be reviewed for removal/redirect in a later editorial cleanup.
- YouTube embeds remain YouTube embeds; self-hosted video uses native browser controls.
- Layout was visually checked on representative page types, not individually screenshot-compared on all 88 routes.

## eBird evidence and remaining work

The implementation referenced Raw Composition's public source:

- https://github.com/rawcomposition/rawcomposition.com/blob/main/scripts/ebird-pull.ts
- https://github.com/rawcomposition/rawcomposition.com/blob/main/src/helpers/ebird.ts

That project imports photos through an undocumented media-search endpoint and reads country counts through a public profile endpoint. It does not demonstrate an official authenticated real-time personal-checklist stream. Its photographed-species list alone cannot represent birds seen without photographs.

The signed-in official world life-list CSV supplied 643 countable species and 15 excluded rows. Public photo API refresh now attaches verified photos to 285 imported species. Five unmatched photo taxa remain for taxonomy review; the site's photographed-species count is the verified attached count and is not claimed to equal the profile's 295 species-with-photos figure.

Public country and subnational totals are connected for India, Indonesia, South Africa and Spain. Known species-level regional memberships come from first-sighting export records and photo metadata. Complete country/state membership still requires the full observations export. The map uses Natural Earth boundaries; Indonesia's visited island regions and Spain's autonomous communities are grouped to match eBird regions.

The Publications landing page, navigation entry and its four exclusive ZIP downloads were removed at the user's request. Individual destination articles remain, with their titles moved to the exterior header and visible date/admin bylines removed. All footers now say 2026. The static preview no longer has a sync API or refresh loop. A monthly GitHub Actions build/deployment workflow is prepared; see GITHUB-PAGES.md for setup and its limitations. Old primary-domain upload URLs are served by image aliases rather than relying on server redirects.

Official references:

- [Download eBird data](https://support.ebird.org/en/support/solutions/articles/48000838205-download-ebird-data)
- [Media export guidance](https://support.ebird.org/en/support/solutions/articles/48000960529)
- [eBird API documentation](https://documenter.getpostman.com/view/664302/S1ENwy59)

## Validation and performance

- 90 generated HTML documents checked for missing local assets/links, canonical/description presence, and WordPress runtime references; zero failures.
- Seven importer tests passed: world deduplication/country overlap; retaining non-photographed birds; ambiguous-taxonomy exclusion; wrong-owner rejection; audio rejection and correct photo acceptance; checklist association; malformed-input rejection.
- Browser verified: portfolio mosaic, photo next/close, publications layout, nested mobile destination selection, mobile article without horizontal overflow, country-map selection.
- 717 images optimized without decoder errors.
- Original raster asset total: 271,920,434 bytes. Comparable 960px-or-smaller WebP selection: 71,178,482 bytes (about 74% smaller across that asset set). This is an asset-size comparison, not a measured page-load speed improvement; originals remain in the downloadable package.
- No Lighthouse score, production Core Web Vitals, full accessibility audit, or search-ranking uplift has been claimed.

Country boundaries are from [Natural Earth](https://www.naturalearthdata.com/about/terms-of-use/), public domain, except India, which uses the [geoBoundaries India ADM0 simplified outline](https://www.geoboundaries.org/api/current/gbOpen/IND/ADM0/) (CC0). Jammu and Kashmir and Ladakh region outlines use the geoBoundaries India ADM1 simplified boundaries, available under [CC BY 2.5 IN](https://creativecommons.org/licenses/by/2.5/in/); source metadata identifies DataMeet India community and the Election Commission of India. Ladakh remains its own map region. The social icon font is the site's existing Font Awesome brand font. Photography and writing remain Sayantan Ghosh's content.
