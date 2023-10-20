import zen 


while(True):
    text = input('zen-shell> ')
    result, error = zen.run('<stdin>' , text)
    
    if error: print(error.as_string())
    else: print(result)