class LookupException(Exception):
    pass


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
    "functionAnnotation": "methods.annotations",
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
