import { getAllPosts, getCategoryStats, filterByCategory, PAGE_SIZE } from '../lib/posts';
import type { APIContext } from 'astro';

// `/search` is deliberately absent: it is a client side search UI with no
// content of its own, it carries `noindex`, and listing it in the sitemap was
// asking Google to index a duplicate of nothing. See Base.astro `noindex`.
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
];

type Entry = { loc: string; lastmod?: string };

function iso(date: Date | undefined): string | undefined {
  return date ? date.toISOString().slice(0, 10) : undefined;
}

function esc(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

export async function GET(context: APIContext) {
  const origin = context.site ?? 'https://www.zonca.dev';
  const posts = await getAllPosts();
  const cats = getCategoryStats(posts);
  // List pages change when a newer post lands on them, so their lastmod is the
  // date of the newest post they list, not the build date. Static pages have no
  // honest date, so they carry none: an invented lastmod teaches Google to
  // distrust the field.
  const lastmodOfPage = (index: number) => iso(posts[index]?.date);

  const entries: Entry[] = staticPages.map((p) => ({ loc: new URL(p, origin).href }));
  entries.push(...posts.map((p) => ({ loc: new URL(`/posts/${p.id}`, origin).href, lastmod: iso(p.date) })));

  for (const cat of cats) {
    const catPosts = filterByCategory(posts, cat.name);
    entries.push({ loc: new URL(`/categories/${cat.slug}`, origin).href, lastmod: iso(catPosts[0]?.date) });
    const totalPages = Math.ceil(catPosts.length / PAGE_SIZE);
    for (let p = 2; p <= totalPages; p++) {
      entries.push({
        loc: new URL(`/categories/${cat.slug}/page/${p}`, origin).href,
        lastmod: iso(catPosts[(p - 1) * PAGE_SIZE]?.date),
      });
    }
  }

  const archivePages = Math.ceil(posts.length / PAGE_SIZE);
  for (let p = 2; p <= archivePages; p++) {
    entries.push({ loc: new URL(`/page/${p}`, origin).href, lastmod: lastmodOfPage((p - 1) * PAGE_SIZE) });
  }

  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${entries
    .map((e) => `  <url><loc>${esc(e.loc)}</loc>${e.lastmod ? `<lastmod>${e.lastmod}</lastmod>` : ''}</url>`)
    .join('\n')}\n</urlset>`;
  return new Response(body, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
}
