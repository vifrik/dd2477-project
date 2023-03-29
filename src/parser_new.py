import javalang


class Utils:
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
            'parameters': [Utils.extract_function_parameter(param_node) for param_node in node.parameters],
            'return_type': node.return_type.name if node.return_type is not None else None,
            'annotations': [annotation.name for annotation in node.annotations],
            'position': node.position

        }


with open("../other/sample_java/MyClass.java", "r") as f:
    source_code = f.read()

tree = javalang.parse.parse(source_code)
for path, node in javalang.ast.walk_tree(tree):
    if isinstance(node, javalang.tree.CompilationUnit):
        print("I am a compilation unit")
    elif isinstance(node, javalang.tree.ClassDeclaration):
        print("I am a class")
    elif isinstance(node, javalang.tree.MethodDeclaration):
        print(Utils.extract_function(node))
    elif isinstance(node, javalang.tree.LocalVariableDeclaration):
        pass
    elif isinstance(node, javalang.tree.FieldDeclaration):
        pass
