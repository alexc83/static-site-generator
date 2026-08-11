import unittest

from textnode import TextNode, TextType


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

if __name__ == "__main__":
    unittest.main()
        