---
title: "healpy 1.20.1: last release with macOS 14 wheels"
date: 2026-10-03
categories: [healpy, github]
layout: post
description: "The healpy 1.20.1 release includes bug fixes and is the final release to provide macOS 14 arm64 wheels before the GitHub runner retirement."
---

The [healpy 1.20.1 release](https://github.com/healpy/healpy/releases/tag/1.20.1) is now available
on [PyPI](https://pypi.org/project/healpy/1.20.1/). This release introduces several important bug
fixes and new features, but it is primarily notable because it marks the final release that will
ship macOS 14 arm64 wheels.

---

## macOS 14 runner retirement context

GitHub is retiring its macOS 14 hosted runner image on November 2, 2026, with brownout windows
causing temporary job failures starting on October 5, 2026. Because healpy built its macOS 14 arm64
wheels (`macosx_14_0_arm64`) using this runner, version 1.20.1 will be the last release to support
it.

Moving forward, future releases will target macOS 15. The underlying issue is that the Homebrew
OpenMP runtime (`libomp`) used to build the wheels now requires macOS 15 or newer. Consequently, a
wheel tagged for macOS 14 would fail to load, as `cibuildwheel`'s delocate step rejects it.
Upgrading to the newest GitHub runner (macOS 26) was not yet possible since the pinned Homebrew
`llvm@15` compiler cannot build against the macOS 26 SDK.

Users on macOS 14 Apple Silicon can remain on version 1.20.1, and `pip` will automatically resolve
to this newest compatible wheel. The CI migration details can be found in [pull request
#1129](https://github.com/healpy/healpy/pull/1129), where wheel builds were moved to macOS 15, and
the release checklist is tracked in [issue #1130](https://github.com/healpy/healpy/issues/1130).

---

## What's new in 1.20.1

This release brings a few key improvements and fixes to the library:

*   **Fix:** `rotate_alm` in-place updates now correctly copy rotated coefficients back for non-C-contiguous `complex128` inputs ([issue #702](https://github.com/healpy/healpy/issues/702)).
*   **Fix:** `lonlat2thetaphi` with `latauto=True` no longer modifies caller-owned arrays and now
  correctly accepts read-only arrays ([pull request
  #1123](https://github.com/healpy/healpy/pull/1123)).
*   **Feature:** `write_cl` gained a `column_units` argument to store units in the FITS `TUNITn`
  keywords, and it now raises a `ValueError` when the length of `column_names` mismatches the `cl`
  arrays ([pull request #828](https://github.com/healpy/healpy/pull/828)).
*   **Dev:** The test data path has been centralized in a `DATAPATH` constant.

---

## Release stats

The release consists of 36 files uploaded to PyPI. These include the source distribution (`sdist`)
and wheels for `cp310` through `cp314`, covering Linux `manylinux` 2.28, macOS arm64, and macOS
x86_64 architectures.
