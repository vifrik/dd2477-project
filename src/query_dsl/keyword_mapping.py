class LookupException(Exception):
    pass


LOOKUP = {
    # metadata
    "filename": "metadata.name",
    "repo": "metadata.repo",
    "import": "metadata.imports",
    "package": "metadata.package",
    # method
    "methodName": "functions.name",
    "methodModifier": "functions.modifiers",
    "returnType": "functions.return_type",
    "functionAnnotation": "functions.annotations",
    "parameterName": "functions.parameters.name",
    "parameterType": "functions.parameters.type",
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