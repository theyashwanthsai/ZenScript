## constants
DIGITS = '0123456789'

## error

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.error_name = error_name
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.details = details
       
        
    def as_string(self):
        result = f'{self.error_name}: {self.details}\n'
        result = result + f'File {self.pos_start.filename}, line {self.pos_start.line + 1}' 
        return result
    
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)



## position

class Position:
    def __init__(self, index, line, column, filename, filetext):
        self.index = index
        self.line = line
        self.column = column
        self.filename = filename
        self.filetext = filetext
        
    def advanceIndex(self, current_char):
        self.index += 1
        self.column += 1
        
        if current_char == '\n':
            self.line += 1
            self.column = 0
            
        return self
    
    def copy(self):
        return Position(self.index, self.line, self.column, self.filename, self.filetext)




## tokens
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_RPAREN = 'RPAREN'
TT_LPAREN = 'LPAREN'

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    
    
## lexer

class Lexer:
    def __init__(self, filename, text):
        self.filename = filename
        self.text = text
        self.pos = Position(-1, 0, -1, filename, text )
        self.current_char = None
        self.advanceNext()
        
    def advanceNext(self):
        self.pos.advanceIndex(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index  < len(self.text) else None
        
    def make_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in ' \t':
                self.advanceNext()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advanceNext()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advanceNext()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advanceNext()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advanceNext()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advanceNext()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advanceNext()
            # if the current character is not in any of the above cases, then it is an invalid character
            else: 
                pos_start = self.pos.copy()
                
                char = self.current_char
                self.advanceNext()
                return [], IllegalCharError(pos_start, self.pos,  "'" + char + "'")
         
        return tokens, None  
    
    def make_number(self):
        num_str = ''
        dot_count = 0
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advanceNext()
        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))
        


        
## run
def run(filename, text):
    lexer = Lexer(filename, text)
    tokens, error = lexer.make_tokens()
    return tokens, error 
