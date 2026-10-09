---
title: "SLIC superpixels on the HEALPix grid: exploring healpy issue #1131"
date: 2026-10-09
categories: [healpy, python]
layout: post
---

An exploration of adapting the SLIC superpixel algorithm to the spherical HEALPix grid, motivated by
a recent proposal in the healpy repository.

## The origin: healpy issue #1131

healpy issue #1131 "Superpixels in healpix grid" (https://github.com/healpy/healpy/issues/1131),
opened by NinaOeh on 5 October 2026, asks whether a function generating superpixels on the HEALPix
grid would be of interest for healpy. The proposal adapts the SLIC superpixel algorithm to the
sphere and comes with a complete, working implementation (healpy_slic.py) attached to the issue.
Eric Hivon, HEALPix co-author, commented that it looks "pretty cool"; the open question is whether
such a feature belongs in healpy. Before answering, I built an exploration notebook to understand
what SLIC superpixels actually do: the executed notebook (with all plots) and the module are in this
gist: https://gist.github.com/zonca/5f78963dbe49002399533f8ef08a237c

## What are superpixels, and what is SLIC?

In 2D image processing, superpixels are the result of oversegmenting an image into a few hundred
small, contiguous regions that group neighbouring pixels with similar values - instead of working
with millions of pixels, a downstream classifier or segmenter works with a few hundred coherent
regions that mostly respect image edges. The term was introduced by Ren & Malik (ICCV 2003).

SLIC (Simple Linear Iterative Clustering, Achanta et al. 2012,
https://doi.org/10.1109/TPAMI.2012.120) is the most widely used superpixel algorithm: an adapted
k-means where each pixel is assigned to the cluster centre minimising a joint feature + spatial
distance:

D = sqrt( (d_feature / c)^2 + (d_spatial / S)^2 )

where d_feature is the difference in map value(s), d_spatial is the SPATIAL distance (in the healpy
adaptation: the angular, great-circle distance between pixel centres - this is the spherical twist),
c is the compactness parameter, and S ~ 2 sqrt(f/k) is the nominal spacing of k superpixels covering
a valid fraction f of the sphere.

- Large compactness -> spatial term dominates -> compact, regular, grid-like superpixels.
- Small compactness -> superpixels follow contours of the map.
- Only pixels within 2S of a centre are considered (local search) -> fast, roughly O(npix) per
  iteration.

The proposed healpy implementation works directly on the HEALPix grid in RING or NESTED ordering,
supports masked maps and multi-feature stacks, and offers three initialisation strategies: greedy
(k-means++ seeding on angular distance, Arthur & Vassilvitskii 2007), farthest (farthest-point
sampling), and hierarchical (centres of the coarser HEALPix level closest to the requested number of
segments - deterministic and ordering-independent by construction).

Prior art worth knowing: adapting SLIC to the sphere already exists in the computer-vision
literature for 360-degree panoramic images - "Spherical Superpixel Segmentation" (Zhao et al. 2018,
IEEE Trans. Multimedia 20(6), 1406-1417, https://doi.org/10.1109/TMM.2017.2772842). The healpy
proposal is essentially that idea (SphSLIC) realised natively on the HEALPix grid.

## What the exploration showed

The notebook (https://gist.github.com/zonca/5f78963dbe49002399533f8ef08a237c) runs the attached
implementation on synthetic nside=64 maps (gradient plus Gaussian blobs), with all plots done via
healpy's projview. Highlights:

1. Compactness is THE knob. At compactness=0.01 superpixels stretch along map contours and the
   superpixel-averaged map is nearly identical to the input; at compactness=10 the segmentation
   degenerates into a quasi-regular sky partition - a fancier ud_grade. Intermediate values give the
   classic compromise: roughly round superpixels that still snap to strong edges.

2. Performance is good. nside=256 (786,432 pixels) with 64 superpixels runs in ~29 s, converging
   after tens of assignment/update iterations.

3. RING vs NESTED: the hierarchical seeding is ordering-independent by construction, but I found
   that exact gradient ties in the low-gradient nudge (which moves seeds off edges) are broken by
   candidate order, so partitions come out ~87% identical (not 100%) across orderings. Benign - the
   results are of the same quality - and fixable with a deterministic tie-break (e.g. lowest pixel
   index).

4. Implementation review findings (all small, none blocking):
   - compactness is not validated: 0 gives a divide-by-zero warning and an all-unassigned result;
     negative values silently behave like their absolute value (the feature term is squared).
   - compactness carries the units of the map: rescaling the map by 1000 with the same compactness
     changes the segmentation (agreement drops to 61%); rescaling compactness along with the map
     reproduces it exactly. A CMB map in K vs uK therefore needs completely different values -
     normalising features internally would make compactness dimensionless.
   - connectivity is not guaranteed (inherent to SLIC, same in 2D): 3/64 superpixels came out
     spatially disconnected. If connected regions matter, SNIC (Achanta & Susstrunk, CVPR 2017,
     https://openaccess.thecvf.com/content_cvpr_2017/html/Achanta_Superpixels_and_Polygons_CVPR_2017_paper.html)
     is the standard fix.
   - duplicate centres can occur after the gradient nudge, silently giving fewer superpixels than
     requested.
   - sparse masks are handled well: polar-cap tests assigned 100% of valid pixels with all clusters
     used, thanks to a sqrt(valid fraction) rescaling of the spacing.

## A healpy plotting gotcha found along the way

hp.projscatter silently does NOTHING on projview figures - it only supports the old mollview-style
axes and returns None without any warning (the axes classes differ). To overlay points on a projview
map, scatter directly in the axes data coordinates: longitude = -phi wrapped to [-pi, pi] (astro
convention), latitude = pi/2 - theta, in radians. This is documented in the notebook.

## Verdict

The proposal works, is fast, and produces sensible segmentations; init='hierarchical' is a good
deterministic default. Points to discuss in the issue: naming (hp.slic vs superpixels()), internal
feature normalisation to make compactness dimensionless, exposing per-superpixel means as an output,
and citing Zhao et al. (2018) as the spherical prior art in the docstring.

Full executed notebook with all the plots:
https://gist.github.com/zonca/5f78963dbe49002399533f8ef08a237c (includes healpy_slic.py from the
issue).

## References

- Achanta, Shaji, Smith, Lucchi, Fua & Sustrunk (2012), SLIC Superpixels Compared to
  State-of-the-Art Superpixel Methods, IEEE TPAMI 34(11), 2274-2282,
  https://doi.org/10.1109/TPAMI.2012.120
- Ren & Malik (2003), Learning a Classification Model for Segmentation, Proc. IEEE ICCV, vol. 2, pp.
  10-17, https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/grouping/papers/ren_malik_iccv03.pdf
- Arthur & Vassilvitskii (2007), k-means++: The Advantages of Careful Seeding, Proc. ACM-SIAM SODA,
  pp. 1027-1035, https://theory.stanford.edu/~sergei/papers/kMeansPP-soda.pdf
- Zhao, Dai, Ma, Wan, Zhang & Zhang (2018), Spherical Superpixel Segmentation, IEEE Trans.
  Multimedia 20(6), 1406-1417, https://doi.org/10.1109/TMM.2017.2772842
- Wan, Xu, Zhao & Feng (2018), Spherical Superpixels: Benchmark and Evaluation, Proc. ACCV, LNCS
  11366, pp. 703-717, http://cic.tju.edu.cn/faculty/lwan/paper/sphsp18/SphSP.html
- Giraud, Borba Pinheiro & Berthoumieu (2020), Generalized Shortest Path-based Superpixels for
  Accurate Segmentation of Spherical Images, Proc. ICPR, https://arxiv.org/abs/2004.07394 (journal
  version in Pattern Recognition 2023, https://arxiv.org/abs/2509.19895)
- Achanta & Sustrunk (2017), Superpixels and Polygons Using Simple Non-Iterative Clustering, Proc.
  IEEE CVPR, pp. 4651-4660,
  https://openaccess.thecvf.com/content_cvpr_2017/html/Achanta_Superpixels_and_Polygons_CVPR_2017_paper.html
- Stutz, Hermans & Leibe (2018), Superpixels: An Evaluation of the State-of-the-Art, CVIU 166, 1-27,
  https://arxiv.org/abs/1612.01601
- Gorski, Hivon, Banday, Wandelt, Hansen, Reinecke & Bartelmann (2005), HEALPix, ApJ 622, 759-771,
  https://doi.org/10.1086/427976
