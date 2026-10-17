import unittest

from block_markdown import (
    BlockType,
    block_to_block_type,
    markdown_to_blocks,
    markdown_to_html_node,
    text_to_children,
)
from parentnode import ParentNode


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        self.assertEqual(
            markdown_to_blocks(md),
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\n"
                "This is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_heading_paragraph_and_list(self):
        md = "# Heading\n\nA **bold** paragraph.\n\n- First\n- Second"
        self.assertEqual(
            markdown_to_blocks(md),
            ["# Heading", "A **bold** paragraph.", "- First\n- Second"],
        )

    def test_single_block(self):
        self.assertEqual(markdown_to_blocks("One paragraph"), ["One paragraph"])

    def test_single_newlines_stay_in_block(self):
        self.assertEqual(
            markdown_to_blocks("First line\nSecond line\nThird line"),
            ["First line\nSecond line\nThird line"],
        )

    def test_trims_each_block(self):
        self.assertEqual(
            markdown_to_blocks(" \t First block \t\n\n  Second block \t "),
            ["First block", "Second block"],
        )

    def test_excessive_newlines(self):
        self.assertEqual(
            markdown_to_blocks("\n\n\nFirst\n\n\n\n\nSecond\n\n\n"),
            ["First", "Second"],
        )

    def test_empty_and_whitespace_only_input(self):
        for md in ("", " \t ", "\n", "\n\n\n\n", " \n\n\t\n\n "):
            with self.subTest(markdown=md):
                self.assertEqual(markdown_to_blocks(md), [])

    def test_whitespace_only_blocks_are_removed(self):
        self.assertEqual(
            markdown_to_blocks("First\n\n \t \n\nSecond"),
            ["First", "Second"],
        )

    def test_internal_spacing_and_indentation_are_preserved(self):
        self.assertEqual(
            markdown_to_blocks("  First  line\n    indented line  \n\nNext"),
            ["First  line\n    indented line", "Next"],
        )


class TestBlockToBlockType(unittest.TestCase):
    def test_paragraphs(self):
        for block in ("", "Plain text", "First line\nSecond line", "Some **bold** text"):
            with self.subTest(block=block):
                self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_heading_levels(self):
        for level in range(1, 7):
            with self.subTest(level=level):
                self.assertEqual(
                    block_to_block_type("#" * level + " Heading"), BlockType.HEADING
                )

    def test_invalid_headings(self):
        for block in ("####### Heading", "#No space", "##\tTab", "#", "Text # Heading"):
            with self.subTest(block=block):
                self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_code_blocks(self):
        for block in (
            "```\nprint('hello')\n```",
            "```\nfirst\nsecond\n```",
            "```\n```",
            "```\n# heading\n> quote\n- item\n```",
        ):
            with self.subTest(block=block):
                self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_invalid_code_blocks(self):
        for block in (
            "`inline code`",
            "```inline```",
            "```python\nprint('hello')\n```",
            "```\nmissing closing fence",
            "missing opening fence\n```",
            "```\ncode\n```\ntrailing text",
        ):
            with self.subTest(block=block):
                self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_quotes(self):
        for block in ("> quote", ">quote", "> first\n>second\n> third", ">first\n>\n>last"):
            with self.subTest(block=block):
                self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_requires_every_line(self):
        for block in ("> quote\nunquoted", "unquoted\n> quote", "> quote\n\n> quote"):
            with self.subTest(block=block):
                self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_unordered_lists(self):
        for block in ("- item", "- first\n- second\n- third"):
            with self.subTest(block=block):
                self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_invalid_unordered_lists(self):
        for block in (
            "-missing space", "* item", "- first\nsecond", "first\n- second",
            "- first\n-\tsecond", "- first\n\n- second",
        ):
            with self.subTest(block=block):
                self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_lists(self):
        self.assertEqual(block_to_block_type("1. item"), BlockType.ORDERED_LIST)
        block = "\n".join(f"{index}. Item {index}" for index in range(1, 13))
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_invalid_ordered_lists(self):
        for block in (
            "0. item", "2. item", "1.item", "1) item", "1.\titem",
            "1. first\n3. skipped", "1. first\n1. repeated",
            "1. first\n2. second\n2. repeated", "1. first\nsecond",
            "1. first\n- second", "1. first\n\n2. second",
        ):
            with self.subTest(block=block):
                self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p>"
            "<p>This is another paragraph with <i>italic</i> text and "
            "<code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><pre><code>This is text that _should_ remain\n"
            "the **same** even with inline stuff\n</code></pre></div>",
        )

    def test_all_heading_levels(self):
        for level in range(1, 7):
            with self.subTest(level=level):
                self.assertEqual(
                    markdown_to_html_node("#" * level + " A **heading**").to_html(),
                    f"<div><h{level}>A <b>heading</b></h{level}></div>",
                )

    def test_quote_with_inline_formatting(self):
        self.assertEqual(
            markdown_to_html_node("> First **bold** line\n>second _italic_ line").to_html(),
            "<div><blockquote>First <b>bold</b> line second <i>italic</i> line</blockquote></div>",
        )

    def test_unordered_list(self):
        self.assertEqual(
            markdown_to_html_node("- **First** item\n- _Second_ item\n- `third`").to_html(),
            "<div><ul><li><b>First</b> item</li><li><i>Second</i> item</li>"
            "<li><code>third</code></li></ul></div>",
        )

    def test_ordered_list(self):
        self.assertEqual(
            markdown_to_html_node("1. **First** item\n2. Second item").to_html(),
            "<div><ol><li><b>First</b> item</li><li>Second item</li></ol></div>",
        )

    def test_ordered_list_with_double_digit_items(self):
        md = "\n".join(f"{index}. Item {index}" for index in range(1, 12))
        items_html = "".join(f"<li>Item {index}</li>" for index in range(1, 12))
        self.assertEqual(markdown_to_html_node(md).to_html(), f"<div><ol>{items_html}</ol></div>")

    def test_links_and_images(self):
        self.assertEqual(
            markdown_to_html_node("[Link](https://example.com) ![Alt](image.png)").to_html(),
            '<div><p><a href="https://example.com">Link</a> '
            '<img src="image.png" alt="Alt"></img></p></div>',
        )

    def test_code_does_not_parse_inline_markdown(self):
        content = "**unfinished _italic [link](url) ![image](image.png) `code`\n"
        self.assertEqual(
            markdown_to_html_node(f"```\n{content}```").to_html(),
            f"<div><pre><code>{content}</code></pre></div>",
        )

    def test_empty_document_and_code(self):
        for md in ("", "\n\n \n\n"):
            with self.subTest(markdown=md):
                self.assertEqual(markdown_to_html_node(md).to_html(), "<div></div>")
        self.assertEqual(
            markdown_to_html_node("```\n```").to_html(),
            "<div><pre><code></code></pre></div>",
        )

    def test_full_document(self):
        md = "# Title\n\nParagraph.\n\n> Quote\n\n- Item\n\n1. Step\n\n```\ncode\n```"
        node = markdown_to_html_node(md)
        self.assertIsInstance(node, ParentNode)
        self.assertEqual(node.tag, "div")
        self.assertEqual(len(node.children), 6)
        self.assertEqual(
            node.to_html(),
            "<div><h1>Title</h1><p>Paragraph.</p><blockquote>Quote</blockquote>"
            "<ul><li>Item</li></ul><ol><li>Step</li></ol>"
            "<pre><code>code\n</code></pre></div>",
        )

    def test_invalid_list_markers_render_as_paragraph(self):
        self.assertEqual(
            markdown_to_html_node("1. First\n3. Skipped").to_html(),
            "<div><p>1. First 3. Skipped</p></div>",
        )

    def test_text_to_children(self):
        children = text_to_children("Plain **bold** and _italic_")
        self.assertEqual(
            [child.to_html() for child in children],
            ["Plain ", "<b>bold</b>", " and ", "<i>italic</i>"],
        )


if __name__ == "__main__":
    unittest.main()
