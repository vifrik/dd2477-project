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
            ('Operator', ':'),
            ('Identifier', 'int'),
            ('Operator', 'AND'),
            ('Separator', '('),
            ('Keyword', 'functionName'),
            ('Operator', ':'),
            ('Identifier', 'hello'),
            ('Operator', 'OR'),
            ('Keyword', 'functionName'),
            ('Operator', ':'),
            ('Identifier', 'hallo'),
            ('Separator', ')')
        ]
        for token, (class_name, value) in zip(tokens, correct):
            self.assertTrue(token.__class__.__name__ == class_name)
            self.assertTrue(token.value == value)