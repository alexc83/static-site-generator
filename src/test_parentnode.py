import unittest

from htmlnode import HTMLNode
from leafnode import LeafNode
from parentnode import ParentNode


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_multiple_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

    def test_to_html_with_nested_siblings_and_props(self):
        node = ParentNode(
            "div",
            [
                ParentNode("p", [LeafNode(None, "First")], {"id": "intro"}),
                ParentNode("p", [LeafNode("b", "Second")]),
            ],
            {"class": "content", "id": "main"},
        )
        self.assertEqual(
            node.to_html(),
            '<div class="content" id="main">'
            '<p id="intro">First</p><p><b>Second</b></p></div>',
        )

    def test_to_html_with_empty_children(self):
        self.assertEqual(ParentNode("div", []).to_html(), "<div></div>")

    def test_to_html_with_missing_tag(self):
        for tag in (None, ""):
            with self.subTest(tag=tag):
                with self.assertRaisesRegex(ValueError, "must have a tag"):
                    ParentNode(tag, []).to_html()

    def test_to_html_with_missing_children(self):
        with self.assertRaisesRegex(ValueError, "must have children"):
            ParentNode("div", None).to_html()

    def test_to_html_with_invalid_nested_node(self):
        node = ParentNode("div", [ParentNode("span", None)])
        with self.assertRaisesRegex(ValueError, "must have children"):
            node.to_html()

    def test_to_html_with_invalid_leaf(self):
        node = ParentNode("div", [LeafNode("span", None)])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_constructor(self):
        children = [LeafNode(None, "Text")]
        props = {"class": "content"}
        node = ParentNode("div", children, props)
        self.assertIsInstance(node, HTMLNode)
        self.assertEqual(node.tag, "div")
        self.assertIs(node.children, children)
        self.assertIs(node.props, props)
        self.assertIsNone(node.value)

    def test_constructor_requires_tag_and_children(self):
        with self.assertRaises(TypeError):
            ParentNode()
        with self.assertRaises(TypeError):
            ParentNode("div")

    def test_constructor_rejects_value(self):
        with self.assertRaises(TypeError):
            ParentNode("div", [], value="Text")


if __name__ == "__main__":
    unittest.main()
