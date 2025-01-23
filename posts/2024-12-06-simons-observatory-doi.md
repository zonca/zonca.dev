---
categories:
- data
date: '2024-12-05'
layout: post
title: Proposal for of Simons Observatory Data Products Attribution
---

## License

 `CC BY 4.0` only requiring attribution and not restricting commercial use or remixes.  

## Attribution

We would like people that use a public dataset to be able to properly attribute the work to the SO Collaboration. If there is a related paper, clearly this should be cited, but this does not necessarily appropriately credit everyone who worked on the infrastructure for producing this open data.

### Cite a paper

Traditionally attribution is achieved by asking people to cite a specific paper, while this works well with Academia rewarding paper citations, if anyone joins the collaboration after publication of the referenced paper, they would not receive proper recognition. Moreover, some data products do not have a specific paper to refer to. Finally, given the large quantity of data that (A)SO plans to release on short timescales, there may not be a specific paper that is relevant for a particular data product.

Publishing a paper takes a lot of time, especially in a large collaboration which does a first round of internal review, therefore an author list is often obsolete by the time the paper is out. Moreover, papers on a specific topic might be spaced by 1 or 2 years and all data products published between those releases would reference an obsolete author list.

### DOI for each dataset

This is the most straighforward use of DOIs, and it is how Zenodo or Figshare work, each dataset (not necessarily each data product, but each data release) is assigned a DOI.

UCSD offers a DOI service which is free to use and has API can that be used to mint DOIs for datasets programmatically within our data release pipeline.

This works well for identifying the data source but (possibly) dilutes citations. It depends a lot on the data release cycle, if data releases are rare, then this could work, each dataset has as authors the people contributing to that release.

Being all based on automated tools, in this case we also need a service (HTTP API) that automatically keeps track of the author list, so that the data release pipeline can query this service and get back the correct list of people to be added to a DOI based on the current status of the collaboration, the type of data product, and the time of the release. This service implements in software all the policies that we decide on how to assign authorship to a data product.

Examples of data products:

* Occasional data release, e.g. once every few months, this could be either simulations or real data or results of some analysis. This is straightforward, we mint a single DOI for the release with the full member list at the time of the release. This doesn't need to be completely automated, there could be a manual step where the membership list got from the automated service is merged with external collaborators and then the DOI is minted.
* Daily products, for example maps, in this case a single DOI per day would make it difficult to aggregate citations, it would be best to create a hierarchical DOI, with a canonical DOI "Simons Observatory Daily Maps" and a DOI for each month which is minted at the beginning of the month, and then data added to it. In this way we could coalesce citations for all the maps under the single canonical DOI.

See for example LIGO, for a data release they both have a page on their website with a DOI <https://gwosc.org/eventapi/html/O4_Discovery_Papers/GW230529_181500/v1/> and then they have [additional (smaller I guess) data products on Zenodo](https://zenodo.org/records/10845779) with another DOI.

### Timed DOI for the SO collaboration

This is an uncommon use of DOIs, the idea is that instead of having DOIs pointing to a specific dataset, the DOI is basically tracking the current members of the collaboration.

First we create a DOI for the "Data produced by Simons Observatory" which is the canonical DOI which ideally points to all data ever published by the collaboration. Then we use the DOI versioning system to create new DOIs regularly, for example every quarter or every 6 months which points to a single URL which collects all data produced in that period, therefore the meaning of a DOI would be for example "Data produced by Simons Observatory between January and March 2025". We can create the DOI in advance and then add the data to it as it is produced. So both data releases and daily products would be added to this DOI. If necessary, metadata of the DOI can be modified, so if we want to add a new member to the doi, we can do that.

Again, it would be best to have the management of authorship automated, and build a service that runs periodically to mint a new DOI and keep it up to date with the current membership list.

One weakness of this system is that it is not clear how to handle an outside member that collaborates just for a single product. In that case, if they are added to the DOI, they would be authors of all data products produced in that time-frame.
