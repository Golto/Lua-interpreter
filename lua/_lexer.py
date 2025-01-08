# ===============================================
# Lexer Implementation for Lua Language
# Author: Guillaume FOUCAUD
# Date: 05/05/2024
# ===============================================

import re
from typing import List, Tuple, Any

class Token:
    def __init__(self, type_: str, value: Any, line: int):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, Line {self.line})"


class Lexer:
    def __init__(self, rules: List[Tuple[str, str]]):
        self.rules = [(re.compile(pattern, re.DOTALL), type_) for type_, pattern in rules]

    def tokenize(self, code: str) -> List[Token]:
        tokens = []
        position = 0
        line = 1
        while position < len(code):
            match_found = False
            for pattern, type_ in self.rules:
                match = pattern.match(code, position)
                if match:
                    if type_ == "WS" or type_ == "COMMENT":
                        # Augmenter le numéro de ligne basé sur le nombre de nouvelles lignes dans le match
                        line += match.group(0).count('\n')
                    else:
                        value = match.group(0)
                        if type_ == "LONGSTRING":
                            # Enlever les délimiteurs [[ et ]]
                            value = value[2:-2]
                            line += value.count('\n')
                        if type_ == "STRING":
                            # Enlever les délimiteurs ""
                            value = value[1:-1]
                        tokens.append(Token(type_, value, line))
                        
                    position = match.end()
                    match_found = True
                    break
            if not match_found:
                errored_line = code.split('\n')[line - 1]
                raise SyntaxError(f"Unknown character '{code[position]}' at line {line}, position {position} \n-> {line} :{errored_line}")
            
        tokens.append(Token("EOF", "", line))  # Ajouter un token EOF à la fin
        return tokens

# ===============================================
# Tokenization Rules Definition
# ===============================================

rules = [
    ("COMMENT", r"--[^\n]*"),
    ("WS", r"\s+"),
    ("LONGSTRING", r"\[\[.*?\]\]"),
    ("STRING", r'"[^"]*"|\'[^\']*\''),
    ("NIL", r"\bnil\b"),
    ("FLOAT", r"\b\d+\.\d+\b"),
    ("INTEGER", r"\b\d+\b"),
    ("BOOLEAN", r"\b(true|false)\b"),
    # Keywords
    ("FUNCTION", r"\bfunction\b"),
    ("END", r"\bend\b"),
    ("ELSEIF", r"\belseif\b"),
    ("IF", r"\bif\b"),
    ("THEN", r"\bthen\b"),
    ("ELSE", r"\belse\b"),
    ("WHILE", r"\bwhile\b"),
    ("DO", r"\bdo\b"),
    ("LOCAL", r"\blocal\b"),
    ("RETURN", r"\breturn\b"),
    ("FOR", r"\bfor\b"),
    ("IN", r"\bin\b"),
    ("BREAK", r"\bbreak\b"),
    # Identifiers and operators
    ("AND", r"\band\b"),
    ("OR", r"\bor\b"),
    ("NOT", r"\bnot\b"),
    ("CONCAT", r"\.\."),
    ("EQUAL", r"=="),
    ("NEQUAL", r"~="),
    ("LE", r"<="),
    ("GE", r">="),
    ("ASSIGN", r"="),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("POW", r"\^"),
    ("MUL", r"\*"),
    ("DIV", r"/"),
    ("MOD", r"%"),
    ("LT", r"<"),
    ("GT", r">"),
    ("HASH", r"#"),
    ("QUESTION", r"\?"),
    ("COLON", r":"),
    ("NEWLINE", r"\n"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LCURLY", r"\{"),
    ("RCURLY", r"\}"),
    ("LBRACKET", r"\["),
    ("RBRACKET", r"\]"),
    ("SEMICOLON", r";"),
    ("COMMA", r","),
    ("DOT", r"\."),
    ("IDENTIFIER", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
]