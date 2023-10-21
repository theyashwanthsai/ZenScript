########################################################
#                       Imports                        #
########################################################
from strings_with_arrows import *




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
        result = result + '\n\n' + string_with_arrows(self.pos_start.filetext, self.pos_start, self.pos_end)
        return result
    
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)


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
        
    def advanceIndex(self, current_char=None):
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
TT_EOF = 'EOF'

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advanceIndex()
            
        if pos_end:
            self.pos_end = pos_end
            
    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
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
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advanceNext()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advanceNext()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advanceNext()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advanceNext()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advanceNext()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advanceNext()
            # if the current character is not in any of the above cases, then it is an invalid character
            else: 
                pos_start = self.pos.copy()
                
                char = self.current_char
                self.advanceNext()
                return [], IllegalCharError(pos_start, self.pos,  "'" + char + "'")

        tokens.append(Token(TT_EOF, pos_start=self.pos ))
        return tokens, None  
    
    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start=self.pos.copy()
        
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advanceNext()
            
        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)
        


########################################################
#                       nodes                          #
########################################################
class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
        
    def __repr__(self):
        return f'{self.tok}'
    
class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
        
    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'
    
class UnaryOpNode:
    def __init__(self, op_tok, right_node):
        self.op_tok = op_tok
        self.right_node = right_node
        
        self.pos_start = self.op_tok.pos_start
        self.pos_end = right_node .pos_end
        
    def __repr__(self):
        return f'({self.op_tok}, {self.right_node})'


########################################################
#                       Parse Result                   #
########################################################
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        
    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
            return res.node
        return res
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        self.error = error
        return self



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

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected '+', '-', '*' or '/'"))
        return res
    
    
########################################################



    def factor(self):
        res = ParseResult()
        tok = self.current_tok
        
        if tok.type in (TT_PLUS, TT_MINUS):
            res.register(self.advanceNext())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))
        
        elif tok.type == TT_LPAREN:
            res.register(self.advanceNext())
            expression = res.register(self.expr())
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advanceNext())
                return res.success(expression)
            else:
                return res.failure(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"))
            
        
        elif tok.type in (TT_INT, TT_FLOAT):
            res.register(self.advanceNext())
            return res.success(NumberNode(tok))
        
        return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected int or float"))
        
    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))
    
    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))
    
    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res
        
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advanceNext())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)
            
        return res.success(left)


########################################################
#                       Values                         #
########################################################

class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        
    def set_pos(self, pos_start = None, pos_end = None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value)
        
    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value)
        
    def multiplied_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value)
        
    def divided_by(self, other):
        if isinstance(other, Number):
            return Number(self.value / other.value)
    
    def __repr__(self):
        return str(self.value)
    

########################################################
#                     Interpreter                      #
########################################################

class Interpreter:
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)
    
    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} Method defined')

###################################################

    def visit_NumberNode(self, node):
        # print("numbernode ")
        return Number(node.tok.value).set_pos(node.pos_start, node.pos_end)

    def visit_BinOpNode(self, node):
        # print("binarynode ")
        l = self.visit(node.left_node)
        r = self.visit(node.right_node)
        if node.op_tok.type == TT_PLUS:
            result = l.added_to(r)
            
        elif node.op_tok.type == TT_MINUS:
            result = l.subbed_by(r)
        
        elif node.op_tok.type == TT_MUL:
            result = l.multiplied_by(r)
            
        elif node.op_tok.type == TT_DIV:
            result = l.divided_by(r)
            
        return result.set_pos(node.pos_start, node.pos_end)
            
    def visit_UnaryOpNode(self, node):
        # print("Unarynode ")
        number = self.visit(node.right_node)
        
        if node.op_tok.type == TT_MINUS:
            number = number.multiplied_by(Number(-1))
        
        return number.set_pos(node.pos_start, node.pos_end)


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
    if abstract_syntax_tree.error: return None, abstract_syntax_tree.error
    
    
    ##### Run the program #####
    interpreter = Interpreter()
    result = interpreter.visit(abstract_syntax_tree.node)
    
    
    return result, None
