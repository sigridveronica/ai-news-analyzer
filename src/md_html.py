import os
import re
import markdown
from image_search import search_unsplash_image  # Must return (image_url, image_credit)

def convert_md_folder_to_html(md_folder, html_output_folder):
    os.makedirs(html_output_folder, exist_ok=True)

    for filename in os.listdir(md_folder):
        if filename.endswith(".md"):
            md_path = os.path.join(md_folder, filename)
            title = filename.replace(".md", "")
            html_path = os.path.join(html_output_folder, filename.replace(".md", ".html"))

            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()
                md_content = re.sub(r'!\[.*?\]\(.*?\)', '', md_content)  # remove Markdown images

                html_body = markdown.markdown(md_content, extensions=["extra", "codehilite", "toc"])
                html_body = re.sub(r'<p>(\[\d+\](?:,\s*\[\d+\])*)</p>', r'\1', html_body)  # inline references

            image_url, image_credit = search_unsplash_image(title)

            # Extract metrics blockquote and convert to bullet list
            metrics_block = ""
            if "<blockquote>" in html_body:
                start = html_body.find("<blockquote>")
                end = html_body.find("</blockquote>") + len("</blockquote>")
                metrics_raw = html_body[start:end]
                html_body = html_body[:start] + html_body[end:]

                text = re.sub(r'<.*?>', '', metrics_raw).strip()
                lines = [f"<li>{line.strip()}</li>" for line in text.splitlines() if line.strip()]
                metrics_block = f"<ul>{''.join(lines)}</ul>"

            html_template = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>{title}</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        margin: 0;
                        background-color: #f8f9fa;
                        color: #212529;
                        line-height: 1.6;
                    }}
                    header {{
                        background-color: #ffffff;
                        text-align: center;
                        padding: 1em;
                        border-bottom: 2px solid #dee2e6;
                    }}
                    header img {{
                        width: 100%;
                        height: auto;
                        max-height: 50vh;
                        object-fit: cover;
                    }}
                    .credit {{
                        font-size: 0.85em;
                        color: #6c757d;
                        margin-top: 0.5em;
                    }}
                    .container {{
                        display: flex;
                        flex-direction: row;
                        max-width: 1200px;
                        margin: 2em auto;
                        padding: 0 1em;
                        gap: 2em;
                    }}
                    main {{
                        flex: 3;
                    }}
                    aside {{
                        flex: 1;
                        background-color: #ffffff;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 1em;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
                        height: fit-content;
                    }}
                    main img {{
                        max-width: 100%;
                        height: auto;
                        display: block;
                        margin: 1.5em auto;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                    }}
                    h1, h2, h3 {{
                        color: #0d6efd;
                    }}
                    a {{
                        color: #0d6efd;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    code {{
                        background: #e9ecef;
                        padding: 0.2em 0.4em;
                        border-radius: 4px;
                        font-family: monospace;
                    }}
                    pre {{
                        background: #e9ecef;
                        padding: 1em;
                        overflow-x: auto;
                        border-radius: 6px;
                    }}
                    blockquote {{
                        border-left: 4px solid #0d6efd;
                        padding-left: 1em;
                        color: #495057;
                        margin: 1em 0;
                        background: #f1f3f5;
                    }}
                </style>
            </head>
            <body>
                <header>
                    <img src="{image_url}" alt="{title} Banner">
                </header>
                <div class="container">
                    <main>
                        {html_body}
                    </main>
                    <aside>
                        <h3>🧠 Metrics</h3>
                        {metrics_block}
                    </aside>
                </div>
            </body>
            </html>
            """

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_template)

            print(f"✅ Converted: {md_path} -> {html_path}")

import os
import re
import markdown
from image_search import search_unsplash_image  # Must return (image_url, image_credit)

def convert_single_md_to_html(md_path, html_output_folder):
    os.makedirs(html_output_folder, exist_ok=True)

    filename = os.path.basename(md_path)
    title = filename.replace(".md", "")
    html_path = os.path.join(html_output_folder, filename.replace(".md", ".html"))

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
        md_content = re.sub(r'!\[.*?\]\(.*?\)', '', md_content)  # remove Markdown images

        html_body = markdown.markdown(md_content, extensions=["extra", "codehilite", "toc"])
        html_body = re.sub(r'<p>(\[\d+\](?:,\s*\[\d+\])*)</p>', r'\1', html_body)  # inline refs

    image_url, image_credit = search_unsplash_image(title)

    metrics_block = ""
    if "<blockquote>" in html_body:
        start = html_body.find("<blockquote>")
        end = html_body.find("</blockquote>") + len("</blockquote>")
        metrics_raw = html_body[start:end]
        html_body = html_body[:start] + html_body[end:]

        text = re.sub(r'<.*?>', '', metrics_raw).strip()
        lines = [f"<li>{line.strip()}</li>" for line in text.splitlines() if line.strip()]
        metrics_block = f"<ul>{''.join(lines)}</ul>"

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                background-color: #f8f9fa;
                color: #212529;
                line-height: 1.6;
            }}
            header {{
                background-color: #ffffff;
                text-align: center;
                padding: 1em;
                border-bottom: 2px solid #dee2e6;
            }}
            header img {{
                width: 100%;
                height: auto;
                max-height: 50vh;
                object-fit: cover;
            }}
            .credit {{
                font-size: 0.85em;
                color: #6c757d;
                margin-top: 0.5em;
            }}
            .container {{
                display: flex;
                flex-direction: row;
                max-width: 1200px;
                margin: 2em auto;
                padding: 0 1em;
                gap: 2em;
            }}
            main {{
                flex: 3;
            }}
            aside {{
                flex: 1;
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 1em;
                box-shadow: 0 2px 6px rgba(0,0,0,0.05);
                height: fit-content;
            }}
            main img {{
                max-width: 100%;
                height: auto;
                display: block;
                margin: 1.5em auto;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            }}
            h1, h2, h3 {{
                color: #0d6efd;
            }}
            a {{
                color: #0d6efd;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            code {{
                background: #e9ecef;
                padding: 0.2em 0.4em;
                border-radius: 4px;
                font-family: monospace;
            }}
            pre {{
                background: #e9ecef;
                padding: 1em;
                overflow-x: auto;
                border-radius: 6px;
            }}
            blockquote {{
                border-left: 4px solid #0d6efd;
                padding-left: 1em;
                color: #495057;
                margin: 1em 0;
                background: #f1f3f5;
            }}
        </style>
    </head>
    <body>
        <header>
            <img src="{image_url}" alt="{title} Banner">
        </header>
        <div class="container">
            <main>
                {html_body}
            </main>
            <aside>
                <h3>🧠 Metrics</h3>
                {metrics_block}
            </aside>
        </div>
    </body>
    </html>
    """

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_template)

    print(f"✅ Converted: {md_path} -> {html_path}")

###FOR TESTING ONLY

if __name__ == "__main__":
    md_path = "/Users/sigridveronica/Desktop/Investing/data/nuclear_energy_2025-06-03.md"
    md_folder = "/Users/sigridveronica/Desktop/Investing/data"
    html_output_folder = "/Users/sigridveronica/Desktop/Investing/html"
    convert_md_folder_to_html(md_folder, html_output_folder)
