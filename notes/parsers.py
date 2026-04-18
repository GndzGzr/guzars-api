import re
import mistune
from django.utils.text import slugify

WIKILINK_PATTERN = r'\[\[([\s\S]+?)\]\]'
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


def plugin_wikilinks(md):
    """
    A Mistune plugin to parse [[Wikilinks]] commonly used in Obsidian.
    """
    # register the parser
    # regex pattern must be compiled or a string in latest mistune versions
    md.inline.register('wikilink', WIKILINK_PATTERN, parse_wikilink, before='link')
    
    # register the HTML renderer
    if md.renderer and md.renderer.__class__.__name__ == 'HTMLRenderer':
        md.renderer.register('wikilink', render_html_wikilink)


def render_markdown_to_html(raw_markdown: str) -> str:
    """
    Takes pure markdown (without frontmatter) and compiles it to HTML,
    replacing Obsidian wikilinks with standard <a> tags.
    """
    markdown = mistune.create_markdown(
        plugins=[
            'strikethrough',
            'footnotes',
            'table',
            plugin_wikilinks
        ]
    )
    return markdown(raw_markdown)


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
