import unittest

from .. import lexer
from .. import error


class TestTokenizer(unittest.TestCase):
    def test_tokenize(self):
        query = """returnType:int 
            AND (
            methodName:hello OR 
        methodName:hallo )
        """
        tokens = lexer.tokenize(query)
        correct = [
            ("Keyword", "returnType"),
            ("Binder", ":"),
            ("Identifier", "int"),
            ("Operator", "AND"),
            ("Separator", "("),
            ("Keyword", "methodName"),
            ("Binder", ":"),
            ("Identifier", "hello"),
            ("Operator", "OR"),
            ("Keyword", "methodName"),
            ("Binder", ":"),
            ("Identifier", "hallo"),
            ("Separator", ")")
        ]
        for token, (class_name, value) in zip(tokens, correct):
            self.assertTrue(token.__class__.__name__ == class_name,
                            msg=f"{token.__class__.__name__} != {class_name}")
            self.assertTrue(token.value == value,
                            msg=f"{token.value} != {value}")
