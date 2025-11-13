---
title: Hierarchical EZID DOIs with Python
date: '2025-11-13'
categories:
  - python
  - data-management
---

In the [previous tutorial](/posts/2025-10-07-ezid-doi-management-with-python.html) we focused on minting a single test DOI with the EZID API. This follow-up shows how to extend the same repository to support a canonical DOI plus two version-specific DOIs that point to one another so DataCite-powered portals can navigate the release history.

## What “hierarchical” means here

The new `create_hierarchical_doi.py` script mints three identifiers under the EZID test shoulder `doi:10.5072/FK2`:

1.  **Canonical DOI (`WORK-ALL`)** – represents the concept of the dataset across all versions and holds the `HasVersion` links.
2.  **Version 1 (`WORK-V1`)** – records version `1.0`, links back to the canonical DOI with `IsVersionOf`, and points forward with `IsPreviousVersionOf`.
3.  **Version 2 (`WORK-V2`)** – records version `2.0`, also links back via `IsVersionOf`, and references v1 via `IsNewVersionOf`.

The metadata pairs mirror the relationships recommended in the [DataCite versioning guide](https://support.datacite.org/docs/versioning). Because we use EZID’s test shoulder, you can run everything end-to-end without impacting production prefixes.

## Running the new scripts

From the `ezid_api` repository:

```bash
# 1) Create the hierarchy (requires EZID credentials in .env)
uv run python create_hierarchical_doi.py

# 2) Inspect the three DOIs and highlight version fields
uv run python check_hierarchical_doi.py
```

Both scripts reuse the `.env` credentials described in the original tutorial, so there is no additional configuration. After the creation step you will see the EZID responses plus the resolver URLs (`https://doi.org/10.5072/FK2/...`) for each identifier.

## What the metadata looks like

The checker writes a full log (`check_hierarchical_doi_output.txt`) that includes all ANVL fields returned by EZID. A shortened snippet of the most interesting version-specific metadata looks like this:

```text
datacite.version: all
datacite.relatedidentifier.1: 10.5072/FK2/WORK-V1
datacite.relatedidentifier.2: 10.5072/FK2/WORK-V2
datacite.relationtype.1: HasVersion
datacite.relationtype.2: HasVersion

datacite.version: 1.0
datacite.relatedidentifier.1: 10.5072/FK2/WORK-ALL
datacite.relatedidentifier.2: 10.5072/FK2/WORK-V2
datacite.relationtype.1: IsVersionOf
datacite.relationtype.2: IsPreviousVersionOf

datacite.version: 2.0
datacite.relatedidentifier.1: 10.5072/FK2/WORK-ALL
datacite.relatedidentifier.2: 10.5072/FK2/WORK-V1
datacite.relationtype.1: IsVersionOf
datacite.relationtype.2: IsNewVersionOf
```

These blocks are copied directly from `check_hierarchical_doi_output.txt` in the repository and demonstrate how each DOI knows about the others. The canonical DOI advertises both version-specific DOIs with `HasVersion`. Version 1 links back to the canonical record and forward to Version 2, while Version 2 links back and acknowledges that it supersedes Version 1. This structure makes it straightforward for downstream portals to surface an “all versions” landing page as well as permalinks to each individual release.

## Where to go next

If you already manage a production shoulder, swap `doi:10.5072/FK2` in both scripts with your own prefix before running. Otherwise, customize the metadata payloads (targets, creators, resource type) to match your datasets and rerun the scripts to mint a new hierarchy whenever a major release ships.
