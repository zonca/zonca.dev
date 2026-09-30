import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const postSchema = z.object({
  title: z.string().optional(),
  date: z.coerce.date().optional(),
  categories: z.array(z.string()).default([]),
  description: z.string().optional(),
  aliases: z.array(z.string()).optional(),
  draft: z.boolean().optional(),
  source: z.string().optional(),
  notebook: z.boolean().optional(),
  layout: z.string().optional(),
});

const pageSchema = z.object({
  title: z.string().optional(),
  description: z.string().optional(),
});

// Canonical post ID = source basename, never the legacy `slug:` front matter
// field (the current site URLs are based on source basenames).
const idFromFile = ({ entry }: { entry: string }) => entry.replace(/\.[^.]+$/, '');

export const collections = {
  posts: defineCollection({
    loader: glob({ pattern: '*.md', base: './posts', generateId: idFromFile }),
    schema: postSchema,
  }),
  generatedPosts: defineCollection({
    loader: glob({ pattern: '*.md', base: './.generated/posts', generateId: idFromFile }),
    schema: postSchema,
  }),
  pages: defineCollection({
    loader: glob({ pattern: '*.md', base: './.generated/pages', generateId: idFromFile }),
    schema: pageSchema,
  }),
};
