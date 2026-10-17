import re

from textnode import TextNode, TextType


_IMAGE_PATTERN = r"!\[([^\[\]]*)\]\(([^()]*)\)"
_LINK_PATTERN = r"(?<!!)\[([^\[\]]*)\]\(([^()]*)\)"


def text_to_textnodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    return nodes


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    return re.findall(_IMAGE_PATTERN, text)


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    return re.findall(_LINK_PATTERN, text)


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    return _split_nodes_pattern(old_nodes, _IMAGE_PATTERN, TextType.IMAGE)


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    return _split_nodes_pattern(old_nodes, _LINK_PATTERN, TextType.LINK)


def _split_nodes_pattern(
    old_nodes: list[TextNode], pattern: str, text_type: TextType
) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        start = 0
        for match in re.finditer(pattern, node.text):
            if match.start() > start:
                new_nodes.append(TextNode(node.text[start:match.start()], TextType.TEXT))
            new_nodes.append(TextNode(match.group(1), text_type, match.group(2)))
            start = match.end()
        if start < len(node.text):
            new_nodes.append(TextNode(node.text[start:], TextType.TEXT))

    return new_nodes


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    if not delimiter:
        raise ValueError("Delimiter must not be empty")

    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        sections = node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise ValueError(
                f"Invalid Markdown: missing closing delimiter {delimiter!r}"
            )

        for index, section in enumerate(sections):
            if section:
                section_type = TextType.TEXT if index % 2 == 0 else text_type
                new_nodes.append(TextNode(section, section_type))

    return new_nodes
