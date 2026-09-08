---
title: "TSCC NIST SP 800-171 compliant environment for sensitive research data"
date: '2026-09-07'
categories: [sdsc, hpc]
layout: post
description: "The Triton Shared Computing Cluster at SDSC now offers a NIST SP 800-171 compliant environment for researchers handling NIH Controlled Access Data and Controlled Unclassified Information. Here's what it is, who should use it, and how to request access."
---

As of **January 2026**, the Triton Shared Computing Cluster (TSCC) at the San Diego Supercomputer
Center (SDSC) has been designated a **NIST SP 800-171 compliant** environment by UC San Diego. This
secure environment is intended for researchers who must process, store, or transmit Controlled
Unclassified Information (CUI) or National Institutes of Health (NIH) Controlled Access Data (CAD),
and it provides a shared, professionally managed computing platform that meets federal
cybersecurity and data protection requirements while preserving the flexibility and performance
expected from TSCC.

### Why this matters now

NIH requires that researchers who access controlled-access data from NIH repositories — including
sensitive genomic datasets such as those in **dbGaP** — protect that data in accordance with
**NIST SP 800-171**, *"Protecting Controlled Unclassified Information in Nonfederal Information
Systems and Organizations."* Under the NIH [Security Best Practices for Users of Controlled-Access
Data](https://grants.nih.gov/sites/default/files/flmngr/NIH-Security-BPs-for-Users-of-Controlled-Access-Data.pdf),
approved users must attest that their institution's computing environment meets this security
baseline. This applies to studies subject to the NIH Genomic Data Sharing (GDS) policy as of
**January 25, 2025**, and to all NIH Controlled-Access Data Repositories (CADRs) for access
agreements effective **February 25, 2026**.

TSCC's compliant environment lets researchers analyze this data on campus cyberinfrastructure
rather than standing up (and paying for) their own compliant system. As SDSC's Cyberinfrastructure
Solutions and Services manager and TSCC program director, Subhashini Sivagnanam, put it:
> "We are now able to ensure that researchers securely work with regulated biomedical and genomic
> datasets while meeting the federal cybersecurity and data protection requirements mandated for
> NIH-controlled research data."

## Who should use this environment

Researchers working with NIH CAD or other sensitive research data that requires NIST SP 800-171
compliance should request access to the TSCC compliant environment. To *access* NIH CAD, you need
an **institutional attestation** confirming that your computing environment meets NIST SP 800-171.
Coordinate with your campus **Office of Information Assurance (OIA)** or Health Sciences IT
organization to obtain the attestation required for submission to NIH. (Non-U.S. users who cannot
attest to NIST SP 800-171 may instead attest to the equivalent **ISO/IEC 27001/27002** standard.)

## How to request access

To initiate access, email [TSCC Support](mailto:tscc-support@ucsd.edu) and include the following
information in your request:

* Your name and affiliation (department/institution)
* A brief description of the research project
* A description of the data that will be accessed or processed
* Whether you have already completed the required campus attestation for handling controlled data
* Your preferred usage model (Hotel or Condo), with details:
  * **Hotel**: how many hours you plan to use (10,000 core-hours minimum)
  * **Condo**: number and type of nodes you plan to purchase
* Your estimated number of users

## Available usage models

The TSCC compliant environment maintains the flexibility expected from a shared research computing
system, offering two allocation models, both centrally managed by the TSCC team:

* **Hotel Program**: Flexible, pay-as-you-go compute access for short-term or variable usage, with
  a 10,000 base core-hour minimum purchase.
* **Condo Program**: Purchase dedicated nodes within the shared cluster, managed by the TSCC team.

## Security controls

The compliant environment enforces stricter controls than the standard cluster, per the
[CUI/CAD / NIST 800-171 Acceptable Use Policy (AUP)](https://www.sdsc.edu/_files/docs/SDSC_TSCC_NIST_AUP.pdf),
which users must additionally sign on top of the general TSCC AUP. Key requirements include:

* **Access via SSH with Duo multi-factor authentication**; access from mobile devices is prohibited,
  and sessions automatically terminate after **90 minutes of inactivity**.
* **Data stays in the environment.** Client workstations are non-CUI systems — you may not copy,
  download, upload, or screen-capture CUI/CAD from TSCC to a client machine. CUI/CAD must reside
  exclusively in approved TSCC Compliance storage (USS compliance storage).
* **No external USB or removable media**, no printing, and no split-tunneling/network bridging
  between the compliant environment and other networks.
* **Limited data scope**: only CUI/CAD may be stored — ITAR-, EAR-, FISMA-, HIPAA-, or patient
  personal data are not permitted on this system.
* The **PI** (or sponsoring organization) is responsible for verifying that each external user has
  obtained all required approvals and attestations before access.

Note that the TSCC project filesystem (`/tscc/projects`) is **not** managed by TSCC itself — it is
available for purchase through the SDSC RDS group, and only SDSC-operated storage may be mounted
on it.

## Onboarding process

Access to the NIST 800-171 compliant TSCC environment follows these steps:

1. **Eligibility verification**: TSCC administrators coordinate with the UC San Diego campus
   compliance office to verify which users are authorized to access the controlled data and the
   secure system.
2. **User agreements**: All approved users must sign the TSCC Acceptable Use Policy (AUP) — and,
   for this environment, the CUI/CAD / NIST AUP — before access is granted.
3. **Principal Investigator agreement**: The PI must sign a Memorandum of Understanding (MOU)
   confirming the selected usage model and associated costs.
4. **Account provisioning**: Once documentation and approvals are complete, accounts are provisioned
   and users receive onboarding instructions for the secure environment.

## Rates

| Item | UC Rate | Non-UC Rate |
|------|---------|-------------|
| NIST node system setup (one time per node/server) | $5,039 | $8,063 |
| NIST Condo Operations — CPU node (per node/year) | $2,382 | $3,812 |
| NIST Condo Operations — GPU node (per node/year) | $7,889 | $12,622 |
| NIST Hotel (per service unit, 10K core-hours minimum) | $0.1402 | $0.2253 |

Recharge rates are subject to change with approval from the UC San Diego Recharge Rate Committee.

## Indirect costs (IDC) for UC San Diego users

SDSC cloud services — including TSCC — are **exempt from UC San Diego Indirect Costs (IDC)** when
acquired to support extramurally funded research. Include these costs in the exclusions for
*modified total direct costs (MTDC)* when developing budgets for new proposals.

## Impact for researchers

Achieving NIST SP 800-171 compliance involved a rigorous review of the system security plan,
controls, and data handling practices across the TSCC environment. As SDSC Chief Information
Security Officer **Winston Armstrong** noted:
> "Working closely with the TSCC team and campus OIA, we were able to build a compliant
> infrastructure for researchers to work with NIH data that is required to meet the new CAD
> requirement."

By providing this environment, SDSC streamlines access to advanced computing resources, letting
researchers leverage the performance of TSCC without compromising their security or compliance
obligations — a key capability as the research community increasingly handles regulated biomedical
and genomic data.

For details on access procedures, required documentation, and rates, email
[TSCC Support](mailto:tscc-support@ucsd.edu) or visit the
[TSCC NIST compliance information page](https://www.sdsc.edu/systems/tscc/nist.html).

*This post is based on the [SDSC announcement](https://www.sdsc.edu/news/2026/PR20260602-TSCC-secure.html),
the [TSCC NIST compliance page](https://www.sdsc.edu/systems/tscc/nist.html), the
[CUI/CAD / NIST AUP](https://www.sdsc.edu/_files/docs/SDSC_TSCC_NIST_AUP.pdf), and the
[NIH Security Best Practices for Users of Controlled-Access Data](https://grants.nih.gov/sites/default/files/flmngr/NIH-Security-BPs-for-Users-of-Controlled-Access-Data.pdf).*
