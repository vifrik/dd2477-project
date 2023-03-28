import javalang
import argparse
from pprint import pprint
import json


def read(filename):
    with open(filename, 'r') as f:
        return f.read()


# https://stackoverflow.com/questions/8230315/how-to-json-serialize-sets
def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)

def extract_variable_declarator(obj):
    assert isinstance(obj, javalang.tree.VariableDeclarator), "error"


def extract_function_parameters(param_list):
    parameter_data = list()

    for node in param_list:
        if isinstance(node, javalang.tree.FormalParameter):
            parameter_entry = dict()
            parameter_entry['name'] = node.name
            parameter_entry['type'] = node.type.name
            parameter_data.append(parameter_entry)
    return parameter_data


def extract_functions(tree):
    function_data = list()

    for path, node in tree.filter(javalang.tree.MethodDeclaration):
        function_entry = dict()
        function_entry['name'] = node.name
        function_entry['modifiers'] = node.modifiers
        function_entry['parameters'] = extract_function_parameters(node.parameters)
        function_entry['return_type'] = node.return_type.name if node.return_type is not None else None
        function_data.append(function_entry)

    return function_data


def extract_classes(tree):
    class_data = list()

    for path, node in tree.filter(javalang.tree.ClassDeclaration):
        class_entry = dict()
        class_entry['name'] = node.name
        class_data.append(class_entry)

    return class_data


def extract_metadata(tree, filepath, url):
    assert isinstance(tree, javalang.tree.CompilationUnit), "error"

    metadata = dict()
    metadata['filepath'] = filepath
    metadata['url'] = url
    metadata['imports'] = tree.imports
    metadata['package'] = tree.package

    return metadata



def main():
    Parser = argparse.ArgumentParser()
    Parser.add_argument("-i", "--input", required=True, help="input file")
    Parser.add_argument("-d", "--debug", help="debug mode", action='store_true')
    args = Parser.parse_args()

    contents = read(args.input)
    tree = javalang.parse.parse(contents)

    output = dict()
    output['document'] = dict()
    output['document']['metadata'] = extract_metadata(tree, args.input, None)
    output['document']['classes'] = extract_classes(tree)
    output['document']['functions'] = extract_functions(tree)

    json_object = json.dumps(output, indent=2, default=serialize_sets)

    args.debug and print(json_object)


if __name__ == '__main__':
    main()
