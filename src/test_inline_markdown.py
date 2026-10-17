import unittest

from inline_markdown import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_delimiter_types(self):
        for delimiter, text_type in (
            ("**", TextType.BOLD),
            ("_", TextType.ITALIC),
            ("`", TextType.CODE),
        ):
            with self.subTest(delimiter=delimiter):
                node = TextNode(
                    f"Before {delimiter}formatted{delimiter} after", TextType.TEXT
                )
                self.assertEqual(
                    split_nodes_delimiter([node], delimiter, text_type),
                    [
                        TextNode("Before ", TextType.TEXT),
                        TextNode("formatted", text_type),
                        TextNode(" after", TextType.TEXT),
                    ],
                )

    def test_multiple_pairs(self):
        node = TextNode("a **bold** b **more bold** c", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "**", TextType.BOLD),
            [
                TextNode("a ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" b ", TextType.TEXT),
                TextNode("more bold", TextType.BOLD),
                TextNode(" c", TextType.TEXT),
            ],
        )

    def test_delimiters_at_boundaries(self):
        node = TextNode("**bold**", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "**", TextType.BOLD),
            [TextNode("bold", TextType.BOLD)],
        )

    def test_adjacent_pairs(self):
        node = TextNode("**first****second**", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "**", TextType.BOLD),
            [TextNode("first", TextType.BOLD), TextNode("second", TextType.BOLD)],
        )

    def test_no_delimiter(self):
        node = TextNode("Plain text", TextType.TEXT)
        self.assertEqual(
            split_nodes_delimiter([node], "**", TextType.BOLD), [node]
        )

    def test_non_text_nodes_are_preserved(self):
        nodes = [
            TextNode("**bold", TextType.BOLD),
            TextNode("_italic", TextType.ITALIC),
            TextNode("`code", TextType.CODE),
            TextNode("**link", TextType.LINK, "https://example.com"),
            TextNode("**image", TextType.IMAGE, "image.png"),
        ]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual(result, nodes)
        for original, preserved in zip(nodes, result):
            self.assertIs(original, preserved)

    def test_multiple_input_nodes(self):
        nodes = [
            TextNode("**first**", TextType.TEXT),
            TextNode("plain", TextType.TEXT),
            TextNode("**second**", TextType.TEXT),
        ]
        self.assertEqual(
            split_nodes_delimiter(nodes, "**", TextType.BOLD),
            [
                TextNode("first", TextType.BOLD),
                TextNode("plain", TextType.TEXT),
                TextNode("second", TextType.BOLD),
            ],
        )

    def test_repeated_passes(self):
        nodes = [TextNode("`**code**` **bold** _italic_", TextType.TEXT)]
        nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        self.assertEqual(
            nodes,
            [
                TextNode("**code**", TextType.CODE),
                TextNode(" ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
            ],
        )

    def test_missing_closing_delimiter(self):
        for delimiter, text_type in (
            ("**", TextType.BOLD),
            ("_", TextType.ITALIC),
            ("`", TextType.CODE),
        ):
            for text in (
                f"before {delimiter}unfinished",
                f"{delimiter}closed{delimiter} then {delimiter}unfinished",
            ):
                with self.subTest(delimiter=delimiter, text=text):
                    with self.assertRaisesRegex(ValueError, "missing closing delimiter"):
                        split_nodes_delimiter(
                            [TextNode(text, TextType.TEXT)], delimiter, text_type
                        )

    def test_delimiters_cannot_pair_across_nodes(self):
        nodes = [
            TextNode("**first", TextType.TEXT),
            TextNode("second**", TextType.TEXT),
        ]
        with self.assertRaises(ValueError):
            split_nodes_delimiter(nodes, "**", TextType.BOLD)

    def test_empty_inputs_and_sections(self):
        self.assertEqual(split_nodes_delimiter([], "**", TextType.BOLD), [])
        for text in ("", "****"):
            with self.subTest(text=text):
                self.assertEqual(
                    split_nodes_delimiter(
                        [TextNode(text, TextType.TEXT)], "**", TextType.BOLD
                    ),
                    [],
                )

    def test_empty_delimiter(self):
        with self.assertRaisesRegex(ValueError, "Delimiter must not be empty"):
            split_nodes_delimiter([TextNode("Text", TextType.TEXT)], "", TextType.BOLD)

    def test_input_is_not_modified(self):
        node = TextNode("Before **bold** after", TextType.TEXT)
        nodes = [node]
        split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual(nodes, [TextNode("Before **bold** after", TextType.TEXT)])
        self.assertIs(nodes[0], node)


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual(
            [("image", "https://i.imgur.com/zjjcJKZ.png")], matches
        )

    def test_multiple_images(self):
        text = (
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) "
            "and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )
        self.assertEqual(
            extract_markdown_images(text),
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
        )

    def test_ignores_links(self):
        text = "[link](https://example.com) ![image](image.png) [other](other.html)"
        self.assertEqual(extract_markdown_images(text), [("image", "image.png")])

    def test_empty_alt_text(self):
        self.assertEqual(extract_markdown_images("![](image.png)"), [("", "image.png")])

    def test_adjacent_and_repeated_images(self):
        self.assertEqual(
            extract_markdown_images("![a](a.png)![b](b.png)![a](a.png)"),
            [("a", "a.png"), ("b", "b.png"), ("a", "a.png")],
        )

    def test_no_images(self):
        for text in ("", "Plain text", "![missing](image.png", "![missing]image.png"):
            with self.subTest(text=text):
                self.assertEqual(extract_markdown_images(text), [])


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_multiple_links(self):
        text = (
            "This is text with a link [to boot dev](https://www.boot.dev) "
            "and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        self.assertEqual(
            extract_markdown_links(text),
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
        )

    def test_ignores_images(self):
        text = "![first](first.png) [link](page.html) ![second](second.png)"
        self.assertEqual(extract_markdown_links(text), [("link", "page.html")])

    def test_adjacent_and_repeated_links(self):
        self.assertEqual(
            extract_markdown_links("[a](a.html)[b](b.html)[a](a.html)"),
            [("a", "a.html"), ("b", "b.html"), ("a", "a.html")],
        )

    def test_url_with_query_and_fragment(self):
        url = "https://example.com/search?q=hello&sort=new#results"
        self.assertEqual(extract_markdown_links(f"[Search!]({url})"), [("Search!", url)])

    def test_empty_anchor_text(self):
        self.assertEqual(extract_markdown_links("[](page.html)"), [("", "page.html")])

    def test_no_links(self):
        for text in (
            "",
            "Plain text",
            "![image](image.png)",
            "[missing](page.html",
            "[missing]page.html",
        ):
            with self.subTest(text=text):
                self.assertEqual(extract_markdown_links(text), [])


class TestSplitImagesAndLinks(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) "
            "and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            split_nodes_image([node]),
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) "
            "and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        self.assertEqual(
            split_nodes_link([node]),
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
            ],
        )

    def test_boundaries_adjacent_and_repeated_matches(self):
        for splitter, prefix, text_type in (
            (split_nodes_image, "!", TextType.IMAGE),
            (split_nodes_link, "", TextType.LINK),
        ):
            with self.subTest(text_type=text_type):
                node = TextNode(
                    f"{prefix}[a](a){prefix}[b](b){prefix}[a](a)", TextType.TEXT
                )
                self.assertEqual(
                    splitter([node]),
                    [TextNode("a", text_type, "a"), TextNode("b", text_type, "b"),
                     TextNode("a", text_type, "a")],
                )

    def test_no_matches_and_malformed_syntax(self):
        for splitter in (split_nodes_image, split_nodes_link):
            for text in ("Plain text", "[broken](url", "![broken]url"):
                with self.subTest(splitter=splitter.__name__, text=text):
                    self.assertEqual(splitter([TextNode(text, TextType.TEXT)]),
                                     [TextNode(text, TextType.TEXT)])

    def test_empty_inputs(self):
        for splitter in (split_nodes_image, split_nodes_link):
            with self.subTest(splitter=splitter.__name__):
                self.assertEqual(splitter([]), [])
                self.assertEqual(splitter([TextNode("", TextType.TEXT)]), [])

    def test_empty_labels_and_urls(self):
        for splitter, prefix, text_type in (
            (split_nodes_image, "!", TextType.IMAGE),
            (split_nodes_link, "", TextType.LINK),
        ):
            with self.subTest(text_type=text_type):
                self.assertEqual(
                    splitter([TextNode(f"{prefix}[](url) {prefix}[label]()", TextType.TEXT)]),
                    [TextNode("", text_type, "url"), TextNode(" ", TextType.TEXT),
                     TextNode("label", text_type, "")],
                )

    def test_non_text_nodes_are_preserved(self):
        nodes = [
            TextNode("![image](url) [link](url)", text_type, "original-url")
            for text_type in (TextType.BOLD, TextType.ITALIC, TextType.CODE,
                              TextType.IMAGE, TextType.LINK)
        ]
        for splitter in (split_nodes_image, split_nodes_link):
            with self.subTest(splitter=splitter.__name__):
                result = splitter(nodes)
                self.assertEqual(result, nodes)
                for original, preserved in zip(nodes, result):
                    self.assertIs(original, preserved)

    def test_mixed_links_and_images(self):
        # Identical labels and URLs ensure a link cannot be confused with an image.
        node = TextNode("![same](url) [same](url)", TextType.TEXT)
        self.assertEqual(
            split_nodes_link([node]),
            [TextNode("![same](url) ", TextType.TEXT), TextNode("same", TextType.LINK, "url")],
        )
        self.assertEqual(
            split_nodes_image([node]),
            [TextNode("same", TextType.IMAGE, "url"), TextNode(" [same](url)", TextType.TEXT)],
        )
        expected = [TextNode("same", TextType.IMAGE, "url"), TextNode(" ", TextType.TEXT),
                    TextNode("same", TextType.LINK, "url")]
        self.assertEqual(split_nodes_link(split_nodes_image([node])), expected)
        self.assertEqual(split_nodes_image(split_nodes_link([node])), expected)

    def test_multiple_nodes_and_input_unchanged(self):
        for splitter, prefix, text_type in (
            (split_nodes_image, "!", TextType.IMAGE),
            (split_nodes_link, "", TextType.LINK),
        ):
            with self.subTest(text_type=text_type):
                nodes = [TextNode(f"{prefix}[first](one) tail", TextType.TEXT),
                         TextNode(f"head {prefix}[second](two)", TextType.TEXT)]
                originals = [TextNode(node.text, node.text_type) for node in nodes]
                self.assertEqual(
                    splitter(nodes),
                    [TextNode("first", text_type, "one"), TextNode(" tail", TextType.TEXT),
                     TextNode("head ", TextType.TEXT), TextNode("second", text_type, "two")],
                )
                self.assertEqual(nodes, originals)


class TestTextToTextNodes(unittest.TestCase):
    def test_all_inline_types(self):
        text = (
            "This is **text** with an _italic_ word and a `code block` "
            "and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) "
            "and a [link](https://boot.dev)"
        )
        self.assertEqual(
            text_to_textnodes(text),
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
        )

    def test_plain_text(self):
        self.assertEqual(
            text_to_textnodes("Plain text, with punctuation!"),
            [TextNode("Plain text, with punctuation!", TextType.TEXT)],
        )

    def test_empty_text(self):
        self.assertEqual(text_to_textnodes(""), [])

    def test_whitespace_is_preserved(self):
        self.assertEqual(
            text_to_textnodes("  **bold**\n"),
            [TextNode("  ", TextType.TEXT), TextNode("bold", TextType.BOLD),
             TextNode("\n", TextType.TEXT)],
        )

    def test_each_type_without_surrounding_text(self):
        for text, expected in (
            ("**bold**", TextNode("bold", TextType.BOLD)),
            ("_italic_", TextNode("italic", TextType.ITALIC)),
            ("`code`", TextNode("code", TextType.CODE)),
            ("![alt](image.png)", TextNode("alt", TextType.IMAGE, "image.png")),
            ("[link](page.html)", TextNode("link", TextType.LINK, "page.html")),
        ):
            with self.subTest(text=text):
                self.assertEqual(text_to_textnodes(text), [expected])

    def test_adjacent_and_repeated_formatting(self):
        self.assertEqual(
            text_to_textnodes("**one**_two_`three`**four**"),
            [TextNode("one", TextType.BOLD), TextNode("two", TextType.ITALIC),
             TextNode("three", TextType.CODE), TextNode("four", TextType.BOLD)],
        )

    def test_code_contents_remain_literal(self):
        text = "**bold** _italic_ ![image](image.png) [link](page.html)"
        self.assertEqual(text_to_textnodes(f"`{text}`"), [TextNode(text, TextType.CODE)])

    def test_underscores_in_urls(self):
        self.assertEqual(
            text_to_textnodes("![alt](some_image.png) [link](some_page.html)"),
            [TextNode("alt", TextType.IMAGE, "some_image.png"),
             TextNode(" ", TextType.TEXT), TextNode("link", TextType.LINK, "some_page.html")],
        )

    def test_empty_image_alt_text(self):
        self.assertEqual(
            text_to_textnodes("![](image.png)"),
            [TextNode("", TextType.IMAGE, "image.png")],
        )

    def test_unclosed_delimiters(self):
        for text in ("**unfinished", "_unfinished", "`unfinished"):
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, "missing closing delimiter"):
                    text_to_textnodes(text)


if __name__ == "__main__":
    unittest.main()
