import zen

while True:
    text = input("zenscript> ")
    result, error = zen.run("<stdin>", text)

    if error:
        print(error.as_string())
    else:
        print(result)

# todo: create a new method in lexer.
# todo: Make changes
# todo: update in lexer, parser, etc
# todo: add support for lee
