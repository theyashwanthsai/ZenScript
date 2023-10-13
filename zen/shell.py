import main 


while(True):
    text = input('zen-shell> ')
    result, error = main.run('<stdin>' , text)
    
    if error: print(error.as_string())
    else: print(result)