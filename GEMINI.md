# Gemini CLI Guidelines for zonca.dev

This document outlines specific guidelines for interacting with the `zonca.dev` website project using the Gemini CLI.

## General Workflow

- **New Blog Posts or Significant Features:** For new blog posts, major feature additions, or changes that significantly alter existing content or structure, **you must** start from the `main` branch, create a new topic branch for your changes, and then open a pull request using `gh pr create`. This ensures proper review and integration.
- **Minor Changes and Fixes:** For minor changes, typo corrections, or small bug fixes that do not warrant a full review process, you may commit directly to `main` and push.
- **Commit and Push:** After making any changes, always commit your changes and push them to the remote repository. This ensures that your work is saved and synchronized.

## Blog Post Categories

- **Existing Categories Only:** When creating or modifying blog posts, **do not invent new categories**. Only use categories that have been previously used in other posts. To find existing categories, you can inspect the `_metadata.yml` file in the `posts/` directory or check individual post files.
- **Do Not Create New Categories:** Never create new categories unless specifically instructed to do so.

## Image Referencing in Blog Posts

When referencing images in blog posts, always use paths relative to the post's directory. If the image is in a subdirectory named `img` within the post's directory, the path should be `img/your_image.png`. Avoid using absolute paths like `/img/your_image.png`.