import unittest

from htmlnode import HTMLNode
from leafnode import LeafNode


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_b(self):
        self.assertEqual(LeafNode("b", "Bold text").to_html(), "<b>Bold text</b>")

    def test_leaf_to_html_a_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(
            node.to_html(), '<a href="https://www.google.com">Click me!</a>'
        )

    def test_leaf_to_html_multiple_props(self):
        node = LeafNode("span", "Text", {"class": "highlight", "id": "note"})
        self.assertEqual(
            node.to_html(), '<span class="highlight" id="note">Text</span>'
        )

    def test_leaf_to_html_raw_text(self):
        node = LeafNode(None, "Raw text", {"class": "ignored"})
        self.assertEqual(node.to_html(), "Raw text")

    def test_leaf_to_html_missing_value(self):
        for tag in ("p", None):
            with self.subTest(tag=tag):
                with self.assertRaises(ValueError):
                    LeafNode(tag, None).to_html()

    def test_leaf_to_html_empty_value(self):
        self.assertEqual(LeafNode("p", "").to_html(), "<p></p>")
        self.assertEqual(LeafNode(None, "").to_html(), "")

    def test_constructor(self):
        node = LeafNode("p", "Text")
        self.assertIsInstance(node, HTMLNode)
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)

    def test_constructor_requires_tag_and_value(self):
        with self.assertRaises(TypeError):
            LeafNode()
        with self.assertRaises(TypeError):
            LeafNode("p")

    def test_constructor_rejects_children(self):
        with self.assertRaises(TypeError):
            LeafNode("p", "Text", children=[])

    def test_repr(self):
        node = LeafNode("p", "Text", {"class": "main-text"})
        self.assertEqual(
            repr(node),
            "LeafNode(\n"
            "Tag: p\n"
            "Value: Text\n"
            "Props: {'class': 'main-text'}\n"
            ")\n",
        )


if __name__ == "__main__":
    unittest.main()
