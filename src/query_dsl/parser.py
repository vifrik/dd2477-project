import json

from . import lexer
from .keyword_mapping import LOOKUP, LookupException

class SyntaxError(Exception):
    pass


class EmptyListExpection(Exception):
    pass


class ListHelper(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def is_empty(self):
        return self.current >= len(self.tokens)

    def check_size(self):
        if self.is_empty():
            raise EmptyListExpection()

    def peek(self):
        self.check_size()
        return self.tokens[self.current]

    def pop(self):
        self.check_size()
        self.current += 1
        return self.tokens[self.current - 1]

class Query(object):
    def __init__(self, query_type, query_value):
        self.query_type = query_type
        self.query_value = query_value

    def __repr__(self):
        return "<%s '%s'>" % (self.query_type, self.query_value)


class Parser(object):
    def __init__(self, tokens):
        self.tokens = ListHelper(tokens)

    def parse(self):
        precedence = {'OR': 1, 'AND': 2}

        operator_stack = []
        output_queue = []

        while not self.tokens.is_empty():
            token = self.tokens.pop()

            if isinstance(token, lexer.Keyword):
                if not isinstance(binder := self.tokens.pop(), lexer.Binder):
                    raise SyntaxError(f"Missing Binder after {token.value}, got {binder.value} instead")
                if not isinstance(identifier := self.tokens.pop(), lexer.Identifier):
                    raise SyntaxError(f"Missing Identifier after {token.value}, got {identifier.value} instead")
                output_queue.append(Query(token.value, identifier.value))
            elif isinstance(token, lexer.Operator):
                while operator_stack and isinstance(operator_stack[-1], lexer.Operator) and precedence[operator_stack[-1].value] >= precedence[token.value]:
                    output_queue.append(operator_stack.pop())
                operator_stack.append(token)
            elif isinstance(token, lexer.Separator):
                if token.value == '(':
                    operator_stack.append(token)
                elif token.value == ')':
                    while operator_stack and operator_stack[-1].value != '(':
                        output_queue.append(operator_stack.pop())
                    if operator_stack and operator_stack[-1].value == '(':
                        operator_stack.pop()
                    else:
                        raise SyntaxError("Missmatched parenthesis")
            else:
                raise SyntaxError(f"Expected Keyword, got {token.value} instead")
        while operator_stack:
            operator = operator_stack.pop()
            if operator.value == '(':
                raise SyntaxError("Missmatched parenthesis")
            output_queue.append(operator)

        return output_queue

    def enclose_json(self, operator, left_operand, right_operand):
        operation = None
        if operator == "AND":
            operation = "must"
        elif operator == "OR":
            operation = "should"

        return {
            "bool": {
                operation: [
                    {
                        "match": left_operand,
                    },
                    {
                        "match": right_operand
                    }
                ]
            }
        }


    def evaluate_postfix(self, tokens):
        operand_stack = []

        for token in tokens:
            if isinstance(token, Query):
                if token.query_type not in LOOKUP:
                    raise LookupException(f"{token.query_type} not in lookup table")
                operand_stack.append({LOOKUP[token.query_type]: token.query_value})
            elif isinstance(token, lexer.Operator):
                left_operand = operand_stack.pop()
                right_operand = operand_stack.pop()
                if token.value == "AND" or token.value == "OR":
                    result = self.enclose_json(token.value, left_operand, right_operand)
                else:
                    raise SyntaxError(f"Unrecognized operator {token.value}")
                operand_stack.append(result)

        return operand_stack.pop()

    def get_elasticsearch_query(self, tokens, json_format=False):
        ast = self.evaluate_postfix(tokens)
        if "bool" not in ast:
            query = {
                "match": ast
            }
        else:
            query = {
                "bool": {
                    "must": self.evaluate_postfix(tokens)
                }
            }
        if json_format:
            return json.dumps(query, indent=4)
        return query
