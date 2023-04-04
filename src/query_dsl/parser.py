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


class Parser(object):
    def __init__(self, tokens):
        self.tokens = ListHelper(list(tokens))

    def parse(self):
        precedence = {'OR': 1, 'AND': 2}

        operator_stack = []
        operand_stack = []

        # Iterate over the tokens
        while not self.tokens.is_empty():
            token = self.tokens.pop()
            token_type = token.__class__.__name__
            token_value = token.value

            if token_type == 'Keyword':
                sub_list = []
                sub_list.append(token_value)
                self.tokens.pop()
                sub_list.append(self.tokens.pop().value)
                operand_stack.append(sub_list)
            elif token_type == 'Operator':
                while operator_stack and operator_stack[-1] != '(' and \
                    precedence[operator_stack[-1]] >= precedence[token_value]:
                    op = operator_stack.pop()
                    right = operand_stack.pop()
                    left = operand_stack.pop()
                    operand_stack.append(f'({op} {left} {right})')
                # Push the new operator onto the stack
                operator_stack.append(token_value)
            elif token_type == 'Separator' and token_value == '(':
                operator_stack.append(token_value)
            elif token_type == 'Separator' and token_value == ')':
                while operator_stack and operator_stack[-1] != '(':
                    op = operator_stack.pop()
                    right = operand_stack.pop()
                    left = operand_stack.pop()
                    operand_stack.append(f'({left} {op} {right})')
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()
                else:
                    raise ValueError('Mismatched parentheses')
            else:
                # Raise an error for unknown token types
                raise ValueError(f'Unknown token type: {token_type}')

        while operator_stack:
            op = operator_stack.pop()
            if op == '(':
                raise ValueError('Mismatched parentheses')
            right = operand_stack.pop()
            left = operand_stack.pop()
            operand_stack.append(f'({op} {left} {right})')

        # The final expression is on the top of the operand stack
        final_expression = operand_stack[-1]
        print(final_expression)