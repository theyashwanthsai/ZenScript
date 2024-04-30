########################################################
#                       run                            #
########################################################
from lexer import Lexer
from tokens import Token
from errors import Error, IllegalCharError
def run(fn, text):
    
    # todo: Make chamges in main 
    
    ##### Genrate tokens #####
    # lexer = Lexer(filename, text)
    # tokens, error = lexer.make_tokens()
    # if error: return None, error
    # ##### Generate AST #####
    # parser = Parser(tokens)
    # abstract_syntax_tree = parser.parse()
    
    # return abstract_syntax_tree, None
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    return tokens, error
