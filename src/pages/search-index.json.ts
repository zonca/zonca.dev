import { getAllPosts } from '../lib/posts';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const posts = await getAllPosts();
  const index = posts.map((p) => ({
    title: p.title,
    url: `/posts/${p.id}.html`,
    date: p.date ? p.date.toISOString().slice(0, 10) : '',
    categories: p.categories,
    summary: p.summary,
  }));
  return new Response(JSON.stringify(index), {
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'public, max-age=3600' },
  });
}
