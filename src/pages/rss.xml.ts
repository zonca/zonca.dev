import rss from '@astrojs/rss';
import { getAllPosts, formatDate } from '../lib/posts';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const posts = await getAllPosts();
  return rss({
    title: 'Andrea Zonca',
    description: 'Scientific computing, astronomy, and AI.',
    site: context.site ?? 'https://www.zonca.dev',
    items: posts.map((post) => ({
      title: post.title,
      description: post.description,
      link: `/posts/${post.id}.html`,
      pubDate: post.date,
    })),
  });
}
