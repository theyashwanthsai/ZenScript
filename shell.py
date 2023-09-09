import zen


while(True):
    text = input('zen-shell> ')
    result, error = zen.run( text)
    
    if error: print(error.as_string())
    else: print(result)