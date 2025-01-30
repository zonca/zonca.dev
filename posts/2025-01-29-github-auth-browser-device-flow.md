---
categories:
- github
date: '2025-01-29'
layout: post
title: Authenticate to GitHub in the Browser with the Device Flow
---

## Introduction

Authenticating to GitHub in the browser using the device flow is essential for applications that cannot directly handle OAuth redirects. This method allows users to authenticate by entering a code on GitHub's website, making it ideal for devices with limited input capabilities or for applications running in environments where traditional OAuth flows are not feasible.

GitHub does not allow direct calls to the device flow from the browser for security reasons. The device flow requires a server process to handle the communication with GitHub's API securely. This server process acts as an intermediary, managing the device code generation, polling for user authentication, and securely storing the access token. By deploying a server process, we ensure that sensitive information is not exposed to the client-side, maintaining the integrity and security of the authentication flow.

## How It Works

The device flow works by generating a device code that the user enters on GitHub's website. The steps are as follows:

1. The client requests a device code from GitHub.
2. GitHub responds with a device code and a user code.
3. The user navigates to GitHub's device activation page and enters the user code.
4. The client polls GitHub to check if the user has completed the authentication.
5. Once authenticated, GitHub provides an access token.

## Deploying on Render.com

To deploy the server code on Render.com, follow these steps:

### Create a Github OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click on **New OAuth App**
3. Fill in the details:
   - **Application name**: `github-auth-proxy-render`
   - **Homepage URL**: `https://github.com`
   - **Authorization callback URL**: `https://localhost`
4. Make sure you enable the **Device flow** in the **OAuth Apps** settings.
5. Get the Client ID, we do not need a secret for the device flow.

### Server Deployment

1. Fork the repository [github_auth_proxy_render](https://github.com/zonca/github_auth_proxy_render).
1. Edit the file `server.js` and replace the `CLIENT_ID` with the one you got from the GitHub OAuth App.
2. Create a new web service on Render.com.
3. Connect your forked repository to the new web service.
4. Deploy the service.
5. Keep the server logs open for debugging purposes

## Test with the Client

1. Edit the file `github_device_flow_auth.html` and replace the urls with the ones from your own Render.com service.
1. Open the file with your browser
2. Click on the button to start the device flow.
3. Follow the instructions on the page.
4. If everything works as expected, you should see all of your used data dumped to the page

![GitHub Device Flow Screenshot](./github_device_flow_screenshot.png)