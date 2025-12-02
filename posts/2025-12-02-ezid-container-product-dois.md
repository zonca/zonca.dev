---
title: Container and Product EZID DOIs with Python
date: '2025-12-02'
categories:
  - python
  - doi
---

This post refers to the [ezid_api repository](https://github.com/zonca/ezid_api).

The previous tutorial showed how to wire a canonical DOI to multiple versions; start there if you need versioning rather than parts: [single DOI basics](/posts/2025-10-07-ezid-doi-management-with-python.html) and [hierarchical versioned DOIs](/posts/2025-11-13-ezid-hierarchical-doi-management.html). This follow-up creates a **container DOI** for a data release and two **product DOIs** that declare they belong to that release. The pattern mirrors a collection landing page (container) that links to specific datasets (products) using DataCite's `HasPart` and `IsPartOf` relations.

## What the container/product pattern does

The new `create_container_doi.py` script mints three identifiers under the EZID test shoulder `doi:10.5072/FK2`:

1.  **Release container (`OCEAN-RELEASE-2025`)** – represents the full 2025 coastal observing system release and lists each product DOI with `HasPart`.
2.  **Product 1 (`OCEAN-RELEASE-2025-P1`)** – a gridded sea surface temperature dataset that points back to the container DOI with `IsPartOf`.
3.  **Product 2 (`OCEAN-RELEASE-2025-P2`)** – a chlorophyll-a mosaic dataset that also uses `IsPartOf` to reference the same container DOI.

Because we stay on the EZID test shoulder, you can try the flow without touching production identifiers.

## Running the scripts

From the `ezid_api` repository root:

```bash
# Mint the release DOI plus two product DOIs
uv run python create_container_doi.py

# Inspect the three identifiers and highlight relation fields
uv run python check_container_doi.py
```

Both scripts reuse the `.env` credentials described in the earlier posts (`EZID_USERNAME` and `EZID_PASSWORD`). The creation step prints each EZID response along with the resolver URLs (`https://doi.org/10.5072/FK2/...`).

## Relationship fields you should see

`check_container_doi.py` prints the ANVL metadata returned by EZID and highlights the relationship fields. A shortened sample looks like:

```text
_target: https://example.org/data-releases/ocean-2025
datacite.relatedidentifier.1: 10.5072/FK2/OCEAN-RELEASE-2025-P1
datacite.relatedidentifiertype.1: DOI
datacite.relationtype.1: HasPart
datacite.relatedidentifier.2: 10.5072/FK2/OCEAN-RELEASE-2025-P2
datacite.relatedidentifiertype.2: DOI
datacite.relationtype.2: HasPart

_target: https://example.org/data-releases/ocean-2025/sea-surface-temp
datacite.relatedidentifier.1: 10.5072/FK2/OCEAN-RELEASE-2025
datacite.relatedidentifiertype.1: DOI
datacite.relationtype.1: IsPartOf
```

The container DOI lists both products with `HasPart`, while each product DOI declares `IsPartOf` to connect back to the release landing page. Swap in your own URLs, creators, and titles before running against a production shoulder.
