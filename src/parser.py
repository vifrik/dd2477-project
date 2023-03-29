#!/usr/bin/env python

import javalang
import argparse
import json


def read(filename):
    with open(filename, 'r') as f:
        return f.read()


# https://stackoverflow.com/questions/8230315/how-to-json-serialize-sets
def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)


def extract_fields(tree):
    field_data = list()

    for path, node in tree.filter(javalang.tree.FieldDeclaration):
        field_entry = dict()
        field_entry['name'] = node.declarators[0].name
        field_entry['type'] = node.type.name if node.type is not None else None
        field_entry['modifiers'] = node.modifiers
        field_entry['position'] = node.position
        field_data.append(field_entry)

    return field_data


def extract_variables(tree):
    variable_data = list()

    for path, node in tree.filter(javalang.tree.VariableDeclaration):
        variable_entry = dict()
        variable_entry['name'] = node.declarators[0].name
        variable_entry['type'] = node.type.name if node.type is not None else None
        variable_entry['position'] = node.position
        variable_data.append(variable_entry)

    return variable_data


def extract_function_parameters(param_list):
    parameter_data = list()

    for node in param_list:
        if isinstance(node, javalang.tree.FormalParameter):
            parameter_entry = dict()
            parameter_entry['name'] = node.name
            parameter_entry['type'] = node.type.name
            parameter_entry['position'] = node.position
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
        function_entry['annotations'] = [annotation.name for annotation in node.annotations]
        function_entry['position'] = node.position
        function_data.append(function_entry)

    return function_data


def extract_classes(tree):
    class_data = list()

    for path, node in tree.filter(javalang.tree.ClassDeclaration):
        class_entry = dict()
        class_entry['name'] = node.name
        class_entry['modifiers'] = node.modifiers
        class_entry['annotations'] = [annotation.name for annotation in node.annotations]
        class_entry['position'] = node.position
        class_entry['extends'] = node.extends.name if node.extends is not None else None
        class_entry['implements'] = node.implements.name if node.implements is not None else None
        class_data.append(class_entry)

    return class_data


def extract_metadata(tree, filepath, url):
    assert isinstance(tree, javalang.tree.CompilationUnit), "error"

    metadata = dict()
    metadata['filepath'] = filepath
    metadata['url'] = url
    metadata['imports'] = [import_ .path for import_ in tree.imports]
    metadata['package'] = tree.package.name if tree.package is not None else None

    return metadata


def get_json(filename, url, debug=False):
    contents = read(filename)
    tree = javalang.parse.parse(contents)

    debug and print(tree)

    output = dict()
    output['document'] = dict()
    output['document']['metadata'] = extract_metadata(tree, filename, url)
    output['document']['classes'] = extract_classes(tree)
    output['document']['functions'] = extract_functions(tree)
    output['document']['variables'] = extract_variables(tree)
    output['document']['fields'] = extract_fields(tree)

    return json.dumps(output, indent=2, default=serialize_sets)


def main():
    Parser = argparse.ArgumentParser()
    Parser.add_argument("-i", "--input", required=True, help="input file")
    Parser.add_argument("-d", "--debug", help="debug mode", action='store_true')
    args = Parser.parse_args()

    json_object = get_json(args.input, None, debug=args.debug)

    args.debug and print(json_object)


if __name__ == '__main__':
    main()
