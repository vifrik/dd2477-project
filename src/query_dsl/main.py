import lexer

if __name__ == '__main__':
    query = """returnType:int 
    AND (
    functionName:hello OR 
functionName:hallo )
    """

    tokens = lexer.tokenize(query)
    for token in tokens:
        print(token)