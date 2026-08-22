import re
import urllib.parse
import markdown
from pymdownx import superfences as _sf  # noqa: F401 — ensure pymdownx is available

def encode_local_links(html):
    # Find all href and src attributes pointing to local paths containing Chinese characters and url-encode them
    def replace_url(match):
        attr = match.group(1)
        url = match.group(2)
        if not url.startswith(('http://', 'https://', 'mailto:', '#')):
            # URL encode the path, but preserve slashes and dots
            decoded = urllib.parse.unquote(url)
            # Encode each component of the path
            parts = decoded.split('/')
            encoded_parts = [urllib.parse.quote(p) if p not in ('.', '..') else p for p in parts]
            url = '/'.join(encoded_parts)
        return f'{attr}="{url}"'
    
    html = re.sub(r'(href|src)="([^"]+)"', replace_url, html)
    return html

MARKDOWN_EXTENSIONS = [
    'extra',
    'tables',
    'pymdownx.superfences',  # supports fenced code blocks inside list items
    'pymdownx.highlight',    # syntax-aware highlighting
]
MARKDOWN_EXTENSION_CONFIGS = {
    'pymdownx.highlight': {'use_pygments': False},  # keep plain <code> output
}


def fix_split_ordered_lists(html):
    """
    Python markdown splits ordered lists with fenced code blocks into multiple
    <ol> elements each starting at 1. This function restores correct numbering
    by splitting on headings AND section-label paragraphs (e.g. <p><strong>OS Name:</strong></p>),
    then adding start="N" only to consecutive <ol> blocks within a true sequence.
    """
    # A "section reset" paragraph is a <p> containing only a <strong> label ending with : or ：
    SECTION_LABEL = re.compile(
        r'<p>\s*(?:<br\s*/?>\s*)?<strong>[^<]+[：:]\s*</strong>\s*</p>',
        re.IGNORECASE
    )

    def fix_section(html_chunk):
        """Within a chunk, number consecutive <ol> blocks correctly, resetting at section labels."""
        # Tokenise by <ol> and </ol> boundaries and section-label paragraphs
        tokens = re.split(r'(<ol>|<ol\s[^>]*>|</ol>)', html_chunk)
        result = []
        counter = 0
        for tok in tokens:
            if tok == '<ol>':
                # Check if the *previous non-whitespace token* was a section-label paragraph
                # which means we should reset the counter
                prev_text = ''.join(result[-5:])  # look back a few tokens
                if SECTION_LABEL.search(prev_text):
                    counter = 1  # reset: this is item 1 of a new group
                else:
                    counter += 1
                if counter > 1:
                    result.append('<ol start="' + str(counter) + '">')
                else:
                    result.append('<ol>')
            else:
                result.append(tok)
        return ''.join(result)

    # Split on headings so each section between headings is handled independently
    parts = re.split(r'(<h[2345][^>]*>.*?</h[2345]>)', html, flags=re.DOTALL)
    fixed_parts = []
    for part in parts:
        if part.startswith('<h'):
            fixed_parts.append(part)
        else:
            fixed_parts.append(fix_section(part))
    return ''.join(fixed_parts)


def render_readme_html(md_content):
    # Convert markdown to html using markdown library
    html = markdown.markdown(
        md_content,
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs=MARKDOWN_EXTENSION_CONFIGS,
    )
    
    # Custom post-processing to match GFM styles
    # Wrap tables with markdown-accessiblity-table
    html = re.sub(r'<table>', '<markdown-accessiblity-table><table role="table">', html)
    html = re.sub(r'</table>', '</table></markdown-accessiblity-table>', html)
    
    # Fix: pull <pre> out of <p> wrappers (Python markdown limitation with fenced code in lists)
    html = re.sub(r'<p>\s*(<pre\b[^>]*>.*?</pre>)\s*', r'\1\n<p>', html, flags=re.DOTALL)
    html = re.sub(r'<p>\s*</p>', '', html)
    # Fix: break orphaned list-item numbers (e.g. 'text.\n2. <strong>') into separate <p>
    html = re.sub(r'(?<=</code>)\n(\d+\.\s+<strong>)', r'</p>\n<p>\1', html)
    html = re.sub(r'([^>])\n(\d+\.\s+<strong>)', r'\1</p>\n<p>\2', html)
    # Fix: restore correct numbering to split <ol> blocks
    html = fix_split_ordered_lists(html)

    # URL encode local paths
    html = encode_local_links(html)
    return html

def parse_markdown_to_index_html(md_content):
    # First, convert Markdown to standard HTML
    html = markdown.markdown(
        md_content,
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs=MARKDOWN_EXTENSION_CONFIGS,
    )
    
    # 1. URL encode local paths
    html = encode_local_links(html)
    
    # 2. Process blockquotes into alert boxes
    # Match blockquotes: <blockquote>...</blockquote>
    def replace_blockquote(match):
        bq_content = match.group(1)
        # Check if there is an alert tag
        alert_match = re.search(r'\[\!(NOTE|TIP|IMPORTANT|WARNING|CAUTION|HINT)\]', bq_content, re.IGNORECASE)
        if alert_match:
            alert_type = alert_match.group(1).lower()
            # Remove the [!TAG] string
            cleaned_content = re.sub(r'\[\!(NOTE|TIP|IMPORTANT|WARNING|CAUTION|HINT)\]\s*', '', bq_content, flags=re.IGNORECASE)
            # Remove leading/trailing breaks
            cleaned_content = re.sub(r'^<br\s*/?>\s*', '', cleaned_content.strip(), flags=re.IGNORECASE)
            
            title_icons = {
                "note": ("ℹ️ NOTE", "alert-note"),
                "tip": ("💡 TIP", "alert-tip"),
                "hint": ("💡 HINT", "alert-tip"),
                "important": ("🔔 IMPORTANT", "alert-important"),
                "warning": ("⚠️ WARNING", "alert-warning"),
                "caution": ("🔥 CAUTION", "alert-caution")
            }
            title_text, css_class = title_icons.get(alert_type, ("NOTE", "alert-note"))
            
            # E.g. wrap alert content with standard styling if it contains multiple items
            return f'<div class="alert {css_class}" style="margin-top:1rem;">\n    <div class="alert-title">{title_text}</div>\n    {cleaned_content.strip()}\n  </div>'
        return match.group(0)
        
    html = re.sub(r'<blockquote>(.*?)</blockquote>', replace_blockquote, html, flags=re.DOTALL)
    
    # 3. Post-process elements for index.html
    # Wrap tables in table-wrap
    html = re.sub(r'<table>', '<div class="table-wrap">\n  <table>', html)
    html = re.sub(r'</table>', '</table>\n</div>', html)
    
    # Add target="_blank" to external links
    def replace_links(match):
        attrs = match.group(1)
        if 'target=' not in attrs:
            return f'<a {attrs} target="_blank" rel="noopener">'
        return match.group(0)
    html = re.sub(r'<a ([^>]+)>', replace_links, html)

    # Fix: Python markdown sometimes wraps <pre> inside <p> when fenced code
    # blocks follow list item continuations. Pull <pre> out of <p> tags.
    html = re.sub(r'<p>\s*(<pre\b[^>]*>.*?</pre>)\s*', r'\1\n<p>', html, flags=re.DOTALL)
    # Remove any empty <p></p> results
    html = re.sub(r'<p>\s*</p>', '', html)
    # Break orphaned list-item numbers into separate <p>
    html = re.sub(r'([^>])\n(\d+\.\s+<strong>)', r'\1</p>\n<p>\2', html)
    # Fix: restore correct numbering to split <ol> blocks
    html = fix_split_ordered_lists(html)

    # Now, let's split the HTML by block elements to wrap steps
    # We can parse the document and extract chapters, steps, etc.
    # To do this cleanly, let's split the HTML by headings.
    heading_regex = r'(<h[2345][^>]*>.*?</h[2345]>)'
    parts = re.split(heading_regex, html, flags=re.DOTALL)
    
    output = []
    in_step = False
    step_num = 0
    step_title = ""
    step_content_parts = []
    
    for part in parts:
        part_strip = part.strip()
        if not part_strip:
            continue
            
        # Check if heading
        is_heading = part_strip.startswith('<h')
        if is_heading:
            # If we were in a step, close it
            if in_step:
                output.append(render_step_from_html(step_num, step_title, step_content_parts))
                in_step = False
                step_content_parts = []
                
            # Parse the heading
            h2_match = re.match(r'<h2[^>]*>(第[零壹貳參肆]章)\s*(.*?)</h2>', part_strip)
            h3_match = re.match(r'<h3[^>]*>(.*?)</h3>', part_strip)
            h4_step_match = re.match(r'<h4[^>]*>步驟\s*(\d+)\s*：\s*(.*?)</h4>', part_strip)
            h4_plain_match = re.match(r'<h4[^>]*>(.*?)</h4>', part_strip)
            h5_match = re.match(r'<h5[^>]*>(.*?)</h5>', part_strip)
            
            if h2_match:
                chap_num = h2_match.group(1)
                chap_title = h2_match.group(2).strip()
                chap_ids = {
                    "第零章": "ch0",
                    "第壹章": "ch1",
                    "第貳章": "ch2",
                    "第參章": "ch3",
                    "第肆章": "ch4"
                }
                chap_id = chap_ids.get(chap_num, "ch")
                output.append(f'\n  <!-- ── {chap_num} ── -->')
                output.append(f'  <h2 id="{chap_id}">{chap_num}　{chap_title}</h2>')
            elif h3_match:
                title = h3_match.group(1).strip()
                output.append(f'\n  <h3>{title}</h3>')
            elif h4_step_match:
                in_step = True
                step_num = int(h4_step_match.group(1))
                step_title = h4_step_match.group(2).strip()
                step_content_parts = []
            elif h4_plain_match:
                title = h4_plain_match.group(1).strip()
                if "Linux" in title:
                    output.append(f'\n  <h4>🐧 {title}</h4>')
                elif "macOS" in title:
                    output.append(f'\n  <h4> {title}</h4>')
                else:
                    output.append(f'\n  <h4>{title}</h4>')
            elif h5_match:
                if in_step:
                    step_content_parts.append(part_strip)
                else:
                    output.append(part_strip)
        else:
            # Content block
            if in_step:
                step_content_parts.append(part_strip)
            else:
                output.append(part_strip)
                
    if in_step:
        output.append(render_step_from_html(step_num, step_title, step_content_parts))
        
    return '\n'.join(output)

def render_step_from_html(num, title, content_parts):
    content_html = '\n'.join(content_parts)
    
    # Wrap local image links inside steps with class="img-link"
    def add_img_link_class(match):
        attrs = match.group(1)
        if 'class=' not in attrs:
            return f'<a class="img-link" {attrs}>'
        return match.group(0)
    content_html = re.sub(r'<a ([^>]*href="[^"]+\.(png|jpg|jpeg)"[^>]*)>', add_img_link_class, content_html)
    
    # Also clean up p tag wrappers around image links
    content_html = re.sub(r'<p>\s*(<a class="img-link".*?</a>)\s*</p>', r'\1', content_html, flags=re.DOTALL)
    
    card = f'''  <div class="step">
    <div class="step-header"><div class="step-num">{num}</div><div class="step-title">{title}</div></div>'''
    if content_html.strip():
        # Indent contents for clean HTML formatting
        indented_content = '\n'.join('    ' + line for line in content_html.strip().split('\n'))
        card += f'\n{indented_content}'
    card += '\n  </div>'
    return card

def main():
    # 1. Read README.md
    with open(r"c:\Users\ChengYu\Desktop\ntut_eastdorm_Ethernet_Guide\README.md", "r", encoding="utf-8") as f:
        md_content = f.read()
        
    # 2. Sync README.html
    print("Syncing README.html...")
    with open(r"c:\Users\ChengYu\Desktop\ntut_eastdorm_Ethernet_Guide\README.html", "r", encoding="utf-8") as f:
        readme_html = f.read()
        
    new_rendered = render_readme_html(md_content)
    start_tag = '<article class="content-card markdown-body" id="rendered-content">'
    end_tag = '</article>'
    start_idx = readme_html.find(start_tag)
    end_idx = readme_html.find(end_tag, start_idx)
    if start_idx != -1 and end_idx != -1:
        readme_html = readme_html[:start_idx + len(start_tag)] + "\n" + new_rendered + "\n" + readme_html[end_idx:]
    else:
        print("Warning: rendered-content tags not found in README.html")
    
    js_start = 'const rawMarkdown = `'
    js_end = '`; // Escaped raw string'
    js_start_idx = readme_html.find(js_start)
    js_end_idx = readme_html.find(js_end, js_start_idx)
    if js_start_idx != -1 and js_end_idx != -1:
        escaped_md = md_content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
        readme_html = readme_html[:js_start_idx + len(js_start)] + escaped_md + readme_html[js_end_idx:]
    else:
        print("Warning: rawMarkdown variable not found in README.html")
    
    with open(r"c:\Users\ChengYu\Desktop\ntut_eastdorm_Ethernet_Guide\README.html", "w", encoding="utf-8") as f:
        f.write(readme_html)
        
    # 3. Sync index.html
    print("Syncing index.html...")
    with open(r"c:\Users\ChengYu\Desktop\ntut_eastdorm_Ethernet_Guide\index.html", "r", encoding="utf-8") as f:
        index_html = f.read()
        
    new_container_content = parse_markdown_to_index_html(md_content)
    
    c_start = '<!-- ── Main Content ── -->'
    c_end = '</div><!-- end .container -->'
    c_start_idx = index_html.find(c_start)
    c_end_idx = index_html.find(c_end, c_start_idx)
    if c_start_idx != -1 and c_end_idx != -1:
        div_container = '<div class="container">'
        div_idx = index_html.find(div_container, c_start_idx)
        if div_idx != -1 and div_idx < c_end_idx:
            index_html = index_html[:div_idx + len(div_container)] + "\n" + new_container_content + "\n" + index_html[c_end_idx:]
        else:
            print("Warning: container div not found in index.html")
    else:
        print("Warning: main content tags not found in index.html")
    
    with open(r"c:\Users\ChengYu\Desktop\ntut_eastdorm_Ethernet_Guide\index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
        
    print("Sync completed successfully!")

if __name__ == '__main__':
    main()
