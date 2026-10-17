from pathlib import Path

from block_markdown import markdown_to_html_node


def extract_title(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            if title:
                return title
    raise ValueError("Markdown must contain an h1 heading")


def generate_page(from_path, template_path, dest_path, basepath="/"):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    markdown = Path(from_path).read_text(encoding="utf-8")
    template = Path(template_path).read_text(encoding="utf-8")
    content = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)
    html = template.replace("{{ Title }}", title).replace("{{ Content }}", content)
    html = html.replace('href="/', f'href="{basepath}')
    html = html.replace('src="/', f'src="{basepath}')

    destination = Path(dest_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding="utf-8")


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath="/"):
    content_dir = Path(dir_path_content)
    destination_dir = Path(dest_dir_path)
    destination_dir.mkdir(parents=True, exist_ok=True)

    for entry in sorted(content_dir.iterdir()):
        if entry.is_dir():
            generate_pages_recursive(entry, template_path, destination_dir / entry.name, basepath)
        elif entry.is_file() and entry.suffix == ".md":
            generate_page(
                entry, template_path, destination_dir / entry.with_suffix(".html").name, basepath
            )
