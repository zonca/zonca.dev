# Gemini CLI Guidelines for zonca.dev

This document outlines specific guidelines for interacting with the `zonca.dev` website project using the Gemini CLI.

## General Workflow

- **New Blog Posts:** When creating a new blog post, always start from the `main` branch, create a new topic branch for your changes, and then open a pull request using `gh pr create`.
- **Commit and Push:** After making any changes, always commit your changes and push them to the remote repository. This ensures that your work is saved and synchronized.
- **Autonomous Commits:** You do not need to ask for permission before committing or double-check commit messages. Proceed with committing and pushing once changes are complete.

## Blog Post Categories

- **Existing Categories Only:** When creating or modifying blog posts, **do not invent new categories**. Only use categories that have been previously used in other posts. To find existing categories, you can inspect the `_metadata.yml` file in the `posts/` directory or check individual post files.
- **Do Not Create New Categories:** Never create new categories unless specifically instructed to do so.

## Image Referencing in Blog Posts

When referencing images in blog posts, always use paths relative to the post's directory. If the image is in a subdirectory named `img` within the post's directory, the path should be `img/your_image.png`. Avoid using absolute paths like `/img/your_image.png`.