---
categories:
- data
date: '2024-08-04'
layout: post
title: Cosmic Microwave Background data licensing
---

Some thoughts on how to license and attribute data products from the Simons Observatory.

Published data products, like papers and software, should have a license, this is for example required by the [FAIR Principles](https://www.go-fair.org/fair-principles/).

We should most certainly choose a license which protects Attribution in order for the SO Collaboration to get credit. Then, we need to decide what is the best strategy to implement this Attribution.

Below we first show how other institution are handling this, then provide some options for the license and some options for implementing the Attribution guaranteed by those licenses.

## Summary

We suggest applying a default CC BY 4.0 license to all public SO data products, and tagging them with a DOI produced quarterly that apportions credit to current and past members of the collaboration.

## What other institutions/data repositories are doing

* ESA Planck data (not specific to Planck but the entire archive): [https://www.cosmos.esa.int/web/esdc/terms-and-conditions](https://www.cosmos.esa.int/web/esdc/terms-and-conditions) , they use CC BY-NC 3.0 IGO which is a modification of CC-BY non-attribution specific for InterGovermental organizations.  
* NSF Guidelines [https://new.nsf.gov/public-access\#policies](https://new.nsf.gov/public-access\#policies), “In 2022, the White House Office of Science and Technology Policy (OSTP) mandated that agencies undertake new plans to ensure that by 2025 peer-reviewed publications and associated data arising from federally funded research be made immediately and freely available upon date of publication. “ but they don’t specify a license  
* LAMBDA: No mention of any license of the data they host: [https://lambda.gsfc.nasa.gov/contact/](https://lambda.gsfc.nasa.gov/contact/)  
* FAIR: For “Reusability” it requires a license, mentions MIT and CC [https://www.go-fair.org/fair-principles/r1-1-metadata-released-clear-accessible-data-usage-license/](https://www.go-fair.org/fair-principles/r1-1-metadata-released-clear-accessible-data-usage-license/)

## Available license options for datasets

A data license tells downstream users both how they can use the data and how they should ensure appropriate attribution. Notably, unlicensed data is considered proprietary, with the copyright held by the original producer. It cannot, strictly, be used without specific permission.

* Creative Commons: CC {BY}-{NC}-{SA} 4.0 [https://creativecommons.org/licenses/by-nc-sa/4.0/](https://creativecommons.org/licenses/by-nc-sa/4.0/). This multi-faceted license contains a number of (potential) provisions:  
  * You are free to share and adapt the data, if and only if:  
    * You provide appropriate attribution (optional)  
    * You only use it for non-commercial purposes (optional)  
    * You must distribute your re-mixed material under the same license (optional)  
  * Perhaps the most appropriate license here is CC BY 4.0; i.e only requiring attribution and not restricting commercial use or remixes.  
    * We could also consider the non-commercial clause, with an ability to dual-license (i.e. if a commercial enterprise would like to use the data we can create a license specifically for them to use it).  
* Open Data Commons, similar to CC, less popular but designed for data: ODC-By [https://opendatacommons.org/licenses/by/1-0/](https://opendatacommons.org/licenses/by/1-0/)

## Attribution

We would like people that use a public dataset to be able to properly attribute the work to the SO Collaboration. If there is a related paper, clearly this should be cited, but this does not necessarily appropriately credit everyone who worked on the infrastructure for producing this open data.

### Cite a paper

Traditionally attribution is achieved by asking people to cite a specific paper, while this works well with Academia rewarding paper citations, if anyone joins the collaboration after publication of the referenced paper, they would not receive proper recognition. Moreover, some data products do not have a specific paper to refer to. Finally, given the large quantity of data that (A)SO plans to release on short timescales, there may not be a specific paper that is relevant for a particular data product.

Publishing a paper takes a lot of time, especially in a large collaboration which does a first round of internal review, therefore an author list is often obsolete by the time the paper is out. Moreover, papers on a specific topic might be spaced by 1 or 2 years and all data products published between those releases would reference an obsolete author list.

### DOI for each dataset

This is how Zenodo or Figshare work, each dataset (not necessarily each data product, but each data release) is assigned a DOI. This works well for identifying the data source but (possibly) dilutes citations. It depends a lot on the data release cycle, if data releases are rare, then this could work, each dataset has as authors the people contributing to that release. Finally, assigning each data product a DOI may be expensive and wasteful ('properly' tracked DOIs are \~$1 to mint).

### Versioned DOI for the SO collaboration

DOI can be versioned, so they allow to have a single DOI that is a general reference to all the versions, and then any number of DOIs for each specific version of the product.

In our case we would create a main DOI mostly to make it easier to find all the versions, but then whenever we release a data product, we tag it with the most recent version of the DOI.

A version of the DOI is generated every quarter (or other timescale) and tracks all current members of the SO Collaboration and those with appropriate status at that time. The actual “paper” referenced by the DOI could just be author list \+ institutions. This is the most flexible and easy to implement strategy. 
