# ===============================================
# Parser Implementation for Lua Language
# Author: Guillaume FOUCAUD
# Date: 03/06/2024
# ===============================================

from typing import List, Tuple, Any, Union, Optional

# ===============================================
# Token
# ===============================================

class Token:
    def __init__(self, type_: str, value: Any, line: int):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, Line {self.line})"

# ===============================================
# Exception
# ===============================================

class ParserError(Exception):
    """Custom exception class for parser errors."""
    pass

# ===============================================
# AST Nodes
# ===============================================

from .ASTNodes import ASTNode
from .ASTNodes import Root, Literal, Table, VariableDeclaration, VariableAssignment, VariableReference
from .ASTNodes import UnaryOperation, BinaryOperation, TernaryOperation
from .ASTNodes import IfStatement, ForStatement, WhileStatement, BreakStatement
from .ASTNodes import FunctionDeclaration, FunctionCall, ReturnStatement
from .ASTNodes import Object, MethodChain, MethodCall

# ===============================================
# Token
# ===============================================

class Token:
    def __init__(self, type_: str, value: Any, line: int):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, Line {self.line})"

# ===============================================
# Parser
# ===============================================

class Parser:
    def __init__(self, tokens: List[Token], code: str):
        """Initialize the parser with a list of tokens and the source code."""
        self.tokens = tokens
        self.current = 0
        self.code = code
        self.precedence = {
            "OR": 1,
            "AND": 2,
            "EQUAL": 3, "NEQUAL": 3,
            "LT": 4, "GT": 4, "LE": 4, "GE": 4,
            "PLUS": 5, "MINUS": 5,
            "MUL": 6, "DIV": 6, "MOD": 6,
            "CONCAT": 7,
            "POW": 8  # Added precedence for POW
        }

    # ------------------------------------------------------------------
    # Parsing

    def parse(self):
        """Parse the tokens into an AST."""
        try:
            return Root(self.parse_statements(), line=self.peek().line)
        except ParserError as error:
            raise SyntaxError(error)
        
    def parse_statements(self):
        statements = []
        while not self.is_at_end() and not self.check("END") and not self.check("ELSE") and not self.check("ELSEIF"):
            statements.append(self.parse_statement())
        return statements
    
    def parse_statement(self):
        if self.match("LOCAL"):
            if self.check("FUNCTION"):
                self.advance()
                return self.parse_function_declaration(is_local=True)
            else:
                return self.parse_local_declaration()
        
        elif self.match("FUNCTION"):
            return self.parse_function_declaration(is_local=False)
        
        elif self.match("RETURN"):
            return self.parse_return_statement()
        
        elif self.match("IF"):
            return self.parse_if_statement()
        
        elif self.match("FOR"):
            return self.parse_for_statement()
        
        elif self.match("WHILE"):
            return self.parse_while_statement()
        
        elif self.match("BREAK"):
            return BreakStatement(line=self.previous().line)
        
        else:
            return self.parse_expression()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
    # Literal
    def parse_literal(self) -> Literal:
        token = self.previous()
        return Literal(token.value, token.type, line=token.line)
        
    # Primary
    def parse_primary(self) -> ASTNode:
        """Parse primary expressions including parenthesized expressions."""
        if self.match("LPAREN"):
            expr = self.parse_expression()
            self.consume("RPAREN", "Expected ')' after expression.")
            return expr

        elif self.match("NIL", "INTEGER", "FLOAT", "STRING", "BOOLEAN"):
            return self.parse_literal()
        
        elif self.match("LONGSTRING"):
            token = self.previous()
            return Literal(token.value, "STRING", line=token.line)
        
        elif self.match("MINUS", "NOT", "HASH"):  # Added HASH for unary operation
            return self.parse_unary_operation()
        
        elif self.match("LCURLY"):
            return self.parse_table()

        elif self.match("IDENTIFIER"):
            return self.parse_identifier()
    
        else:
            line, errored_line = self.get_line()
            raise ParserError(f"Unsupported primary expression type '{self.peek().type}' at line {line}. \n-> {line} :{errored_line}")
        
    # Unary operation
    def parse_unary_operation(self) -> ASTNode:
        """Parse unary operations."""
        operator = self.previous().type
        operand = self.parse_primary()
        return UnaryOperation(operator, operand, line=self.previous().line)
    
    # Binary operation
    def parse_binary_operation(self, left) -> ASTNode:
        """Parse binary operations."""
        operator = self.previous().type
        right = self.parse_primary()
        return BinaryOperation(left, operator, right, line=self.previous().line)
    
    # Expression
    def parse_expression(self) -> ASTNode:
        return self.parse_expression_with_precedence(0)
    
    # Expression < precedence
    def parse_expression_with_precedence(self, min_precedence: int) -> ASTNode:
        left = self.parse_primary()
        while True:
            if self.peek().type not in self.precedence or self.precedence[self.peek().type] < min_precedence:
                break
            operator = self.advance().type
            right = self.parse_expression_with_precedence(self.precedence[operator] + 1)
            left = BinaryOperation(left, operator, right, line=self.previous().line)
        return left
    
    # Table: array/dictionary
    def parse_table(self) -> Table:
        entries = []
        is_array = True  # Assume the table is array-like unless a key-value pair is found

        while not self.check("RCURLY"):
            if self.match("COMMA"):  # Ignore commas
                continue

            # Check if the next token indicates a key-value pair or an array element
            if self.check("IDENTIFIER") and self.tokens[self.current + 1].type == "ASSIGN":
                # Parse key-value pair
                key = self.advance()
                self.consume("ASSIGN", "Expected '=' after key in table.")
                value = self.parse_expression()
                entries.append([Literal(key.value, key.type, line=key.line), value])
                is_array = False  # This is not an array
            else:
                # Parse array element
                value = self.parse_expression()
                entries.append([Literal(len(entries) + 1, "INTEGER", line=self.peek().line), value])  # Use 1-based indexing for array elements

            if self.match("COMMA"):  # Prepare for the next entry
                continue

        self.consume("RCURLY", "Expected '}' at the end of table.")
        return Table(entries, is_array, line=self.previous().line)
    
    # Identifier
    def parse_identifier(self) -> ASTNode:
        """Parse an identifier which can be a variable name, method chain, function call, etc."""
        name = self.previous().value

        while True:
            if self.match("ASSIGN"):
                # variable_name = value
                value = self.parse_expression()
                return VariableAssignment(name, value, line=self.previous().line)

            elif self.match("LBRACKET"):
                # variable_name[index]
                index = self.parse_expression()
                self.consume("RBRACKET", "Expected ']' after index.")
                if self.match("ASSIGN"):
                    # variable_name[index] = value
                    value = self.parse_expression()
                    return VariableAssignment(name, value, index, line=self.previous().line)
                else:
                    return VariableReference(name, index, line=self.previous().line)

            elif self.check("DOT"):
                # variable_name.method_name...
                return self.parse_method_chain(name)

            elif self.match("LPAREN"):
                # variable_name(...)
                return self.parse_function_call(name)

            else:
                break

        return VariableReference(name, line=self.previous().line)

    # Function Call
    def parse_function_call(self, name) -> FunctionCall:
        arguments = self.parse_arguments()
        self.consume("RPAREN", "Expected ')' after arguments.")
        return FunctionCall(name, arguments, line=self.previous().line)
    
    # Arguments (when calling)
    def parse_arguments(self) -> ASTNode:
        args = []
        if not self.check("RPAREN"):
            while True:
                args.append(self.parse_expression())
                if not self.match("COMMA"):
                    break
        return args
    
    # Chaining of methods
    def parse_method_chain(self, parent_name) -> ASTNode:
        """Parse a chain of methods or property accesses."""
        parent = Object(parent_name, line=self.previous().line)

        while self.match("DOT"):
            method_name = self.consume("IDENTIFIER", "Expected identifier after '.'").value
            if self.match("LPAREN"):
                arguments = self.parse_arguments()
                self.consume("RPAREN", "Expected ')' after arguments.")
                parent = MethodCall(method_name, parent, arguments, line=self.previous().line)
            else:
                parent = MethodChain(method_name, parent, line=self.previous().line)

        return parent
    
    # Variable declaration
    def parse_local_declaration(self) -> VariableDeclaration:
        # The 'local' keyword has already been consumed
        name = self.consume("IDENTIFIER", "Expected identifier after 'local'.").value

        if self.match("COMMA"):
            line, errored_line = self.get_line()
            raise ParserError(f"Multiple assignment detected at line {line}. This interpreter does not support multiple assignments. "
                              f"Please separate the assignments.\n-> {line} :{errored_line}")

        self.consume("ASSIGN", "Expected '=' after identifier.")
        value = self.parse_expression()
        return VariableDeclaration(name, value, line=self.previous().line)
    
    # Function declaration
    def parse_function_declaration(self, is_local = True) -> FunctionDeclaration:
        name = self.consume("IDENTIFIER", "Expected function name after 'function'.").value
        self.consume("LPAREN", "Expected '(' after function name.")
        params = self.parse_parameters()  # This already consumes the closing RPAREN
        body = self.parse_statements()
        self.consume("END", "Expected 'END' to close the function.")
        return FunctionDeclaration(name, params, body, line=self.previous().line)
    
    # Function Parameters
    def parse_parameters(self) -> ASTNode:
        """Parse function parameters from the tokens."""
        parameters = []
        if not self.check("RPAREN"):  # Check if the parameter list is empty
            while True:
                if self.check("IDENTIFIER"):
                    parameters.append(self.advance().value)
                else:
                    line, errored_line = self.get_line()
                    raise ParserError(f"Expected an identifier for parameter name, got {self.peek().type} at line {self.peek().line}. \n-> {line} :{errored_line}")

                # After a parameter, there should be either a comma or a closing parenthesis
                if self.check("RPAREN"):
                    break
                elif self.match("COMMA"):
                    continue  # Continue if there is a comma, expecting another parameter
                else:
                    line, errored_line = self.get_line()
                    raise ParserError(f"Expected ',' or ')', but got {self.peek().type} at line {self.peek().line}. \n-> {line} :{errored_line}")

        self.consume("RPAREN")  # Consume the closing parenthesis
        return parameters
    
    def parse_return_statement(self) -> ReturnStatement:
        value = self.parse_expression()
        return ReturnStatement(value, line=self.previous().line)

    def parse_if_statement(self) -> IfStatement:
        condition = self.parse_expression()
        self.consume("THEN", "Expected 'then' after condition in if-statement.")
        then_branch = self.parse_statements()

        elseif_branches = []
        while self.match("ELSEIF"):
            elseif_condition = self.parse_expression()
            self.consume("THEN", "Expected 'then' after condition in elseif-statement.")
            elseif_branch = self.parse_statements()
            elseif_branches.append((elseif_condition, elseif_branch))

        else_branch = []
        if self.match("ELSE"):
            else_branch = self.parse_statements()

        self.consume("END", "Expected 'end' after if-statement blocks.")
        return IfStatement(condition, then_branch, else_branch, elseif_branches, line=self.previous().line)

    def parse_for_statement(self) -> ForStatement:
        """Parse a 'for' statement, which can be a numeric for-loop or a generic for-loop."""
        
        var_names = self.parse_for_variables()

        if self.match("ASSIGN"):  # Numeric for-loop: for i = start, end, step do ...
            start = self.parse_expression()
            self.consume("COMMA", "Expected ',' after start expression in numeric for-loop.")
            end = self.parse_expression()
            step = None
            if self.match("COMMA"):
                step = self.parse_expression()
            self.consume("DO", "Expected 'do' after expressions in numeric for-loop.")
            body = self.parse_statements()
            self.consume("END", "Expected 'end' after body of numeric for-loop.")
            return ForStatement(var_names, start, end, step, None, body, line=self.previous().line)

        elif self.match("IN"):  # Generic for-loop: for key, value in expr do ...
            expr_list = self.parse_expression()
            self.consume("DO", "Expected 'do' after expressions in generic for-loop.")
            body = self.parse_statements()
            self.consume("END", "Expected 'end' after body of generic for-loop.")
            return ForStatement(var_names, None, None, None, expr_list, body, line=self.previous().line)

        else:
            line, errored_line = self.get_line()
            raise ParserError(f"Expected '=' or 'in' after loop variables, got '{self.peek().type}' at line {line}. \n-> {line} :{errored_line}")

    def parse_for_variables(self) -> List[str]:
        """Parse the variable part of a for loop."""
        var_names = [self.consume("IDENTIFIER", "Expected identifier in for loop.").value]
        
        while self.match("COMMA"):
            var_names.append(self.consume("IDENTIFIER", "Expected identifier after ','.").value)
        
        if not self.check("ASSIGN") and not self.check("IN"):
            line, errored_line = self.get_line()
            raise ParserError(f"Expected '=' or 'in' after loop variables, got '{self.peek().type}' at line {line}. \n-> {line} :{errored_line}")
        
        return var_names

    def parse_while_statement(self) -> WhileStatement:
        condition = self.parse_expression()  # Parse the loop condition
        self.consume("DO", "Expected 'do' after condition in while loop.")
        body = self.parse_statements()  # Parse the loop body
        self.consume("END", "Expected 'end' to close while loop.")
        return WhileStatement(condition, body, line=self.previous().line)
    
    # ------------------------------------------------------------------

    def get_line(self):
        line = self.peek().line
        errored_line = self.code.split('\n')[line - 1]
        return (line, errored_line)

    def advance(self):
        """Advance the current token index and return the current token."""
        if not self.is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]

    def consume(self, token_type, message=None):
        """Consume the next token if it's of the expected type, else raise an error."""
        if self.check(token_type):
            return self.advance()

        if message is None:
            message = f"Expected token '{token_type}'."

        line, errored_line = self.get_line()
        raise ParserError(f"{message} Got '{self.peek().type}' instead at line {self.peek().line}. \n-> {line} :{errored_line}")

    def check(self, type):
        """Check if the current token is of the given type."""
        if self.is_at_end():
            return False
        return self.tokens[self.current].type == type

    def match(self, *types):
        """Consume the current token if its type matches any in the provided types."""
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def peek(self):
        """Return the current token without consuming it."""
        return self.tokens[self.current]
    
    def previous(self):
        """Return the token just before the current one."""
        return self.tokens[self.current - 1]

    def is_at_end(self):
        """Check if the parser has reached the end of the token list."""
        return self.current >= len(self.tokens) or self.tokens[self.current].type == "EOF"
