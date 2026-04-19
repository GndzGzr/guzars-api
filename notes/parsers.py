import re
import mistune
from django.utils.text import slugify

WIKILINK_PATTERN = r'(?<!\!)\[\[([\s\S]+?)\]\]'
EMBED_PATTERN = r'!\[\[([\s\S]+?)\]\]'


def parse_wikilink(inline, m, state):
    text = m.group(0)
    inner = text[2:-2]
    
    # Check if there's an alias: [[Note Name|Alias]]
    if '|' in inner:
        target, alias = inner.split('|', 1)
    else:
        target = inner
        alias = inner

    # target can contain block hashes: [[Note Name#Heading]]
    target_note = target
    target_hash = ""
    if '#' in target:
        target_note, target_hash = target.split('#', 1)
        target_hash = "#" + slugify(target_hash)

    target_slug = slugify(target_note)
    
    state.append_token({
        'type': 'wikilink',
        'attrs': {'target_slug': target_slug, 'alias': alias, 'target_hash': target_hash}
    })
    return m.end()


def render_html_wikilink(renderer, target_slug, target_hash, alias):
    # This renders pure HTML anchor linking to the API representation.
    # e.g., <a href="/api/notes/my-note#heading">My Note</a>
    href = f"/api/notes/{target_slug}{target_hash}"
    return f'<a href="{href}" class="internal-link">{alias}</a>'


def parse_obsidian_embed(inline, m, state):
    text = m.group(0)
    inner = text[3:-2] # remove ![[ ]]
    
    if '|' in inner:
        target, alias = inner.split('|', 1)
    else:
        target = inner
        alias = ""
    
    state.append_token({
        'type': 'obsidian_embed',
        'attrs': {'target': target.strip(), 'alias': alias.strip()}
    })
    return m.end()


def render_html_obsidian_embed(renderer, target, alias):
    lower_target = target.lower()
    
    # Map to a centralized asset endpoint that the frontend or backend proxy will resolve
    # e.g., <img src="/api/assets/?file=dog.png" />
    import urllib.parse
    encoded_target = urllib.parse.quote(target)
    asset_url = f"/api/assets/?file={encoded_target}"

    IMG_EXTS = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp')
    
    if lower_target.endswith(IMG_EXTS):
        alt = alias if alias else target
        # sometimes obsidian uses |100 for width
        width_str = f'width="{alias}"' if alias and alias.isdigit() else ""
        return f'<img src="{asset_url}" alt="{alt}" class="obsidian-embed-image" {width_str} />'
    
    elif lower_target.endswith('.pdf'):
        # Determine specific visual height if alias provided
        height = alias if (alias and alias.isdigit()) else "600"
        return f'<iframe src="{asset_url}" class="obsidian-embed-pdf" width="100%" height="{height}px" style="border:none;"></iframe>'
    
    else:
        # It's embedding another Markdown Note block entirely
        # Render a placeholder or recursive blockquote (since we can't fetch the note contents directly here without breaking the stateless parser)
        target_note = target
        
        target_hash = ""
        if '#' in target:
            target_note, target_hash = target.split('#', 1)
            target_hash = "#" + slugify(target_hash)

        target_slug = slugify(target_note)
        href = f"/api/notes/{target_slug}{target_hash}"
        return f'<blockquote class="obsidian-embed-note"><a href="{href}" class="internal-link">Transcluded Note: {target}</a></blockquote>'


def plugin_obsidian_embeds(md):
    """
    A Mistune plugin to parse ![[Embeds]] commonly used in Obsidian for Images/PDFs/Notes.
    """
    md.inline.register('obsidian_embed', EMBED_PATTERN, parse_obsidian_embed, before='link')
    if md.renderer and hasattr(md.renderer, 'register'):
        md.renderer.register('obsidian_embed', render_html_obsidian_embed)


def plugin_wikilinks(md):
    """
    A Mistune plugin to parse [[Wikilinks]] commonly used in Obsidian.
    """
    md.inline.register('wikilink', WIKILINK_PATTERN, parse_wikilink, before='link')
    if md.renderer and hasattr(md.renderer, 'register'):
        md.renderer.register('wikilink', render_html_wikilink)


class ObsidianHTMLRenderer(mistune.HTMLRenderer):
    def image(self, alt, url, title=None):
        # Override the native markdown image `![alt](src)` to map our secure assets route 
        # so relative image paths work flawlessly in the frontend.
        import urllib.parse
        encoded_url = urllib.parse.quote(url)
        asset_url = f"/api/assets/?file={encoded_url}"
        
        html = f'<img src="{asset_url}" alt="{alt}"'
        if title:
            import html as html_lib
            safe_title = html_lib.escape(title)
            html += f' title="{safe_title}"'
        html += ' />'
        return html

def render_markdown_to_html(raw_markdown: str) -> str:
    """
    Takes pure markdown (without frontmatter) and compiles it to HTML,
    replacing Obsidian wikilinks with standard <a> tags.
    """
    renderer = ObsidianHTMLRenderer()
    markdown = mistune.create_markdown(
        renderer=renderer,
        plugins=[
            'strikethrough',
            'footnotes',
            'table',
            plugin_obsidian_embeds,
            plugin_wikilinks
        ]
    )
    return markdown(raw_markdown)


def extract_toc_from_content(raw_markdown: str):
    """
    Extracts a Table of Contents (TOC) as JSON array from Markdown headers.
    Matches `# Heading 1`, `## Heading 2`, etc.
    """
    toc = []
    # Regex to match Markdown headers line by line (# levels)
    pattern = re.compile(r'^(#{1,6})\s+(.*)', re.MULTILINE)
    
    for match in pattern.finditer(raw_markdown):
        level = len(match.group(1))
        text = match.group(2).strip()
        slug = slugify(text)
        
        toc.append({
            'level': level,
            'text': text,
            'slug': slug
        })
        
    return toc

def extract_links_from_content(raw_markdown: str):
    """
    Utility to extract all outgoing wikilinks from raw Markdown text.
    Returns a list of dictionaries with target note information natively without formatting it.
    """
    links = []
    # Find all [[Target|Alias]]
    for match in re.finditer(WIKILINK_PATTERN, raw_markdown):
        # We also want to capture a snippet of context for the graph
        # For simplicity, extract the sentence containing the match.
        snippet_start = max(0, match.start() - 50)
        snippet_end = min(len(raw_markdown), match.end() + 50)
        context_text = raw_markdown[snippet_start:snippet_end].replace('\n', ' ')

        inner = match.group(1)
        if '|' in inner:
            target, _ = inner.split('|', 1)
        else:
            target = inner
            
        target_note = target
        
        # Skip assets and documents that shouldn't be indexed as notes
        _lower = target_note.lower()
        if _lower.endswith(('.png', '.pdf', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.mp4', '.mp3')):
            continue

        target_hash = ""
        if '#' in target:
            target_note, target_hash = target.split('#', 1)
            target_hash = slugify(target_hash)

        links.append({
            'target_slug': slugify(target_note),
            'target_original': target_note,
            'target_block': target_hash,
            'context_text': f"...{context_text}..."
        })
    return links
