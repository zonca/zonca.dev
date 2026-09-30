import { getCollection } from 'astro:content';
import type { CollectionEntry } from 'astro:content';

export type Post = {
  id: string;
  date: Date | undefined;
  title: string;
  description?: string;
  categories: string[];
  source: string;
  notebook: boolean;
  draft: boolean;
};

function fixEntry(entry: CollectionEntry<'posts' | 'generatedPosts'>): Post {
  const id = entry.id;
  const data = entry.data;
  return {
    id,
    date: data.date ?? undefined,
    title: data.title ?? id,
    description: data.description,
    categories: data.categories ?? [],
    source: data.source ?? `posts/${id}.md`,
    notebook: !!data.notebook,
    draft: !!data.draft,
  };
}

export async function getAllPosts(): Promise<Post[]> {
  const [posts, generated] = await Promise.all([
    getCollection('posts'),
    getCollection('generatedPosts'),
  ]);
  return [...posts.map(fixEntry), ...generated.map(fixEntry)]
    .filter((p) => p.id !== 'README' && !p.draft)
    .filter((p) => p.date !== undefined)
    .sort((a, b) => (b.date!.getTime() ?? 0) - (a.date!.getTime() ?? 0));
}

export function formatDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}
