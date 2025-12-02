---
title: "Take control of your Kaiser Permanente blood test results (no coding knowledge required)"
author: "Andrea Zonca"
categories: [tutorial, health]
date: 2025-12-02
---

Are you tired of deciphering your Kaiser Permanente blood test results, wishing there was an easier way to track your health data over time without needing to be a coding expert? This guide will show you how to leverage readily available tools to analyze your health summary, specifically focusing on lipid panels, using a step-by-step approach.

## Step 1: Download your Health Summary from kp.org

1.  **Log in** to your kp.org account.
2.  Navigate to **"Health Summary"**.
3.  Click on **"Download Health Summary"**.

This action will download a `.zip` file to your computer.

## Step 2: Extract the Data

Locate the downloaded `.zip` file (usually in your `Downloads` folder) and **double-click it** to extract its contents. Inside, you'll find a folder structure. The actual data you need is typically located within the `IHE_XDM/Firstname1/` folder. This folder contains numerous `.xml` files, each representing different aspects of your health record.

:::callout-warning
At this point, you might have many `.xml` files (e.g., 77 in one instance). Directly feeding all of these into most AI chat interfaces like ChatGPT or Gemini is not feasible, as they often have limitations on the number of files or the total content size they can process simultaneously.
:::

## Step 3: Use GitHub and Codex (ChatGPT Plus) for Analysis

While coding experience would allow you to process these files with tools like `codex cli` or Gemini in the terminal, the easiest non-coding solution is to use **Codex**, a feature available with **ChatGPT Plus** (a paid subscription, approximately $20/month).

Here's how to do it:

1.  **Create a free account on [Github.com](https://github.com/)**.
2.  **Create a New Repository**:
    *   Click the **"+"** sign in the top right corner and select "New repository".
    *   **IMPORTANT**: Make sure to select **"Private"** for your repository. This ensures your personal health data remains secure and confidential.
    *   Check **"Add a README file"** so your repository isn't empty.
    *   Click "Create repository".
3.  **Upload Your XML Files**:
    *   Once your repository is created, click the **"Add file"** button, then select **"Upload files"**.
    *   Drag and drop all the `.xml` files from your `IHE_XDM/Firstname1/` folder into the upload area.
    *   Commit the changes.
4.  **Connect to Codex on ChatGPT**:
    *   Go to [chatgpt.com](https://chatgpt.com/).
    *   Select **Codex** (available if you have ChatGPT Plus).
    *   Follow the prompts to **link your GitHub account** and choose the private repository where you uploaded your `.xml` files.
5.  **Analyze Your Data**:
    *   In the Codex chat interface, provide a clear instruction, such as:
        > "Analyze the XML files and extract all values from the lipid panel of my blood tests to a a csv file named `lipid_panel.csv`."
    *   Let Codex work. This process might take up to 10 minutes, depending on the number and size of your files.

## Step 4: Visualize Your Results

After Codex finishes, it will generate a `lipid_panel.csv` file within your GitHub repository. You can now use this CSV data for visualization:

1.  **Open the `lipid_panel.csv` file** in your GitHub repository and **copy its entire content**.
2.  **Paste the content into the regular ChatGPT interface** (not Codex).
3.  Ask ChatGPT to create a plot. For example:
    > "I'll paste a CSV. Create a 4-panel plot with lipid values (Total Cholesterol, LDL, HDL, Triglycerides). Also add typical healthy limits for each, and shade the 'bad' areas (e.g., too high LDL, too low HDL) in red."

This process empowers you to gain meaningful insights from your health data without writing a single line of code, transforming raw XML into understandable visualizations.