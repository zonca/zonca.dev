---
categories:
- ai
- tools
date: 2026-04-21
layout: post
slug: configure-claude-code-minimax
title: Configure Claude Code with MiniMax on NRP

---

## Setup Claude Code with MiniMax models on NRP infrastructure

This guide covers configuring Claude Code to use MiniMax models through the NRP (Nautilus Research Platform) infrastructure, including setting up Brave Search for web queries.

### Why Use NRP Models and Brave Search?

Claude Code's built-in web search feature requires a paid Claude Pro subscription. By using the free NRP infrastructure with MiniMax models and configuring the Brave Search MCP server, you get:

- **Free access** to powerful LLMs without a Claude subscription
- **Web search capabilities** via Brave Search API (separate free API key required)
- **Research-friendly** infrastructure for academic users

For real-time availability of NRP models, check the [LLM Managed Service Status](https://nrp.ai/documentation/userdocs/ai/llm-managed/#live-inference-status) page.

### Available Models

The NRP platform offers several models. While this guide focuses on **MiniMax-M2**, another excellent option is **GLM 4.7** (`glm-4.7`), which performs well for coding tasks. However, GLM 4.7 is often busy due to high demand, so MiniMax-M2 serves as a reliable alternative.

### Get Your NRP API Key

First, you need an API token from the National Research Platform. See the detailed guide [Configure NRP LLM with OpenCode and Crush](./2026-01-29-configure-nrp-llm-opencode-crush.md) for instructions on generating your token at [https://nrp.ai/llmtoken/](https://nrp.ai/llmtoken/).

### Environment Variables

Add the following to your `~/.bashrc` or shell configuration (replace `your-api-key-here` with your actual token):

```bash
# Claude Code configuration for NRP with MiniMax
export ANTHROPIC_BASE_URL="https://ellm.nrp-nautilus.io/anthropic"
export ANTHROPIC_API_KEY="your-api-key-here"
export ANTHROPIC_DEFAULT_OPUS_MODEL="minimax-m2"
export ANTHROPIC_DEFAULT_SONNET_MODEL="minimax-m2"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="minimax-m2"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"
export CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY="1"
export CLAUDE_CODE_ENABLE_TELEMETRY="0"
export API_TIMEOUT_MS="3000000"
export DISABLE_TELEMETRY="1"
```

### Optional: YOLO Mode Alias

For a frictionless experience with automatic permission approval:

```bash
alias claude="claude --dangerously-skip-permissions"
```

### Brave Search MCP Server

For web search capabilities, configure the Brave Search MCP server:

1. Get a Brave Search API key from [https://brave.com/search/api/](https://brave.com/search/api/)

2. Add the MCP server configuration to your project's `.claude.json`:

```json
{
  "mcpServers": {
    "brave-search": {
      "type": "stdio",
      "command": "brave-search-mcp-server",
      "args": ["--transport", "stdio", "--brave-api-key", "YOUR_BRAVE_API_KEY"],
      "env": {}
    }
  }
}
```

3. Install the server globally (optional, for faster startup):

```bash
npm install -g @brave/brave-search-mcp-server
```

### Verification

Verify the MCP server is connected:

```bash
claude mcp list
```

You should see:

```
brave-search: brave-search-mcp-server --transport stdio --brave-api-key ... - ✓ Connected
```
