########################################################
#                       constants                      #
########################################################
DIGITS = '0123456789'


########################################################
#                       error                          #
########################################################
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



########################################################
#                       position                      #
########################################################
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





########################################################
#                       tokens                         #
########################################################
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
    
    

########################################################
#                       lexer                          #
########################################################
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
        


########################################################
#                       nodes                          
########################################################
class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        
    def __repr__(self):
        return f'{self.tok}'
    
class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        
    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'
    

########################################################
#                       parser                         #
########################################################
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_index = -1
        self.advanceNext()
        
    def advanceNext(self):
        self.tok_index += 1
        if self.tok_index < len(self.tokens):
            self.current_tok = self.tokens[self.tok_index]
        return self.current_tok

########################################################
    def parse(self):
        res = self.expr()
        return res

    def factor(self):
        tok = self.current_tok
        if tok.type in (TT_INT, TT_FLOAT):
            self.advanceNext()
            return NumberNode(tok)
        
    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))
    
    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))
    
    def bin_op(self, func, ops):
        left = func()
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            self.advanceNext()
            right = func()
            left = BinOpNode(left, op_tok, right)
        return left 




        

########################################################
#                       run                            #
########################################################
def run(filename, text):
    
    
    
    ##### Genrate tokens #####
    lexer = Lexer(filename, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error
    ##### Generate AST #####
    parser = Parser(tokens)
    abstract_syntax_tree = parser.parse()
    
    return abstract_syntax_tree, None


    
