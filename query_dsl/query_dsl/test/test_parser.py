import unittest

from .. import lexer
from .. import parser
from .. import error


class TestParser(unittest.TestCase):
    def test_missing_binder(self):
        query = "import"
        tokens = list(lexer.tokenize(query))
        p = parser.Parser(tokens)
        self.assertRaises(error.DslSyntaxError, p.parse)

    def test_missing_identifier(self):
        query = "className:"
        tokens = list(lexer.tokenize(query))
        p = parser.Parser(tokens)
        self.assertRaises(error.DslSyntaxError, p.parse)

    def test_missing_parenthesis_left(self):
        query = "(methodName:somename AND returnType:int"
        tokens = list(lexer.tokenize(query))
        p = parser.Parser(tokens)
        self.assertRaises(error.DslSyntaxError, p.parse)

    def test_missing_parenthesis_right(self):
        query = "methodName:somename AND returnType:int)"
        tokens = list(lexer.tokenize(query))
        p = parser.Parser(tokens)
        self.assertRaises(error.DslSyntaxError, p.parse)

    def test_missing_operand_right(self):
        query = "methodName:somename AND"
        tokens = list(lexer.tokenize(query))
        p = parser.Parser(tokens)
        operand_stack = p.parse()
        self.assertRaises(error.DslSyntaxError, p.evaluate_postfix, operand_stack)

    def test_missing_operand_left(self):
        query = "AND returnType:int"
        tokens = list(lexer.tokenize(query))
        p = parser.Parser(tokens)
        operand_stack = p.parse()
        self.assertRaises(error.DslSyntaxError, p.evaluate_postfix, operand_stack)