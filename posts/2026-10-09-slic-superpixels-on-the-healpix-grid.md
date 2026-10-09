---
title: "SLIC superpixels on the HEALPix grid"
date: 2026-10-09
categories: [healpy, python]
layout: post
---

NinaOeh proposed in a
[healpy issue](https://github.com/healpy/healpy/issues/1131)
a `slic` function that adapts SLIC superpixels to HEALPix maps, with a complete implementation
attached. This post is what I found testing it; the executed notebook and the module are here:
https://gist.github.com/zonca/5f78963dbe49002399533f8ef08a237c

## SLIC in one paragraph

Superpixels oversegment an image into a few hundred compact regions of similar pixels, so
downstream algorithms work with regions instead of millions of pixels. SLIC (Achanta et al. 2012)
is an adapted k-means: each pixel joins the centre minimising

D = sqrt( (d_feature / c)^2 + (d_spatial / S)^2 )

where c is the compactness parameter and S ~ 2 sqrt(f/k) the nominal spacing of k superpixels
over a valid fraction f of the sky. Large c: regular, grid-like cells. Small c: superpixels
follow the contours of the map. Only pixels within 2S of a centre are compared, so an iteration
costs ~O(npix). The healpy version uses angular distances and supports RING/NESTED, masks and
multi-feature stacks; the same idea exists for 360-degree panoramas as SphSLIC (Zhao et al. 2018).

## Findings

- Compactness is the knob: at 0.01 superpixels hug map contours and the superpixel-averaged map
  is nearly the input; at 10 the segmentation degenerates into a regular grid, a fancier
  ud_grade.
- Fast: nside=256 (786k pixels), 64 superpixels, ~29 s.
- RING vs NESTED: hierarchical seeding is ordering-independent, but exact gradient ties in the
  seed nudge are broken by candidate order, so partitions are 87% identical, not 100%; a
  deterministic tie-break would fix it.
- compactness=0 gives divide-by-zero warnings and an empty result; negative values silently
  behave like their absolute value. Needs validation.
- compactness carries the units of the map: scaling the map by 1000 with the same c drops
  agreement to 61%, scaling c with the map reproduces the segmentation exactly. Normalising
  features internally would make it dimensionless.
- Connectivity is not guaranteed (inherent to SLIC): 3/64 superpixels came out disconnected;
  SNIC (Achanta & Sustrunk 2017) fixes this if needed.
- Duplicate centres can occur after the seed nudge, silently giving fewer superpixels than
  requested.
- Sparse masks are fine: a polar-cap test assigned 100% of valid pixels.

## Verdict

Works, fast, sensible output; init='hierarchical' is a good deterministic default. Worth
discussing in the issue: naming, internal feature normalisation, exposing per-superpixel means,
citing Zhao et al. (2018) as prior art.

## References

- Achanta et al. (2012), SLIC Superpixels Compared to State-of-the-Art Superpixel Methods, IEEE
  TPAMI 34(11), 2274-2282:
  https://doi.org/10.1109/TPAMI.2012.120
- Ren & Malik (2003), Learning a Classification Model for Segmentation, IEEE ICCV:
  https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/grouping/papers/ren_malik_iccv03.pdf
- Arthur & Vassilvitskii (2007), k-means++: The Advantages of Careful Seeding, ACM-SIAM SODA:
  https://theory.stanford.edu/~sergei/papers/kMeansPP-soda.pdf
- Zhao et al. (2018), Spherical Superpixel Segmentation, IEEE Trans. Multimedia 20(6), 1406-1417:
  https://doi.org/10.1109/TMM.2017.2772842
- Wan et al. (2018), Spherical Superpixels: Benchmark and Evaluation, ACCV, LNCS 11366, 703-717:
  http://cic.tju.edu.cn/faculty/lwan/paper/sphsp18/SphSP.html
- Giraud et al. (2020), Generalized Shortest Path-based Superpixels for Accurate Segmentation of
  Spherical Images, ICPR:
  https://arxiv.org/abs/2004.07394
  (journal version, Pattern Recognition 2023: https://arxiv.org/abs/2509.19895)
- Achanta & Sustrunk (2017), Superpixels and Polygons Using Simple Non-Iterative Clustering,
  IEEE CVPR:
  https://openaccess.thecvf.com/content_cvpr_2017/html/Achanta_Superpixels_and_Polygons_CVPR_2017_paper.html
- Stutz et al. (2018), Superpixels: An Evaluation of the State-of-the-Art, CVIU 166, 1-27:
  https://arxiv.org/abs/1612.01601
- Gorski et al. (2005), HEALPix, ApJ 622, 759-771:
  https://doi.org/10.1086/427976
