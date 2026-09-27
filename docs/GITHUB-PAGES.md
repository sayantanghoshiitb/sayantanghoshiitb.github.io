# GitHub Pages deployment and monthly eBird refresh

## Repository layout

Create a public repository and push the **contents of this project directory** as its root. `.github/workflows/pages.yml` must be at the root `.github/workflows/` directory. Do not push the enclosing `outputs/` directory. `private/`, `.env`, virtual environments and `dist/` are excluded by `.gitignore`. The workflow builds `dist/` from the source.

## Enable publishing

In the repository, open Settings → Pages → Build and deployment → Source → GitHub Actions. Use `main` as the default branch (the workflow listens to pushes to main). Commit/push to publish, or use Actions → Build and publish photography site → Run workflow. Manual runs optionally refresh bird data.

In Settings → Pages set the custom domain to `sayantanghosh.com`. The site uses URLs beginning with `/`, so test it at a user-site root (`USERNAME.github.io`) or on the configured custom domain. A temporary project URL (`USERNAME.github.io/REPO/`) does not support these root paths unchanged. Setting the domain does not change DNS; follow GitHub's custom-domain instructions to verify your domain, configure BigRock DNS and enable HTTPS.

The custom-domain setting is managed in GitHub Pages settings. A CNAME file is unnecessary for a custom Actions deployment.

## Monthly update

The workflow schedule is `17 3 1 * *`: the first day of each month at 03:17 UTC, 08:47 India time. GitHub schedules can be delayed. The workflow must be on the default branch; GitHub can disable schedules on inactive public repositories, so check the Actions page if updates stop.

A Windows runner uses the native PowerShell HTTP client already validated locally. It refreshes public country/state totals and photo metadata, verifies contributor identity, retains the last good snapshot on endpoint failures, and commits `data/birds.json`. The job therefore needs permission to write repository contents; branch protection may require adjusting how automated snapshot commits are accepted. The data snapshot is passed to a separate Linux build job, which generates the static website and publishes it through GitHub Pages. No server runs for visitors and no browser polling is present.

This is the same **undocumented public JSON API approach** as Raw Composition. It requires a public profile, not an eBird password or account session. Endpoints may change. It is not official account OAuth, nor does it expose every new non-photographed life-list entry automatically.

For new species without photos or complete state membership, export your updated official Download My Data CSV to `private/checklists.csv`, run `python scripts/import_ebird.py --checklists private/checklists.csv`, then commit the resulting public `data/birds.json`. Do not commit the raw CSV. Public photos reattach during the next refresh. Photo taxa that cannot be reconciled with the imported life list are reported in Actions and are not silently added as verified lifers.

## Old WordPress URLs

GitHub Pages ignores `_redirects` and `_headers`. The build instead copies each referenced primary-domain image to its original `/wp-content/uploads/...` path. Those URLs return actual image files, including for clients without JavaScript; no redirect service is required. `/wp-sitemap.xml` also resolves directly. Existing retained page URLs already have their own `index.html`.

Aliases increase the generated site to about 835 MB, below GitHub Pages' 1 GB site limit. The build uses real copies because Pages artifacts cannot contain hard links or symbolic links. Removing Publications means `/publications/` is intentionally no longer served. GitHub Pages controls caching and the www/custom-domain redirect; it cannot apply custom server redirect/header rules.

## References

- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits

No repository has been created remotely, no GitHub workflow has run remotely, and no DNS or live-site changes have been made during these local edits.
