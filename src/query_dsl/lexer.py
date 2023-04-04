class LexerError(Exception):
    pass


class Token(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "%s '%s'" % (self.__class__.__name__, self.value)

    def __str__(self):
        return repr(self)


class Keyword(Token):
    VALUES = {
        "returnType",
        "functionDecorator",
        "functionName",
        "parameterType",
        "parameterValue",
        "parameterName",
        "variableType",
        "variableName",
        "fieldType",
        "fieldName",
        "import",
    }


class Binder(Token):
    VALUES = {
        ':'
    }


class Operator(Token):
    MAX_LEN = 3
    VALUES = {
        "AND",
        "OR"
    }


class Separator(Token):
    VALUES = {
        "(", ")"
    }


class Identifier(Token):
    pass


class Lexer(object):
    def __init__(self, data):
        self.cur_pos = 0
        self.end_pos = 0

        self.data = data
        self.length = len(data)

        self.cur_line = 1
        self.cur_col = -1

    def read_identifier(self):

        self.end_pos = self.cur_pos + 1

        while self.end_pos < len(self.data):
            if self.data[self.end_pos].isalnum():
                self.end_pos += 1
            else:
                break

        ident = self.data[self.cur_pos:self.end_pos]
        if ident in Keyword.VALUES:
            token_type = Keyword
        else:
            token_type = Identifier

        return token_type

    def is_operator(self):
        for length in range(1, min(self.length - self.cur_pos, Operator.MAX_LEN) + 1):
            end_index = self.cur_pos + length
            if self.data[self.cur_pos:end_index] in Operator.VALUES:
                self.end_pos = end_index
                return True
        return False

    def is_separator(self):
        if self.data[self.cur_pos] in Separator.VALUES:
            self.end_pos = self.cur_pos + 1
            return True
        return False

    def tokenize(self):
        while self.cur_pos < self.length:
            c = self.data[self.cur_pos]

            if c.isspace():
                self.cur_pos += 1
                continue
            elif c in Binder.VALUES:
                self.end_pos = self.cur_pos + 1
                token_type = Binder
            elif self.is_operator():
                token_type = Operator
            elif self.is_separator():
                token_type = Separator
            elif c.isalnum():
                token_type = self.read_identifier()
            else:
                continue

            token = token_type(self.data[self.cur_pos:self.end_pos])

            yield token

            self.cur_pos = self.end_pos


def tokenize(entry):
    lexer = Lexer(entry)
    return lexer.tokenize()
