import unittest

from htmlnode import HTMLNode



class TestTexNode(unittest.TestCase):
   

    def test_repr(self):
            html_node = HTMLNode("p", "This is a paragraph", 
                                     props={"class": "main-text", "id": "p-id"})
            str_repr = ("HTMLNode(\n"
            "Tag: p\n"
            "Value: This is a paragraph\n"
            "Children: None\n"
            "Props: {'class': 'main-text', 'id': 'p-id'}\n"
            ")\n")
            self.assertEqual(html_node.__repr__(), str_repr)

    def test_props_to_html(self):
                html_node = HTMLNode("p", "This is a paragraph", 
                                         props={"class": "main-text", "id": "p-id"})
                str_props = " class=\"main-text\" id=\"p-id\""
                self.assertEqual(html_node.props_to_html(), str_props)

    def test_props_to_html_empty_props(self):
                    html_node = HTMLNode("p", "This is a paragraph")
                    str_props = ""
                    self.assertEqual(html_node.props_to_html(), str_props)

if __name__ == "__main__":
    unittest.main()
        