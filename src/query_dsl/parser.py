import json

from . import lexer

class ParserError(Exception):
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
                self.tokens.pop()
                output_queue.append(Query(token.value, self.tokens.pop().value))
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
        while operator_stack:
            output_queue.append(operator_stack.pop())

        return output_queue


    def evaluate_postfix(self, tokens):
        operand_stack = []

        for token in tokens:
            if isinstance(token, Query):
                operand_stack.append({token.query_type:token.query_value})
            elif isinstance(token, lexer.Operator):
                left_operand = operand_stack.pop()
                right_operand = operand_stack.pop()
                if token.value == 'AND':
                    result = {'AND': [left_operand, right_operand]}
                elif token.value == 'OR':
                    result = {'OR': [left_operand, right_operand]}
                operand_stack.append(result)

        return operand_stack.pop()