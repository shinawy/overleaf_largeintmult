"""
ArithV Lexer for Pygments
Custom lexer for the ArithV hardware description language
"""

from pygments.lexer import RegexLexer, bygroups, words
from pygments.token import *

class ArithVLexer(RegexLexer):
    name = 'ArithV'
    aliases = ['arithv']
    filenames = ['*.arithv']
    
    tokens = {
        'root': [
            # Comments
            (r'#.*$', Comment.Single),
            
            # Strings
            (r'"[^"]*"', String.Double),
            (r"'[^']*'", String.Single),
            
            # Type keywords (blue)
            (words(('input', 'output', 'variable', 'TestBench', 'Module'), 
                   suffix=r'\b'), Keyword.Type),
            
            # Operation keywords (purple/magenta)
            (words(('Add', 'Sub', 'Mul', 'Shl', 'Shr', 'And', 'Or', 'Xor', 
                    'Not', 'Concat', 'Slice', 'PrimMul', 'PrimAdd'), 
                   suffix=r'\b'), Keyword.Reserved),
            
            # Attribute keywords (orange)
            (words(('is_signed', 'op_mode'), suffix=r'\b'), Name.Attribute),
            
            # Numbers
            (r'\b\d+\b', Number.Integer),
            
            # Operators and punctuation
            (r'[=:,\[\](){}]', Punctuation),
            
            # Identifiers
            (r'[a-zA-Z_][a-zA-Z0-9_]*', Name),
            
            # Whitespace
            (r'\s+', Text),
        ]
    }
