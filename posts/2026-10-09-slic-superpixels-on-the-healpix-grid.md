---
title: "SLIC superpixels on the HEALPix grid"
date: 2026-10-09
categories: [healpy, python]
layout: post
---

A recent [healpy issue](https://github.com/healpy/healpy/issues/1131) proposes a `slic` function
that generates superpixels on the HEALPix grid, adapting the SLIC algorithm to the sphere, with a
complete working implementation attached. This post is what I found testing it; the executed
notebook (with all plots) and the module are here:
https://gist.github.com/zonca/5f78963dbe49002399533f8ef08a237c

## What are superpixels, and what is SLIC?

In 2D image processing, superpixels oversegment an image into a few hundred small, contiguous
regions that group neighbouring pixels with similar values: instead of working with millions of
pixels, a downstream classifier or segmenter works with a few hundred coherent regions that
mostly respect image edges.

SLIC (Achanta et al. 2012) is the most widely used superpixel algorithm, an adapted k-means:
each pixel is assigned to the cluster centre minimising a joint feature + spatial distance

D = sqrt( (d_feature / c)^2 + (d_spatial / S)^2 )

where d_feature is the difference in map value(s), d_spatial is the angular distance between
pixel and centre (the spherical twist), c is the compactness parameter, and S ~ 2 sqrt(f/k) is
the nominal spacing of k superpixels covering a valid fraction f of the sphere.

- Large compactness: the spatial term dominates and superpixels become compact, regular and
  grid-like.
- Small compactness: superpixels follow the contours of the map.
- Only pixels within 2S of a centre are compared, so an iteration costs ~O(npix): this local
  search is what makes SLIC fast, also on the sphere.

The proposed implementation works directly on the HEALPix grid in RING or NESTED ordering,
supports masked maps and multi-feature stacks, and offers three ways to place the initial
centres: greedy k-means++ seeding (random), farthest-point sampling, and hierarchical seeding at
the centres of the coarser HEALPix level closest to the requested number of segments
(deterministic and ordering-independent). The same idea exists in the computer-vision literature
as SphSLIC, for 360-degree panoramic images (Zhao et al. 2018).

## Findings

- Compactness is the knob: at 0.01 superpixels stretch along map contours and the
  superpixel-averaged map is nearly identical to the input; at 10 the segmentation degenerates
  into a quasi-regular sky partition, a fancier ud_grade. Intermediate values give roughly round
  superpixels that still snap to strong edges.
- Fast: nside=256 (786,432 pixels), 64 superpixels, ~29 s.
- RING vs NESTED: hierarchical seeding is ordering-independent by construction, but exact
  gradient ties in the low-gradient nudge (which moves seeds off edges) are broken by candidate
  order, so partitions come out 87% identical, not 100%. Same quality either way; a
  deterministic tie-break would fix it.
- compactness=0 gives divide-by-zero warnings and an all-unassigned result; negative values
  silently behave like their absolute value (the feature term is squared). Needs validation.
- compactness carries the units of the map: scaling the map by 1000 with the same compactness
  drops agreement to 61%; scaling compactness along with the map reproduces the segmentation
  exactly. A CMB map in K vs uK needs completely different values, so normalising features
  internally would make compactness dimensionless.
- Connectivity is not guaranteed (inherent to SLIC, same in 2D): 3/64 superpixels came out
  spatially disconnected. SNIC (Achanta & Sustrunk 2017) enforces connectivity if needed.
- Duplicate centres can occur after the seed nudge, silently giving fewer superpixels than
  requested.
- Sparse masks are fine: the nominal spacing is rescaled by the valid fraction, and a polar-cap
  test assigned 100% of valid pixels with all clusters used.

## Verdict

Works, fast, sensible segmentations; init='hierarchical' is a good deterministic default. Worth
discussing in the issue: naming (hp.slic vs superpixels()), internal feature normalisation,
exposing per-superpixel means as an output, citing Zhao et al. (2018) as prior art.

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
