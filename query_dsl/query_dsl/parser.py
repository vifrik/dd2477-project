from abc import ABC, abstractmethod, abstractproperty
import json
import random
import string

from . import lexer
from .error import DslSyntaxError


class EmptyListException(Exception):
    pass


class ListHelper(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def is_empty(self):
        return self.current >= len(self.tokens)

    def check_size(self):
        if self.is_empty():
            raise EmptyListException()

    def peek(self):
        self.check_size()
        return self.tokens[self.current]

    def pop(self):
        self.check_size()
        self.current += 1
        return self.tokens[self.current - 1]


class Query(ABC):
    TOKEN_CLASS = None

    def get_fields(self):
        return [attr for attr in dir(self) if not attr.startswith("_") and not callable(getattr(self, attr))]

    def get_fields_dict(self):
        return {
            field: getattr(self, field) for field in self.get_fields()
        }

    def get_fields_size(self):
        return len(self.get_fields())

    def _query_helper_match(self, field, value):
        if len(value) == 1:
            return {
                "match": {
                    self.TOKEN_CLASS.FIELDS[field]: value[0]
                }
            }

        return {
            "bool": {
                "should": [
                    {
                        "match": {
                            self.TOKEN_CLASS.FIELDS[field]: val
                        }
                    } for val in value
                ]
            }
        }

    def _query_helper_bool(self):
        inner_match = [self._query_helper_match(k, v) for k, v in self.get_fields_dict().items()]
        if len(inner_match) == 1:
            return inner_match[0]

        return {
            "bool": {
                "must": inner_match
            }
        }

    def _get_random_string(self, length):
        return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

    def get_query(self):
        return {
            "nested": {
                "path": self.TOKEN_CLASS.PATH,
                "query": self._query_helper_bool(),
                "inner_hits": {
                    "name": f"{self.TOKEN_CLASS.LEADER}-{self._get_random_string(10)}",
                    "highlight": {
                        "fields": {
                            self.TOKEN_CLASS.FIELDS[field]: {} for field in self.get_fields()
                        }
                    }
                }
            }
        }


class MetadataQuery(Query):
    TOKEN_CLASS = lexer.MetadataKeyword

    def get_query(self):
        return {
            "match": {
                self.TOKEN_CLASS.PATH: self._query_helper_bool()
            }
        }


class MethodQuery(Query):
    TOKEN_CLASS = lexer.MethodKeyword


class ClassQuery(Query):
    TOKEN_CLASS = lexer.ClassKeyword


class VariableQuery(Query):
    TOKEN_CLASS = lexer.VariableKeyword


class FieldQuery(Query):
    TOKEN_CLASS = lexer.FieldKeyword


class Parser(object):
    def __init__(self, tokens):
        self.tokens = ListHelper(tokens)

    def check_grammar(self, class_expected, token, expected=None):
        class_name = class_expected.__name__
        if self.tokens.is_empty():
            raise DslSyntaxError(f"Expected {class_name} after {token.value}, got nothing")
        if not isinstance(new_token := self.tokens.pop(), class_expected):
            raise DslSyntaxError(f"Expected {class_name} after {token.value}, got {new_token.value} instead")
        if expected is not None and new_token.value != expected:
            raise DslSyntaxError(f"Expected {class_name} after {token.value}, got {new_token.value} instead")
        return new_token

    def parse(self):
        precedence = {"OR": 1, "AND": 2}

        operator_stack = []
        output_queue = []

        while not self.tokens.is_empty():
            token = self.tokens.pop()

            if isinstance(token, lexer.Keyword):
                if isinstance(token, lexer.MetadataKeyword):
                    query = MetadataQuery()
                elif isinstance(token, lexer.MethodKeyword):
                    query = MethodQuery()
                elif isinstance(token, lexer.ClassKeyword):
                    query = ClassQuery()
                elif isinstance(token, lexer.VariableKeyword):
                    query = VariableQuery()
                elif isinstance(token, lexer.FieldKeyword):
                    query = FieldQuery()
                else:
                    raise DslSyntaxError("No bueno")

                self.check_grammar(lexer.Separator, token, "[")

                while not isinstance(self.tokens.peek(), lexer.Separator):
                    identifiers = list()
                    attr = self.check_grammar(lexer.Attribute, token)

                    if not attr.value in query.TOKEN_CLASS.FIELDS.keys():
                        raise DslSyntaxError(f"Unrecognized {attr.__class__} for {token.__class__}")

                    binder = self.check_grammar(lexer.Binder, attr)
                    identifier = self.check_grammar(lexer.Identifier, binder)
                    identifiers.append(identifier.value)

                    while self.tokens.peek().value == "|":
                        self.check_grammar(lexer.Binder, identifier)
                        identifier = self.check_grammar(lexer.Identifier, binder)
                        identifiers.append(identifier.value)

                    setattr(query, attr.value, identifiers)

                    next_token = self.tokens.peek()
                    if next_token.value == ",":
                        self.check_grammar(lexer.Binder, identifier)
                    elif not next_token.value == "]":
                        raise DslSyntaxError(f"Expected , or ], got {next_token.value}")

                self.check_grammar(lexer.Separator, token, "]")
                output_queue.append(query)

                if not self.tokens.is_empty() and not isinstance(self.tokens.peek(), lexer.Operator):
                    operator_stack.append(lexer.Operator("AND"))
            elif isinstance(token, lexer.Operator):
                while operator_stack and isinstance(operator_stack[-1], lexer.Operator) and precedence[operator_stack[-1].value] >= precedence[token.value]:
                    output_queue.append(operator_stack.pop())
                operator_stack.append(token)
            elif isinstance(token, lexer.Separator):
                if token.value == "(":
                    operator_stack.append(token)
                elif token.value == ")":
                    while operator_stack and operator_stack[-1].value != "(":
                        output_queue.append(operator_stack.pop())
                    if operator_stack and operator_stack[-1].value == "(":
                        operator_stack.pop()
                    else:
                        raise DslSyntaxError("Missmatched parenthesis")
            else:
                raise DslSyntaxError(f"Expected Keyword, got {token.value} instead")
        while operator_stack:
            operator = operator_stack.pop()
            if operator.value == "(":
                raise DslSyntaxError("Missmatched parenthesis")
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
                    left_operand,
                    right_operand
                ]
            }
        }

    def evaluate_postfix(self, tokens):
        operand_stack = []

        for token in tokens:
            if isinstance(token, Query):
                query = token.get_query()
                operand_stack.append(query)
            elif isinstance(token, lexer.Operator):
                if len(operand_stack) < 2:
                    raise DslSyntaxError(f"Not enough operands provided for {token.value}")
                left_operand = operand_stack.pop()
                right_operand = operand_stack.pop()
                if token.value == "AND" or token.value == "OR":
                    result = self.enclose_json(token.value, left_operand, right_operand)
                else:
                    raise DslSyntaxError(f"Unrecognized operator {token.value}")
                operand_stack.append(result)

        return operand_stack.pop()

    def get_elasticsearch_query(self, tokens, json_format=False):
        ast = self.evaluate_postfix(tokens)
        if json_format:
            return json.dumps(ast, indent=4)
        return ast
