import unittest

from . import lexer


class TestTokenizer(unittest.TestCase):
    def test_tokenize(self):
        query = """returnType:int 
            AND (
            functionName:hello OR 
        functionName:hallo )
        """
        tokens = lexer.tokenize(query)
        correct = [
            ('Keyword', 'returnType'),
            ('Binder', ':'),
            ('Identifier', 'int'),
            ('Operator', 'AND'),
            ('Separator', '('),
            ('Keyword', 'functionName'),
            ('Binder', ':'),
            ('Identifier', 'hello'),
            ('Operator', 'OR'),
            ('Keyword', 'functionName'),
            ('Binder', ':'),
            ('Identifier', 'hallo'),
            ('Separator', ')')
        ]
        for token, (class_name, value) in zip(tokens, correct):
            self.assertTrue(token.__class__.__name__ == class_name,
                            msg=f"{token.__class__.__name__} != {class_name}")
            self.assertTrue(token.value == value,
                            msg=f"{token.value} != {value}")