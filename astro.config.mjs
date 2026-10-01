import { defineConfig } from 'astro/config';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rewriteInternalLinks from './src/plugins/internal-links.mjs';

export default defineConfig({
  site: 'https://www.zonca.dev',
  output: 'static',
  build: {
    format: 'file',
  },
  trailingSlash: 'never',
  compressHTML: true,
  markdown: {
    remarkPlugins: [remarkMath, rewriteInternalLinks],
    rehypePlugins: [[rehypeKatex, { throwOnError: false }]],
  },
});
