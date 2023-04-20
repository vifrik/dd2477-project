from .error import DslSyntaxError


class LexerError(Exception):
    pass


class Token(object):
    VALUES = None
    DESCRIPTION = None

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "%s '%s'" % (self.__class__.__name__, self.value)

    def __str__(self):
        return repr(self)


class Keyword(Token):
    LEADER = None
    PATH = None
    FIELDS = None


class MetadataKeyword(Keyword):
    LEADER = "metadata"
    FIELDS = {
        "name": "metadata.name",
        "repo": "metadata.repo",
        "import": "metadata.imports",
        "package": "metadata.package"
    }


class MethodKeyword(Keyword):
    LEADER = "method"
    PATH = "methods"
    FIELDS = {
        "name": "methods.name",
        "modifier": "methods.modifiers",
        "returnType": "methods.return_type",
        "annotation": "methods.annotations",
        "parameterName": "methods.parameters.name",
        "parameterType": "methods.parameters.type",
    }


class ClassKeyword(Keyword):
    LEADER = "class"
    PATH = "classes"
    FIELDS = {
        "name": "classes.name",
        "modifier": "classes.modifiers",
        "annotation": "classes.annotations",
        "extend": "classes.extends",
    }


class VariableKeyword(Keyword):
    LEADER = "variable"
    PATH = "variables"
    FIELDS = {
        "name": "variables.name",
        "type": "variables.type",
    }


class FieldKeyword(Keyword):
    LEADER = "field"
    PATH = "fields"
    FIELDS = {
        "name": "fields.name",
        "type": "fields.type",
    }

class Attribute(Token):
    pass


class Binder(Token):
    VALUES = {
        ":",
        ",",
        "|"
    }
    DESCRIPTION = "placeholder"


class Operator(Token):
    MAX_LEN = 3
    VALUES = {
        "AND",
        "OR"
    }


class Separator(Token):
    VALUES = {
        "(", ")",
        "[", "]"
    }


class Identifier(Token):
    pass


attributes = {attr for attr in [
    *MetadataKeyword.FIELDS.keys(),
    *MethodKeyword.FIELDS.keys(),
    *ClassKeyword.FIELDS.keys(),
    *VariableKeyword.FIELDS.keys(),
    *FieldKeyword.FIELDS.keys()
]}


def generate_documentation():
    token_classes = [Keyword, Binder, Operator, Separator]

    for token_class in token_classes:
        print(f"Token type: {token_class.__name__}:")
        print(f"\tpossible {token_class.__name__.lower()}s:")
        if token_class.VALUES is not None:
            for value in token_class.VALUES:
                print(f"\t\t'{value}'")

        if token_class.DESCRIPTION is not None:
            print(f"\tdescription:")
            print(f"\t\t{token_class.DESCRIPTION}")
        print("\n")


class Lexer(object):
    def __init__(self, data):
        self.cur_pos = 0
        self.end_pos = 0

        if data is None:
            raise DslSyntaxError("Expected data, got NoneType")
        
        if data == "":
            raise DslSyntaxError("Expected data, got empty string")

        self.data = data
        self.length = len(data)

        self.cur_line = 1
        self.cur_col = -1

    def read_identifier(self):

        self.end_pos = self.cur_pos + 1

        while self.end_pos < len(self.data):
            if self.data[self.end_pos].isalnum() or self.data[self.end_pos] in ['.', '-', '_', '/']:
                self.end_pos += 1
            else:
                break

        ident = self.data[self.cur_pos:self.end_pos]
        if ident in attributes:
            token_type = Attribute
        elif ident in MetadataKeyword.LEADER:
            token_type = MetadataKeyword
        elif ident in MethodKeyword.LEADER:
            token_type = MethodKeyword
        elif ident in ClassKeyword.LEADER:
            token_type = ClassKeyword
        elif ident in VariableKeyword.LEADER:
            token_type = VariableKeyword
        elif ident in FieldKeyword.LEADER:
            token_type = FieldKeyword
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
