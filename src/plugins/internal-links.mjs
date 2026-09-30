import { visit } from 'unist-util-visit';

// Rewrites relative internal Markdown links such as ./foo.md (or foo.md) to the
// canonical /posts/foo.html route, mirroring how the Quarto site resolved them.
// Keeps anchors and query strings. Leaves absolute, external and fragment links
// untouched.
function rewriteInternalLinks() {
  return (tree) => {
    visit(tree, 'link', (node) => {
      if (typeof node.url !== 'string') return;
      const url = node.url;
      if (/^(https?:|mailto:|tel:|#|\/|\.\.\/)/.test(url)) return;
      const m = url.match(/^(\.\/)?([^#?]+?)\.(md|qmd|markdown)([#?].*)?$/i);
      if (!m) return;
      node.url = `/posts/${m[2]}.html${m[4] || ''}`;
    });
  };
}

export default rewriteInternalLinks;
