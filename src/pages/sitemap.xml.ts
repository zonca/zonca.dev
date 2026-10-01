import { getAllPosts, getCategoryStats } from '../lib/posts';
import type { APIContext } from 'astro';

const staticPages = [
  '/',
  '/about',
  '/ai',
  '/ai/research',
  '/ai/operations',
  '/ai/customers',
  '/ai/bookkeeping',
  '/ai/italian-school',
  '/ai/responsible-ai',
  '/GEMINI',
  '/AGENTS',
  '/skill/SKILL',
];

function esc(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

export async function GET(context: APIContext) {
  const origin = context.site ?? 'https://www.zonca.dev';
  const posts = await getAllPosts();
  const cats = getCategoryStats(posts);
  const urls = [
    ...staticPages.map((p) => new URL(p, origin).href),
    ...posts.map((p) => new URL(`/posts/${p.id}`, origin).href),
    ...cats.map((c) => new URL(`/categories/${c.slug}`, origin).href),
  ];
  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls
    .map((u) => `  <url><loc>${esc(u)}</loc></url>`)
    .join('\n')}\n</urlset>`;
  return new Response(body, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
}
