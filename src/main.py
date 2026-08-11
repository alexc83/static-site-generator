from htmlnode import HTMLNode
from textnode import TextNode, TextType


if __name__ == "__main__":
    node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(node)

    html_node = HTMLNode("p", "This is a paragraph", 
                         props={"class": "main-text", "id": "p-id"})
    print(html_node)
    print("props:")
    print(html_node.props_to_html())

    heading_node = HTMLNode("h1", "This is a main heading")
    print(heading_node.props_to_html())