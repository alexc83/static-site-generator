class HTMLNode:

    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError("Method not implemented yet")

    def props_to_html(self):
        final_str_representation = ""
        if self.props == None:
            return final_str_representation
        for key, value in self.props.items():
            final_str_representation += f" {key}=\"{value}\""
        return final_str_representation

    def __repr__(self):
        reprentative_str = (
            "HTMLNode(\n"
            f"Tag: {self.tag}\n"
            f"Value: {self.value}\n"
            f"Children: {self.children}\n"
            f"Props: {self.props}\n"
            ")\n"
        )
        return reprentative_str