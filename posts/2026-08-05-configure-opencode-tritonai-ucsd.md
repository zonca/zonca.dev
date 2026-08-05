---
title: "Configure opencode to use TritonAI Developer API at UC San Diego"
date: 2026-08-05
categories: [ai, llm, tools]
layout: post
description: "A step-by-step tutorial for adding UC San Diego's TritonAI Developer API as a provider in opencode, including how to request access, find available models, and test them."
---

[opencode](https://opencode.ai) is a terminal-based AI coding agent that supports any
OpenAI-compatible API as a provider. UC San Diego's [TritonAI Developer
API](https://tritonai.ucsd.edu/developer-apis/index.html) is exactly that: a secure,
centralized LLM gateway powered by LiteLLM that provides access to both commercial cloud
models and self-hosted open-source models running on SDSC infrastructure.

This tutorial walks through the full setup: requesting access, discovering available models,
adding TritonAI as an opencode provider, and testing that everything works.

## Request API access

Before you can use the TritonAI Developer API, you need to request access through the
[Kuali Build form](https://tritonai.ucsd.edu/developer-apis/start.html). You will need:

- Your UC San Diego credentials
- Department and project information
- An intended use case description
- A chart string for billing (only for usage beyond free credits)

Access requests are typically reviewed within 2-3 business days. Once approved, you
receive an API key and **$15 per month in free credits** for self-hosted models.

::: {.callout-important title="Limited free credits"}
All UCSD affiliates receive **$15/month** in free credits for self-hosted models by default.
This is designed for experimentation, coursework, and light prototyping. If you need more
capacity or access to cloud-hosted commercial models (GPT-4, Claude, Gemini), you can request
[Extended Access](https://tritonai.ucsd.edu/developer-apis/faq.html) with a chart string for
billing. Credits refresh monthly and are non-transferable.
:::

## Store your API key

Once you receive your API key, store it as an environment variable. Add this line to your
`~/.bashrc` or `~/.zshrc`:

```bash
export TRITONGPTKEY='your-api-key-here'
```

Then reload your shell:

```bash
source ~/.bashrc
```

## Discover available models

The TritonAI API exposes a standard OpenAI-compatible `/v1/models` endpoint. Query it with
your API key to see what is available:

```bash
curl -s "https://tritonai-api.ucsd.edu/v1/models" \
  -H "Authorization: Bearer $TRITONGPTKEY" | python3 -m json.tool
```

At the time of writing, the API returns the following models:

| Model ID | Type | Max context |
|----------|------|-------------|
| `api-gpt-oss-120b` | Chat (reasoning) | 128k |
| `api-glm-5.2` | Chat (reasoning) | 320k |
| `api-gemma-4-26b` | Chat (reasoning) | 128k |
| `api-gemma-4-31b` | Chat (reasoning) | 256k |
| `api-deepseek-v4-flash` | Chat | 1M |
| `api-cohere-transcribe` | Audio transcription | — |
| `api-lightonocr-1b` | OCR | 8k |
| `api-tgpt-embeddings` | Embeddings | 32k |

The self-hosted models (those starting with `api-`) run on UC San Diego infrastructure at the
San Diego Supercomputer Center, meaning your data never leaves campus. This makes them suitable
for research involving sensitive data that does not require P4/Health classification.

## Add TritonAI as an opencode provider

opencode stores its configuration in `~/.config/opencode/opencode.json`. The config uses the
`@ai-sdk/openai-compatible` npm package for any OpenAI-compatible provider.

Here is a complete minimal config file that adds TritonAI as a provider with all five chat
models:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": "allow",
  "provider": {
    "tritonai": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "TritonAI UCSD",
      "options": {
        "baseURL": "https://tritonai-api.ucsd.edu/v1",
        "apiKey": "YOUR_TRITONGPTKEY"
      },
      "models": {
        "gpt-oss-120b": { "name": "GPT-OSS 120B" },
        "glm-5.2": { "name": "GLM 5.2" },
        "gemma-4-26b": { "name": "Gemma 4 26B" },
        "gemma-4-31b": { "name": "Gemma 4 31B" },
        "deepseek-v4-flash": { "name": "DeepSeek V4 Flash" }
      }
    }
  }
}
```

::: {.callout-warning title="Keep your API key private"}
The `apiKey` field above contains a real key for illustration. In your own config, use your
own key. Never commit your API key to version control or share it publicly.
:::

### How the config maps to opencode model names

opencode references models using the pattern `provider/model-id`. With the config above, you
get:

- `tritonai/gpt-oss-120b`
- `tritonai/glm-5.2`
- `tritonai/gemma-4-26b`
- `tritonai/gemma-4-31b`
- `tritonai/deepseek-v4-flash`

You can switch between them in the opencode interface or set a default model in the config
with the `"model"` field at the top level.

## Test the models

Before relying on the models for coding work, test each one with a simple request. This
verifies that your API key is valid, the models are online, and the opencode configuration is
correct.

### Quick curl test

```bash
curl -s "https://tritonai-api.ucsd.edu/v1/chat/completions" \
  -H "Authorization: Bearer $TRITONGPTKEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "api-deepseek-v4-flash", "messages": [{"role": "user", "content": "What is 2+2?"}], "max_tokens": 200}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['choices'][0]['message']['content'])"
```

::: {.callout-note title="Use enough max_tokens for reasoning models"}
Most TritonAI models produce a `reasoning_content` field before the final `content`. If
`max_tokens` is too low (e.g. 50), the model spends all tokens on reasoning and returns
`null` for content. Use at least 200 tokens for simple queries.
:::

### Test all chat models at once

```bash
for model in api-gpt-oss-120b api-glm-5.2 api-gemma-4-26b api-gemma-4-31b api-deepseek-v4-flash; do
  echo "=== $model ==="
  curl -s "https://tritonai-api.ucsd.edu/v1/chat/completions" \
    -H "Authorization: Bearer $TRITONGPTKEY" \
    -H "Content-Type: application/json" \
    -d "{\"model\": \"$model\", \"messages\": [{\"role\": \"user\", \"content\": \"What is 2+2? Answer with just the number.\"}], \"max_tokens\": 200}" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['choices'][0]['message'].get('content','(no content)'))"
  echo ""
done
```

All five models should respond. The `api-deepseek-v4-flash` and `api-gpt-oss-120b` models
tend to return concise answers, while the Gemma and GLM models may include reasoning traces
before the final answer.

## Monitoring your credit usage

You can check your current spend and remaining budget through the `/key/info` endpoint:

```bash
curl -s "https://tritonai-api.ucsd.edu/key/info" \
  -H "Authorization: Bearer $TRITONGPTKEY" | python3 -m json.tool
```

The response includes fields like `spend`, `max_budget`, and `budget_reset_at` so you can
track how much of your $15 monthly allocation you have used.

## Combining TritonAI with other providers

One of the strengths of opencode is that you can configure multiple providers side by side.
For example, you might use TritonAI for self-hosted models (keeping sensitive data on campus)
and a commercial provider for frontier model capabilities. Simply add additional blocks under
the `"provider"` key.

## Summary

UC San Diego's TritonAI Developer API provides a secure, OpenAI-compatible gateway to both
self-hosted and cloud-hosted LLMs. By adding it as a provider in opencode, you get a
terminal-based AI coding agent backed by campus infrastructure. The $15/month free credit
allocation is sufficient for experimentation and light prototyping with the self-hosted
models.

For more information, see the [TritonAI Developer API
documentation](https://tritonai.ucsd.edu/developer-apis/index.html), the [Get
Started](https://tritonai.ucsd.edu/developer-apis/start.html) page, and the
[FAQs](https://tritonai.ucsd.edu/developer-apis/faq.html).
