import unittest

from leafnode import LeafNode
from textnode import TextNode, TextType, text_node_to_html_node


class TestTexNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq_test(self):
            node = TextNode("This is a text node", TextType.BOLD)
            node2 = TextNode("This is a text node 2", TextType.BOLD)
            self.assertNotEqual(node, node2)

    def test_not_eq_text_type(self):
                node = TextNode("This is a text node", TextType.BOLD)
                node2 = TextNode("This is a text node 2", TextType.ITALIC)
                self.assertNotEqual(node, node2)

    def test_not_eq_url(self):
                    node = TextNode("This is a text node", TextType.BOLD)
                    node2 = TextNode("This is a text node 2", TextType.BOLD, "www.google.com")
                    self.assertNotEqual(node, node2)

    def test_repr(self):
            node = TextNode("This is a text node", TextType.BOLD)
            str_repr = "TextNode(This is a text node, bold, None)"
            self.assertEqual(node.__repr__(), str_repr)

class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertIsNone(html_node.tag)
        self.assertEqual(html_node.value, "This is a text node")
        self.assertIsNone(html_node.props)
        self.assertEqual(html_node.to_html(), "This is a text node")

    def test_formatted_text(self):
        for text_type, tag in (
            (TextType.BOLD, "b"),
            (TextType.ITALIC, "i"),
            (TextType.CODE, "code"),
        ):
            with self.subTest(text_type=text_type):
                html_node = text_node_to_html_node(TextNode("Text", text_type))
                self.assertIsInstance(html_node, LeafNode)
                self.assertEqual(html_node.tag, tag)
                self.assertEqual(html_node.value, "Text")
                self.assertIsNone(html_node.props)
                self.assertEqual(html_node.to_html(), f"<{tag}>Text</{tag}>")

    def test_link(self):
        node = TextNode("Click me!", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click me!")
        self.assertEqual(html_node.props, {"href": "https://example.com"})
        self.assertEqual(
            html_node.to_html(), '<a href="https://example.com">Click me!</a>'
        )

    def test_image(self):
        node = TextNode("An image", TextType.IMAGE, "https://example.com/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(
            html_node.props,
            {"src": "https://example.com/image.png", "alt": "An image"},
        )

    def test_empty_text(self):
        html_node = text_node_to_html_node(TextNode("", TextType.TEXT))
        self.assertEqual(html_node.to_html(), "")

    def test_plain_alias(self):
        html_node = text_node_to_html_node(TextNode("Text", TextType.PLAIN))
        self.assertIsNone(html_node.tag)
        self.assertEqual(html_node.value, "Text")

    def test_unsupported_type(self):
        for text_type in (None, "bold", "unknown"):
            with self.subTest(text_type=text_type):
                with self.assertRaisesRegex(ValueError, "Unsupported text type"):
                    text_node_to_html_node(TextNode("Text", text_type))


if __name__ == "__main__":
    unittest.main()
