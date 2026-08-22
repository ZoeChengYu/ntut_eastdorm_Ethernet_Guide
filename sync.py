import re
import urllib.parse
import markdown

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

def render_readme_html(md_content):
    # Convert markdown to html using markdown library
    html = markdown.markdown(md_content, extensions=['extra', 'tables', 'fenced_code'])
    
    # Custom post-processing to match GFM styles
    # Wrap tables with markdown-accessiblity-table
    html = re.sub(r'<table>', '<markdown-accessiblity-table><table role="table">', html)
    html = re.sub(r'</table>', '</table></markdown-accessiblity-table>', html)
    
    # URL encode local paths
    html = encode_local_links(html)
    return html

def parse_markdown_to_index_html(md_content):
    # First, convert Markdown to standard HTML
    html = markdown.markdown(md_content, extensions=['extra', 'tables', 'fenced_code'])
    
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
