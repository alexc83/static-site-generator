from enum import Enum

from htmlnode import HTMLNode
from inline_markdown import text_to_textnodes
from parentnode import ParentNode
from textnode import TextNode, TextType, text_node_to_html_node


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def block_to_block_type(block: str) -> BlockType:
    for level in range(1, 7):
        if block.startswith("#" * level + " ") and len(block) > level + 1:
            return BlockType.HEADING

    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE

    lines = block.split("\n")
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST
    if all(line.startswith(f"{index}. ") for index, line in enumerate(lines, 1)):
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH


def markdown_to_blocks(markdown: str) -> list[str]:
    blocks = []
    for section in markdown.split("\n\n"):
        block = section.strip()
        if block:
            blocks.append(block)
    return blocks


def text_to_children(text: str) -> list[HTMLNode]:
    return [text_node_to_html_node(node) for node in text_to_textnodes(text)]


def markdown_to_html_node(markdown: str) -> ParentNode:
    children = [_block_to_html_node(block) for block in markdown_to_blocks(markdown)]
    return ParentNode("div", children)


def _block_to_html_node(block: str) -> ParentNode:
    match block_to_block_type(block):
        case BlockType.HEADING:
            marker, text = block.split(" ", 1)
            return ParentNode(f"h{len(marker)}", text_to_children(text))
        case BlockType.CODE:
            text_node = TextNode(block[4:-3], TextType.TEXT)
            code = ParentNode("code", [text_node_to_html_node(text_node)])
            return ParentNode("pre", [code])
        case BlockType.QUOTE:
            text = " ".join(line[1:].strip() for line in block.split("\n"))
            return ParentNode("blockquote", text_to_children(text))
        case BlockType.UNORDERED_LIST:
            items = [line[2:] for line in block.split("\n")]
            return _list_to_html_node("ul", items)
        case BlockType.ORDERED_LIST:
            items = [line.split(". ", 1)[1] for line in block.split("\n")]
            return _list_to_html_node("ol", items)
        case _:
            text = " ".join(block.split("\n"))
            return ParentNode("p", text_to_children(text))


def _list_to_html_node(tag: str, items: list[str]) -> ParentNode:
    return ParentNode(tag, [ParentNode("li", text_to_children(item)) for item in items])
