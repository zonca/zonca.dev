---
title: "Cosmosage: A Specialized AI Assistant for Cosmology"
date: 2025-12-17 10:00:00
categories: [jetstream, llm, cosmology]
layout: post
slug: cosmosage-launch
---

[Cosmosage](https://cosmosage.online/) is an AI assistant specialized in cosmology. It has been trained on thousands of cosmology papers and textbooks, starting from a large-language model base and subsequently fine-tuned on cosmology-specific data and synthetic Q&A pairs. This specialized training enables it to answer domain-specific questions more accurately than general-purpose models.

We invite the community to try it out and share feedback, report bugs, or suggest features by leaving comments on the Hugging Face model page: <https://huggingface.co/AstroMLab/AstroSage-70B>

I assisted Tijmen de Haan with the deployment of this service on Jetstream 2.

### Related posts

* [Cosmosage Unshelver](./2025-12-16-cosmosage-unshelver.md) - Technical details on the deployment controller.
* [Deploy a 70B LLM to Jetstream](./2025-09-18-deploy-70b-llm-jetstream.md) - Guide on deploying the underlying model infrastructure.
* [Deploy a ChatGPT-like LLM on Jetstream with llama.cpp](./2025-09-30-jetstream-llm-llama-cpp.md) - A broader tutorial on running GGUF models on Jetstream, adapted from the work on Cosmosage.
* [Timing the Unshelving of a Jetstream 70B LLM Instance](./2025-09-18-llm-unshelve.md) - Measurements on how fast the service can come online from a shelved state.
