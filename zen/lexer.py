########################################################
#                       lexer                          #
########################################################
from constants import DIGITS
from tokens import Token, TT_INT, TT_FLOAT, TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_LPAREN, TT_RPAREN
from errors import Error, IllegalCharError
from position import Position


# todo: Make changes to the interpreter
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
        

