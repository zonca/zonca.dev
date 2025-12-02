---
title: EZID DOI Management with Python
date: '2025-10-07'
categories:
  - python
  - doi
---

This project offers Python scripts for interacting with the EZID API to create and verify Digital Object Identifiers (DOIs).

## Setup

1.  **Clone the Repository**: If you haven't already, clone the [EZID API repository](https://github.com/zonca/ezid_api).
2.  **Configure Credentials**: Create a `.env` file in the project root with your `EZID_USERNAME` and `EZID_PASSWORD`. This file is Git-ignored for security.
3.  **Install Dependencies**: Use `uv` to set up a virtual environment and install dependencies from `requirements.txt` (`uv venv` then `uv pip install -r requirements.txt`).

## Usage

1.  **Create a Test DOI**: Run `uv run python create_doi.py`. A successful creation will show a `201 Created` response and the DOI identifier.
2.  **Check the Status of a Test DOI**: Run `uv run python check_doi.py` to retrieve and display the DOI's metadata.

## Verification

![Screenshot of EZID Identifier Details page](img/ezid_screenshot.png)

You can verify the DOI in a web browser:

*   **View Metadata**: Access `https://ezid.cdlib.org/id/doi:10.5072/FK2/TESTDOI123` to see the raw metadata.
*   **Resolve DOI**: The DOI `https://doi.org/10.5072/FK2/TESTDOI123` will redirect to `https://www.google.com` as configured.
