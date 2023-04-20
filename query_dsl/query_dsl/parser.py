import json

from . import lexer
from .error import DslSyntaxError
from .keyword_mapping import LOOKUP, LookupException, EXCLUDE


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


class Query(object):
    def __init__(self, query_type, query_value):
        self.query_type = query_type
        self.query_value = query_value

    def __repr__(self):
        return "<%s '%s'>" % (self.query_type, self.query_value)


class Parser(object):
    def __init__(self, tokens):
        self.tokens = ListHelper(tokens)

    def check_grammar(self, class_expected, token):
        class_name = class_expected.__name__
        if self.tokens.is_empty():
            raise DslSyntaxError(
                f"Expected {class_name} after {token.value}, got nothing")
        if not isinstance(new_token := self.tokens.pop(), class_expected):
            raise DslSyntaxError(
                f"Expected {class_name} after {token.value}, got {new_token.value} instead")
        return new_token

    def parse(self):
        precedence = {
            lexer.Operator.Type.OR: 1,
            lexer.Operator.Type.SOR: 1,
            lexer.Operator.Type.AND: 2,
            lexer.Operator.Type.SAND: 2,
        }

        operator_stack = []
        output_queue = []

        while not self.tokens.is_empty():
            token = self.tokens.pop()

            if isinstance(token, lexer.Keyword):
                binder = self.check_grammar(lexer.Binder, token)
                identifier = self.check_grammar(lexer.Identifier, binder)
                output_queue.append(Query(token.value, identifier.value))
            elif isinstance(token, lexer.Operator):
                while operator_stack and \
                    isinstance(operator_stack[-1], lexer.Operator) and \
                    precedence[operator_stack[-1].get()] >= \
                    precedence[token.get()]:
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
                raise DslSyntaxError(
                    f"Expected Keyword, got {token.value} instead")
        while operator_stack:
            operator = operator_stack.pop()
            if operator.value == "(":
                raise DslSyntaxError("Missmatched parenthesis")
            output_queue.append(operator)

        return output_queue

    def enclose_json(self, operator_token, left_operand, right_operand):
        operation = None
        if operator_token.get() == lexer.Operator.Type.AND:
            operation = "must"
        elif operator_token.get() == lexer.Operator.Type.OR:
            operation = "should"

        return {
            "bool": {
                operation: [
                    left_operand,
                    right_operand
                ]
            }
        }

    def merge_json(self, operator_token, left_operand, right_operand):
        operation = None
        if operator_token.get() == lexer.Operator.Type.SAND:
            operation = "must"
        elif operator_token.get() == lexer.Operator.Type.SOR:
            operation = "should"

        if "nested" not in left_operand or "nested" not in right_operand:
            raise lexer.DslSyntaxError(f"{operator_token.value} can only be applied to operands of similar type")

        left_path = left_operand["nested"]["path"]
        right_path = right_operand["nested"]["path"]
        if left_path != right_path:
            raise lexer.DslSyntaxError(f"{left_path} is not same as {right_path}")

        left_query = left_operand["nested"]["query"]
        right_query = right_operand["nested"]["query"]

        query = left_operand
        query["nested"]["query"] = {
            "bool": {
                operation: [
                    left_query,
                    right_query
                ]
            }
        }

        return query

    def evaluate_postfix(self, tokens):
        operand_stack = []

        for token in tokens:
            if isinstance(token, Query):
                if token.query_type not in LOOKUP:
                    raise LookupException(
                        f"{token.query_type} not in lookup table")

                query_path = LOOKUP[token.query_type]

                query = {
                    "match": {
                        query_path: token.query_value
                    }
                }
                if token.query_type not in EXCLUDE:
                    query = {
                        "nested": {
                            "path": query_path.split(".")[0],
                            "query": query,
                            "inner_hits": {
                                # TODO bug here
                                # if (methodName:xx AND returnType:T1) OR (methodName:xx AND returnType:T2)
                                # query can be simplified as methodName:xx AND (returnType:T1 OR returnType:T2)
                                # which would not cause an error but user may not
                                "name": "=".join(
                                    [query_path, token.query_value]),
                                "highlight": {
                                    "fields": {
                                        query_path: {}
                                    }
                                }
                            }
                        }
                    }
                operand_stack.append(query)
            elif isinstance(token, lexer.Operator):
                if len(operand_stack) < 2:
                    raise DslSyntaxError(
                        f"Not enough operands provided for {token.value}")
                left_operand = operand_stack.pop()
                right_operand = operand_stack.pop()
                if token.get() in [lexer.Operator.Type.AND, lexer.Operator.Type.OR]:
                    result = self.enclose_json(token, left_operand, right_operand)
                elif token.get() in [lexer.Operator.Type.SAND, lexer.Operator.Type.SOR]:
                    result = self.merge_json(token, left_operand, right_operand)
                else:
                    raise DslSyntaxError(f"Unrecognized operator {token.value}")
                operand_stack.append(result)

        return operand_stack.pop()

    def get_elasticsearch_query(self, tokens, json_format=False):
        ast = self.evaluate_postfix(tokens)
        if json_format:
            return json.dumps(ast, indent=4)
        return ast
