#!/usr/bin/env python

import javalang
import json
import argparse
import os


class Parser:
    class Utils:
        # https://stackoverflow.com/questions/8230315/how-to-json-serialize-sets
        def serialize_sets(obj):
            if isinstance(obj, set):
                return list(obj)

        def extract_field(node):
            return {
                'name': node.declarators[0].name,
                'type': node.type.name if node.type is not None else None,
                'modifiers': node.modifiers,
                'position': node.position
            }

        def extract_variable(node):
            return {
                'name': node.declarators[0].name,
                'type': node.type.name if node.type is not None else None,
                'position': node.position
            }

        def extract_function_parameter(node):
            return {
                'name': node.name,
                'type': node.type.name,
                'position': node.position
            }

        def extract_function(node):
            return {
                'name': node.name,
                'modifiers': node.modifiers,
                'parameters': [Parser.Utils.extract_function_parameter(param_node) for param_node in node.parameters],
                'return_type': node.return_type.name if node.return_type is not None else None,
                'annotations': [annotation.name for annotation in node.annotations],
                'position': node.position

            }

        def extract_class(node):
            return {
                'name': node.name,
                'modifiers': node.modifiers,
                'annotations': [
                    annotation.name for annotation in node.annotations],
                'position': node.position,
                'extends': node.extends.name if node.extends is not None else None,
                # 'implements': node.implements.name if node.implements is not None else None
            }

        def extract_metadata(node):
            return {
                'imports': [import_ .path for import_ in node.imports],
                'package': node.package.name if node.package is not None else None
            }

    def __init__(self, folderpath, metadata_filename):
        self.folderpath = folderpath
        self.metadata_filename = metadata_filename

        with open(os.path.join(folderpath, metadata_filename), "r") as f:
            self.metadata = json.load(f)

    def _parse(self, filename):
        filepath = os.path.join(self.folderpath, filename)

        with open(filepath, "r") as f:
            source_code = f.read()

        result = {
            'metadata': None,
            'functions': [],
            'classes': [],
            'variables': [],
            'fields': []
        }

        tree = javalang.parse.parse(source_code)
        for path, node in javalang.ast.walk_tree(tree):
            if isinstance(node, javalang.tree.CompilationUnit):
                result['metadata'] = self.metadata[filename]
                result['metadata'].update(Parser.Utils.extract_metadata(node))
            elif isinstance(node, javalang.tree.ClassDeclaration):
                result['classes'].append(Parser.Utils.extract_class(node))
            elif isinstance(node, javalang.tree.MethodDeclaration):
                result['functions'].append(Parser.Utils.extract_function(node))
            elif isinstance(node, javalang.tree.LocalVariableDeclaration):
                result['variables'].append(Parser.Utils.extract_variable(node))
            elif isinstance(node, javalang.tree.FieldDeclaration):
                result['fields'].append(Parser.Utils.extract_field(node))

        return result

    def parse_folder(self):
        for filename in os.listdir(self.folderpath):
            if filename == self.metadata_filename:
                continue
            try:
                yield self._parse(filename)
            except javalang.parser.JavaSyntaxError:
                print(f"Something went from parsing {filename}...")
