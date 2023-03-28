import parso

with open('main.py', 'r') as f:
    code = f.read()

tree = parso.parse(code)

print(tree.dump())
