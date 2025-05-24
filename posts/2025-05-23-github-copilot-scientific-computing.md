---
categories:
- github
- ai
- python
date: '2025-05-23'
layout: post
title: How to use GitHub Copilot for Scientific Computing
---

GitHub Copilot is rapidly transforming the landscape of scientific computing by streamlining code development and accelerating research workflows. This guide outlines how computational scientists can leverage Copilot, with a focus on professional and research-oriented use cases.

## 1. Accessing GitHub Copilot with an Academic Discount

Researchers and educators at accredited institutions can obtain free access to GitHub Copilot by verifying their academic status:

- Visit the [GitHub Education Benefits page](https://github.com/settings/education/benefits).
- Sign in with your GitHub account.
- Apply using your institutional email address (e.g., `.edu`).
- Upon approval, Copilot and other academic resources will be available at no cost.

## 2. Installing Visual Studio Code (VS Code)

VS Code is the recommended environment for integrating GitHub Copilot into scientific workflows:

- Download VS Code from the [official website](https://code.visualstudio.com/).
- Follow the installation instructions for your operating system (Linux, macOS, or Windows).

## 3. Enabling GitHub Copilot in VS Code

- Launch VS Code and open the Extensions view (`Ctrl+Shift+X`).
- Search for "GitHub Copilot" and install the extension.
- Authenticate with your GitHub account to activate Copilot.

## 4. Using Visual Studio Code at NERSC

Visual Studio Code can be used at NERSC on both login and compute nodes. For setup instructions and details, refer to the official documentation: [Using VS Code at NERSC](https://docs.nersc.gov/connect/vscode/).

## 5. Enabling GitHub Copilot Model Context Protocol (MCP) and Interacting with Issues/PRs

GitHub Copilot's Model Context Protocol (MCP) allows the Copilot extension to access a broader context from your project, improving the relevance and quality of code suggestions. Additionally, with the MCP server, you can interact directly with GitHub issues and pull requests from within VS Code.

To enable MCP and these features:

- Visit the [GitHub MCP Server page](https://github.com/github/github-mcp-server).
- Click the **Install** icon to add the MCP server to your GitHub account or organization. This step is straightforward and only requires a single click.

The most complex part of the setup is obtaining a personal access token (PAT) for authentication:

- To generate a classic token, go to your [GitHub settings](https://github.com/settings/tokens?type=beta), select "Generate new token (classic)", and grant the necessary scopes (typically `repo`, `workflow`, and `read:org`).
- Use this token when prompted by the MCP server or the Copilot extension.

**Note:** The GitHub MCP server requires Docker to run, which is not supported on NERSC systems due to network and security restrictions. If you are working in such a restricted environment, you will not be able to use MCP features, but Copilot will continue to function in its standard mode.

## 6. Practical Hints for Effective Use

1. **Always use Copilot in agent mode**: This enables the most advanced features, including context awareness and code reasoning.
2. **Select the best model**: As of now, GPT-4.1 provides the highest quality completions. Gemini 2.5 Pro is the next best option. If you notice a model repeatedly making the same mistake, try switching to another model.
3. **Iterate when stuck**: If Copilot gets stuck or produces incorrect code, switch models or rephrase your prompt to encourage a different approach.
4. **Jupyter Notebook support is limited**: Copilot's integration with Jupyter Notebooks is not as robust as with standard code files. The most effective workflow is to generate code cell by cell using the inline Copilot suggestions.
5. **Leverage context**: Provide clear comments or function signatures to help Copilot understand your intent and generate more relevant code.
6. **Review and validate**: Always review Copilot's suggestions for correctness, especially in scientific computing workflows where accuracy is critical.

