class LookupException(Exception):
    pass


EXCLUDE = [
    "filename",
    "repo",
    "import",
    "package"
]


LOOKUP = {
    # metadata
    "filename": "metadata.name",
    "repo": "metadata.repo",
    "import": "metadata.imports",
    "package": "metadata.package",
    # method
    "methodName": "methods.name",
    "methodModifier": "methods.modifiers",
    "returnType": "methods.return_type",
    "methodAnnotation": "methods.annotations",
    "parameterName": "methods.parameters.name",
    "parameterType": "methods.parameters.type",
    # class
    "className": "classes.name",
    "classModifier": "classes.modifiers",
    "classAnnotation": "classes.annotations",
    "classExtend": "classes.extends",
    # variable
    "variableName": "variables.name",
    "variableType": "variables.type",
    # field
    "fieldName": "fields.name",
    "fieldType": "fields.type",
}
