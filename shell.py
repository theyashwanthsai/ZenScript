import zen

while True:
    text = input("zenscript> ")
    result, error = zen.run("<stdin>", text)

    if error:
        print(error.as_string())
    else:
        print(result)

# todo: Add spell for making functions
# todo: Add if else statement
# todo: todo make compile
# todo: Add new stuff
# todo: make changes here
