---
title: "Configure NRP LLM with OpenCode and Crush"
date: "2026-01-29"
categories: [ai]
---

* **UPDATED 2026-01-31**: Added details about namespace requirements for generating tokens.

The National Research Platform (NRP) provides a free Large Language Model (LLM) service for researchers. This service allows you to access powerful models like GLM 4.7, Llama 3, and Qwen 3 via an OpenAI-compatible API.

This tutorial shows how to configure two popular CLI AI tools, **Crush** and **OpenCode**, to use the NRP LLM service.

## Get your Token

First, you need to generate an API token.
Go to [https://nrp.ai/llmtoken/](https://nrp.ai/llmtoken/) and log in with your institutional credentials to get your free token.

**Note:** A user has to be a member of a namespace with LLM feature in order to be able to generate tokens.
SDSC users are privileged and are added to `sdsc-llm` namespace by a daemon every half an hour, but others might need to join a namespace first.
Faculty members can have their own namespaces and add others with no restrictions.
For more information on namespaces, see [Getting Started](https://nrp.ai/documentation/userdocs/start/getting-started/).

In your terminal, export your token to a variable (replace `...` with your actual token):

```bash
export TOKEN="your_token_here"
```

## Configure OpenCode

[OpenCode](https://opencode.ai) is a powerful terminal-based coding assistant.

To configure it for NRP, run the following command to create the configuration file:

```bash
mkdir -p ~/.config/opencode
cat <<JSON > ~/.config/opencode/opencode.json
{
  "\$schema": "https://opencode.ai/config.json",
  "provider": {
    "nrp": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "NRP Nautilus",
      "options": {
        "baseURL": "https://ellm.nrp-nautilus.io/v1",
        "apiKey": "$TOKEN"
      },
      "models": {
        "glm-4.7": { "name": "GLM 4.7" },
        "gpt-oss": { "name": "GPT-OSS" },
        "llama3-sdsc": { "name": "Llama 3 (SDSC)" },
        "qwen3": { "name": "Qwen 3" },
        "gemma3": { "name": "Gemma 3" }
      }
    }
  }
}
JSON
```

Verify it works by running:

```bash
opencode run -m nrp/gpt-oss "Hello"
```

## Configure Crush

[Crush](https://github.com/crush-sh/crush) is another excellent CLI tool.

To configure it for NRP, run this command:

```bash
mkdir -p ~/.config/crush
cat <<JSON > ~/.config/crush/crush.json
{
  "providers": {
    "nrp": {
      "id": "nrp",
      "name": "NRP Nautilus",
      "type": "openai",
      "base_url": "https://ellm.nrp-nautilus.io/v1",
      "api_key": "$TOKEN",
      "models": [
        { "id": "glm-4.7", "name": "GLM 4.7", "context_window": 256000, "default_max_tokens": 4096 },
        { "id": "glm-v", "name": "GLM V", "context_window": 256000, "default_max_tokens": 4096 },
        { "id": "gpt-oss", "name": "GPT-OSS", "context_window": 128000, "default_max_tokens": 4096 },
        { "id": "llama3-sdsc", "name": "Llama 3 (SDSC)", "context_window": 128000, "default_max_tokens": 4096 },
        { "id": "qwen3", "name": "Qwen 3", "context_window": 128000, "default_max_tokens": 4096 },
        { "id": "gemma3", "name": "Gemma 3", "context_window": 128000, "default_max_tokens": 4096 }
      ]
    }
  },
  "models": {
    "large": { "model": "glm-4.7", "provider": "nrp" },
    "small": { "model": "gpt-oss", "provider": "nrp" }
  },
  "recent_models": {
    "large": [
      { "model": "glm-4.7", "provider": "nrp" },
      { "model": "gpt-oss", "provider": "nrp" }
    ]
  }
}
JSON
```

Verify it works by running:

```bash
crush run -m nrp/glm-4.7 "Hello"
```

You are now ready to use powerful open-source models for free in your terminal!
