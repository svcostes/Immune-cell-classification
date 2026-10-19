#!/usr/bin/env python3
"""
download_from_osdr.py  (PLACEHOLDER — activate after the OSDR upload is complete)
=================================================================================

Downloads the raw imaging data (and any tabular inputs) for this project from the
NASA Open Science Data Repository (OSDR) and places them where the notebooks expect
them:

    *.tif / *.tiff   ->  data/representative_images/
    *.csv / *.xlsx   ->  data/

Why this is a placeholder: the OSDR accession (OSD-1027) has not been finalised /
published yet, so the file list it returns is currently empty or unresolved. Once
the OSDR upload is complete, this script is expected to work as-is; the only thing
that should need changing is the ACCESSION constant below (and, if the deposited
folder layout differs, the DEST mapping in `classify_destination`).

Endpoints used (NASA OSDR "Biological Data API", BDAPI — verified against a live
accession, OSD-37, on 2026-10-13):

  1. File listing (REST, JSON):
       https://visualization.osdr.nasa.gov/biodata/api/v2/dataset/{ACCESSION}/assay/*/sample/*/files/

     Each file entry carries:
       "file name"  -> the deposited filename
       "URL"        -> the signed download URL, of the form
                       https://osdr.nasa.gov/geode-py/ws/studies/{ACCESSION}/download?source=datamanager&file={name}

  2. Metadata query (CSV, alternative to the REST listing):
       https://visualization.osdr.nasa.gov/biodata/api/v2/query/metadata/?id.accession={ACCESSION}&file.filename

Refs:
  https://visualization.osdr.nasa.gov/biodata/api/
  https://github.com/nasa/OSDR_Tutorials (guide: "Use the Biological Data API")
"""

import json
import os
import urllib.parse
import urllib.request

# ---------------------------------------------------------------------------
# TODO(OSDR upload): confirm this accession string once the deposit is final.
# The manuscript cites the repository as OSDR; the accession expected here is
# OSD-1027. If the published accession differs, change this one constant.
# ---------------------------------------------------------------------------
ACCESSION = "OSD-1027"

# Where the repo lives (script is at src/download_from_osdr.py, so root is ../).
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "representative_images")

API_ROOT = "https://visualization.osdr.nasa.gov/biodata/api/v2"


def list_files(accession: str) -> dict:
    """Return the raw JSON file-listing for an OSDR accession."""
    url = (
        f"{API_ROOT}/dataset/{urllib.parse.quote(accession)}"
        "/assay/*/sample/*/files/"
    )
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.load(resp)


def iter_files(listing: dict):
    """Yield (filename, download_url) pairs from a BDAPI file-listing JSON.

    The listing nests as  accession -> assays -> {assay} -> samples -> {sample}
    -> files -> {filename} -> {"URL": ...}.  We walk it generically so the code
    is robust to however OSDR organises the deposited assays/samples.
    """
    def walk(node):
        if isinstance(node, dict):
            # A file entry: a dict that has both "file name" and "URL".
            name = node.get("file name")
            url = node.get("URL")
            if name and url:
                yield name, url
            for value in node.values():
                yield from walk(value)
        elif isinstance(node, list):
            for item in node:
                yield from walk(item)

    yield from walk(listing)


def classify_destination(filename: str) -> str:
    """Map a deposited filename to its local directory."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in (".tif", ".tiff"):
        # TODO(OSDR upload): if OSDR flattens the images into per-field folders
        # (as in the current local layout), preserve any relative subpath here.
        return IMAGES_DIR
    if ext in (".csv", ".xlsx", ".xls"):
        return DATA_DIR
    return os.path.join(DATA_DIR, "other")


def main() -> None:
    os.makedirs(IMAGES_DIR, exist_ok=True)

    print(f"Listing files for OSDR accession {ACCESSION} ...")
    listing = list_files(ACCESSION)

    files = list(iter_files(listing))
    if not files:
        # ------------------------------------------------------------------
        # TODO(OSDR upload): expected until the deposit is published — the
        # listing is empty because the accession is not live yet. Remove this
        # guard once the upload completes.
        # ------------------------------------------------------------------
        print(
            f"No files found for {ACCESSION}. "
            "This is expected while the OSDR upload is still pending.\n"
            "Once the deposit is live, re-run this script to fetch the images."
        )
        return

    print(f"Found {len(files)} file(s). Downloading ...")
    for name, url in files:
        dest = os.path.join(classify_destination(name), os.path.basename(name))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if os.path.exists(dest):
            print(f"  skip (exists): {name}")
            continue
        print(f"  download: {name}")
        urllib.request.urlretrieve(url, dest)

    print("Done. Files placed under data/ (images -> data/representative_images/).")


if __name__ == "__main__":
    main()
