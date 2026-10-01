import { getCollection } from 'astro:content';
import type { CollectionEntry } from 'astro:content';

export type Post = {
  id: string;
  date: Date | undefined;
  title: string;
  description?: string;
  summary: string;
  categories: string[];
  source: string;
  notebook: boolean;
  draft: boolean;
};

export function makeSummary(body: string, fallback: string): string {
  const lines = body.split('\n');
  const structural = /^(#{1,6}\s|```|>|[-*+]\s|\d+\.\s|\||!\[|<div|<script|<iframe|<!--)/;
  const paragraphs: string[][] = [];
  let cur: string[] = [];
  const flush = () => {
    if (cur.length) {
      paragraphs.push(cur);
      cur = [];
    }
  };
  for (const line of lines) {
    const t = line.trim();
    if (t === '') {
      flush();
      continue;
    }
    if (paragraphs.length === 0 && cur.length === 0 && structural.test(t)) continue;
    if (cur.length && structural.test(t)) flush();
    cur.push(line);
  }
  flush();

  const clean = (arr: string[]) =>
    arr
      .join(' ')
      .replace(/!\[([^\]]*)\]\([^)]*\)/g, '$1')
      .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
      .replace(/[*_`~#]/g, '')
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();

  // Keep complete sentences only - never cut mid-sentence.
  let text = clean(paragraphs[0] ?? []);
  if (text.length > 320) {
    const cut = text.slice(0, 320);
    let end = Math.max(cut.lastIndexOf('. '), cut.lastIndexOf('! '), cut.lastIndexOf('? '));
    if (end < 80) {
      const rest = text.slice(80);
      const m = rest.match(/[.!?](\s|$)/);
      end = m ? 80 + m.index! + 1 : -1;
    }
    text = end >= 0 ? text.slice(0, end + 1).trimEnd() : text.slice(0, 320).trimEnd();
  }
  if (text.length < 120 && paragraphs.length > 1) {
    const p2 = clean(paragraphs[1] ?? []);
    if (p2) text = `${text} ${p2}`;
  }
  if (text.length < 40) return fallback;
  return text;
}

function fixEntry(entry: CollectionEntry<'posts' | 'generatedPosts'>): Post {
  const id = entry.id;
  const data = entry.data;
  const body = entry.body ?? '';
  const fallback = (data.description ?? data.title ?? id) as string;
  return {
    id,
    date: data.date ?? undefined,
    title: data.title ?? id,
    description: data.description,
    summary: data.description || makeSummary(body, fallback),
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

export const PAGE_SIZE = 15;

export function slugifyCategory(cat: string): string {
  return cat.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

export function getCategoryStats(posts: Post[]): { name: string; slug: string; count: number }[] {
  // Group case-insensitively (legacy posts use both "hpc" and "HPC"); display
  // the most frequent casing as the canonical name.
  const counts = new Map<string, number>();
  const casing = new Map<string, Map<string, number>>();
  for (const p of posts) {
    for (const c of p.categories) {
      const key = c.toLowerCase();
      counts.set(key, (counts.get(key) ?? 0) + 1);
      const byCase = casing.get(key) ?? new Map<string, number>();
      byCase.set(c, (byCase.get(c) ?? 0) + 1);
      casing.set(key, byCase);
    }
  }
  const stats = [...counts.entries()].map(([key, count]) => {
    const best = [...(casing.get(key)!.entries())].sort((a, b) => b[1] - a[1])[0][0];
    return { name: best, slug: slugifyCategory(key), count };
  });
  return stats.sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
}

export function filterByCategory(posts: Post[], name: string): Post[] {
  const key = name.toLowerCase();
  return posts.filter((p) => p.categories.some((c) => c.toLowerCase() === key));
}
