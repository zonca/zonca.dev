import { visit } from 'unist-util-visit';

// Normalizes internal Markdown links to the canonical extensionless
// /posts/<slug> route (the final public URL served by Cloudflare):
//   ./foo.md or foo.md   -> /posts/foo
//   /posts/foo.md        -> /posts/foo
//   /posts/foo.html      -> /posts/foo
//   /posts/foo/          -> /posts/foo
// Keeps anchors and query strings. Leaves absolute, external and fragment
// links untouched.
function rewriteInternalLinks() {
  return (tree) => {
    visit(tree, 'link', (node) => {
      if (typeof node.url !== 'string') return;
      const url = node.url;

      // Relative links to post sources: foo.md, ./foo.md
      const rel = url.match(/^(\.\/)?([^/#?]+?)\.(md|qmd|markdown)([#?].*)?$/i);
      if (rel && !/^(https?:|mailto:|tel:|#|\/|\.\.\/)/.test(url)) {
        node.url = `/posts/${rel[2]}${rel[4] || ''}`;
        return;
      }

      // Root-relative links to post sources: /posts/foo.md
      const rooted = url.match(/^\/posts\/([^/#?]+)\.(md|qmd|markdown)([#?].*)?$/i);
      if (rooted) {
        node.url = `/posts/${rooted[1]}${rooted[3] || ''}`;
        return;
      }

      // Root-relative links to rendered post pages: /posts/foo.html
      const rendered = url.match(/^\/posts\/([^/#?]+)\.html([#?].*)?$/i);
      if (rendered) {
        node.url = `/posts/${rendered[1]}${rendered[2] || ''}`;
        return;
      }

      // Root-relative post links with a trailing slash: /posts/foo/
      const slash = url.match(/^\/posts\/([^/#?]+)\/([#?].*)?$/);
      if (slash) {
        node.url = `/posts/${slash[1]}${slash[2] || ''}`;
      }
    });
  };
}

export default rewriteInternalLinks;
