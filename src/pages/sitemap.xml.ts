import { getAllPosts, getCategoryStats, filterByCategory, PAGE_SIZE } from '../lib/posts';
import type { APIContext } from 'astro';

const staticPages = [
  '/',
  '/about',
  '/ai/',
  '/ai/research',
  '/ai/operations',
  '/ai/customers',
  '/ai/bookkeeping',
  '/ai/italian-school',
  '/ai/responsible-ai',
  '/AGENTS',
  '/skill/SKILL',
  '/search',
];

function esc(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

export async function GET(context: APIContext) {
  const origin = context.site ?? 'https://www.zonca.dev';
  const posts = await getAllPosts();
  const cats = getCategoryStats(posts);
  // Archive pagination pages (page 1 is the list page itself); mirrors the
  // getStaticPaths logic in page/[page].astro and categories/[category]/page/[p].astro.
  const archivePages: string[] = [];
  for (let p = 2; p <= Math.ceil(posts.length / PAGE_SIZE); p++) {
    archivePages.push(`/page/${p}`);
  }
  for (const cat of cats) {
    const totalPages = Math.ceil(filterByCategory(posts, cat.name).length / PAGE_SIZE);
    for (let p = 2; p <= totalPages; p++) {
      archivePages.push(`/categories/${cat.slug}/page/${p}`);
    }
  }
  const urls = [
    ...staticPages.map((p) => new URL(p, origin).href),
    ...posts.map((p) => new URL(`/posts/${p.id}`, origin).href),
    ...cats.map((c) => new URL(`/categories/${c.slug}`, origin).href),
    ...archivePages.map((p) => new URL(p, origin).href),
  ];
  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls
    .map((u) => `  <url><loc>${esc(u)}</loc></url>`)
    .join('\n')}\n</urlset>`;
  return new Response(body, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
}
