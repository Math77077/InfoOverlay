#!/usr/bin/env python3
"""
Documentation Compilation Service.
Responsible for normalizing Markdown content and rendering a production-ready PDF layout.
"""

import os
import sys
import markdown
from xhtml2pdf import pisa

INPUT_FILE = os.path.abspath('USER_MANUAL.md')
OUTPUT_FILE = os.path.abspath('dist/Manual_do_Usuario.pdf')

UNICODE_REPLACEMENTS = {
    '📂': '[Pasta]',
    '📄': '[Arq]',
    '⚙️': '[Exec]',
    '⚠️': 'ATENÇÃO:',
    '🚫': 'AVISO:',
    '├──': '|--',
    '└──': '|__',
    '──': '--',
    '│': '|',
    '├': '|',
    '└': '|',
    '─': '-'
}

HTML_TEMPLATE = '''<html>
<head>
<style>
    @page {
        size: a4;
        margin: 2.5cm;
    }
    body { 
        font-family: Helvetica, Arial, sans-serif; 
        color: #333; 
        line-height: 1.5; 
        font-size: 10pt;
    } 
    h1 { color: #056e9b; border-bottom: 1px solid #056e9b; padding-bottom: 5px; font-size: 20pt; } 
    h2 { color: #1f2833; margin-top: 20px; font-size: 14pt; page-break-after: avoid; } 
    h3 { color: #459cd6; font-size: 12pt; page-break-after: avoid; } 
    
    pre, table, blockquote {
        page-break-inside: avoid;
    }
    
    code { 
        background: #f4f4f4; 
        font-family: Courier, monospace; 
        font-size: 9pt;
    } 
    pre {
        background: #f4f4f4;
        border: 1px solid #ddd;
        padding: 10px;
        font-family: Courier, monospace;
        font-size: 9pt;
        margin-bottom: 15px;
    }
    table { 
        border-collapse: collapse; 
        width: 100%; 
        margin-top: 15px; 
        margin-bottom: 15px;
    } 
    th, td { 
        border: 1px solid #ccb3b3; 
        padding: 8px; 
        text-align: left; 
        font-size: 9pt;
    } 
    th { 
        background-color: #f8f9fa; 
        color: #056e9b; 
    } 
    blockquote { 
        margin: 15px 0; 
        padding: 10px; 
        background-color: #fff3cd; 
        border-left: 4px solid #ffc107; 
        color: #856404; 
    }
</style>
</head>
<body>[]</body>
</html>'''

def normalize_markdown(raw_content: str) -> str:
    """Replaces complex Unicode characters and emojis with clean printable ASCII."""
    normalized = raw_content
    for unicode_char, ascii_text in UNICODE_REPLACEMENTS.items():
        normalized = normalized.replace(unicode_char, ascii_text)
    return normalized

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file '{INPUT_FILE}' not found.", file=sys.stderr)
        sys.exit(1)
        
    # Get the target directory safely
    target_dir = os.path.dirname(OUTPUT_FILE)
    if target_dir: # Only create if there's a valid directory string
        os.makedirs(target_dir, exist_ok=True)

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        md_content = f.read()

    clean_md = normalize_markdown(md_content)
    md_html = markdown.markdown(clean_md, extensions=['extra'])
    
    # FIXED: Clean injection targeted to structural token
    html_content = HTML_TEMPLATE.replace('[]', md_html)
    
    print("Compiling markdown to production PDF layout...")
    with open(OUTPUT_FILE, 'wb') as f_out:
        pisa_status = pisa.CreatePDF(html_content, dest=f_out)
        
    if pisa_status.err:
        print(f"Compilation failed with xhtml2pdf errors: {pisa_status.err}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Success: Production document exported cleanly to {OUTPUT_FILE}")

if __name__ == '__main__':
    main()