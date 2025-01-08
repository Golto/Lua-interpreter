# ===============================================
# Lua Evaluator
# Author: Guillaume FOUCAUD
# Date: 06/06/2024
# Description: Executes Lua code represented as an AST.
# ===============================================

from typing import Any, List, Dict, Tuple, Callable, Union

from .native import TableEval, libraries, functions, Library

# ===============================================
# AST Node
# ===============================================

from .ASTNodes import ASTNode
from .ASTNodes import Root, Literal, Table, VariableDeclaration, VariableAssignment, VariableReference
from .ASTNodes import UnaryOperation, BinaryOperation, TernaryOperation
from .ASTNodes import IfStatement, ForStatement, WhileStatement, BreakStatement
from .ASTNodes import FunctionDeclaration, FunctionCall, ReturnStatement
from .ASTNodes import Object, MethodChain, MethodCall

# ===============================================
# Errors
# ===============================================

MAX_LOOP_ITERATIONS = 65_536

class ChainedException(Exception):
    def __init__(self, message: str, line: int, node_name: str, code_line: str, original_exception: Exception = None):
        self.message = message
        self.line = line
        self.node_name = node_name
        self.code_line = code_line
        self.original_exception = original_exception

    def get_format(self) -> str:
        if self.node_name == "Root":
            return f"{self.message} ({self.node_name})"
        return f"{self.message} at line {self.line} ({self.node_name})\n-> {self.line}: {self.code_line}"

    def __str__(self) -> str:
        
        formatted_message = self.get_format()
        error_type = type(self.original_exception).__name__
        
        if self.original_exception:
            formatted_message += f"\n\n{error_type}: {str(self.original_exception)}"

        
        
        return formatted_message



class FunctionCallingError(ChainedException):
    pass

class ReturnError(ChainedException):
    pass

class MaximumLoopError(ChainedException):
    """Exception levée lorsque le nombre maximal d'itérations de boucle est dépassé."""
    pass

class BreakException(ChainedException):
    """Exception utilisée pour gérer l'instruction break dans les boucles."""
    pass

class FunctionNotDeclaredError(ChainedException):
    """Exception levée lorsque la fonction appelée n'est pas déclarée."""
    pass

class VariableNotDeclaredError(ChainedException):
    """Exception levée lorsque la variable référencée n'est pas déclarée."""
    pass

class InvalidOperationError(ChainedException):
    """Exception levée lorsque l'opération effectuée est invalide."""
    pass

class FunctionArgumentError(ChainedException):
    """Exception levée lorsque les arguments passés à une fonction ne correspondent pas aux paramètres attendus."""
    pass

# ===============================================
# Evaluator
# ===============================================

class Evaluator:

    def __init__(self, libraries: List[Library] = []):
        self.environment = {}
        self.logs = ""
        self.return_value = None
        self.environment_stack = []
        self._add_native_functions()
        self._add_native_libs()
        self.libraries = libraries

        self.code = None
        self.lines = []

    def set_code(self, code: str):
        self.code = code
        self.lines = self._split_code_into_lines()

    def _split_code_into_lines(self):
        lines = []
        current_line = ""
        in_string = False
        string_delimiter = None
        i = 0

        if self.code is None:
            raise ValueError("Evaluator does not have any code. Please use .set_code(code) to initialize the code.")
        
        while i < len(self.code):
            char = self.code[i]
            
            if not in_string:
                if char in ["'", '"']:
                    in_string = True
                    string_delimiter = char
                elif char == '[' and i + 1 < len(self.code) and self.code[i+1] == '[':
                    in_string = True
                    string_delimiter = ']]'
                    i += 1  # Skip the next '['
                elif char == '\n':
                    lines.append(current_line)
                    current_line = ""
                    i += 1
                    continue
            else:
                if string_delimiter == ']]' and char == ']' and i + 1 < len(self.code) and self.code[i+1] == ']':
                    in_string = False
                    i += 1  # Skip the next ']'
                elif char == string_delimiter:
                    in_string = False
            
            current_line += char
            i += 1

        if current_line:
            lines.append(current_line)
        
        return lines

    def get_code_line(self, line: int) -> str:
        if line <= 0 or line > len(self.lines):
            return None
        return self.lines[line - 1]
    
    def get_line_from_node(self, node: ASTNode) -> str:
        line = node.line if hasattr(node, 'line') else -1
        code_line = self.get_code_line(line)
        return code_line

    # -----------------------------------------------------------------------
    # Native Functions

    def _add_native_functions(self):
        """
        Add native functions to the environment.
        """
        self.environment.update(functions)
        self.environment.update({
            "print": self.native_print,
            "require": self.native_require,
        })

    def native_print(self, *args):
        """print([value1], [value2], ...) : affiche les valeurs passées en argument"""
        self.logs += " ".join(str(arg) for arg in args) + "\n"

    def native_require(self, library_name: str):
        if self.environment.get(library_name):
            raise ImportError(f"Library '{library_name}' already exists in the environment.")

        library = None
        for lib in self.libraries:
            name = lib.name
            if name == library_name:
                library = lib

        if library is None:
            raise ImportError(f"No library named '{library_name}' found.")
        else:
            self.environment[library.name] = library
            return library
    
    # -----------------------------------------------------------------------
    # Native Libs

    def _add_native_libs(self):
        self.environment.update(libraries)

    # -----------------------------------------------------------------------
    # Evaluation

    def evaluate(self, node: ASTNode):
        method_name = 'eval_' + node.__class__.__name__
        method = getattr(self, method_name)
        try:
            return method(node)
        except ChainedException as ce:
            raise ce
        except Exception as e:
            code_line = self.get_line_from_node(node)
            raise ChainedException(str(e), node.line, node.__class__.__name__, code_line, e)

    def eval_Root(self, node: Root):
        try:
            result = None
            for statement in node.body:
                result = self.evaluate(statement)
            return result
        except Exception as e:
            raise ChainedException("Execution stopped", node.line, "Root", self.get_line_from_node(node), e)

    def eval_Literal(self, node: Literal):
        try:
            _type = node.type
            value = node.value

            if _type == "INTEGER":
                return int(value)
            elif _type == "FLOAT":
                return float(value)
            elif _type == "BOOLEAN":
                return value.lower() == "true"
            elif _type == "STRING":
                return str(value)
            elif _type == "NIL":
                return None
            else:
                raise InvalidOperationError(f"Unsupported literal type: {node.type}", node.line, "Literal", self.get_line_from_node(node))
        except Exception as e:
            raise InvalidOperationError(f"Couldn't evaluate literal", node.line, "Literal", self.get_line_from_node(node), e)

    def eval_Table(self, node: Table):
        try:
            evaluated_entries = []
            for key_node, value_node in node.entries:
                if node.is_array:
                    if key_node.type == "INTEGER":
                        evaluated_key = self.evaluate(key_node)
                    else:
                        raise InvalidOperationError(f"Array key must be an integer. Got: {key_node.type}", key_node.line, "Table", self.get_line_from_node(node))
                else:
                    if key_node.type == "IDENTIFIER":
                        evaluated_key = key_node.value
                    else:
                        raise InvalidOperationError(f"Dictionary key must be an identifier. Got: {key_node.type}", key_node.line, "Table", self.get_line_from_node(node))

                evaluated_value = self.evaluate(value_node)
                evaluated_entries.append([evaluated_key, evaluated_value])
            return TableEval(evaluated_entries, node.is_array)
        except Exception as e:
            raise InvalidOperationError(f"Couldn't evaluate table", node.line, "Table", self.get_line_from_node(node), e)

    def eval_VariableDeclaration(self, node: VariableDeclaration):
        try:
            value = self.evaluate(node.value) if node.value else None
            self.environment[node.name] = value
            return value
        except Exception as e:
            raise InvalidOperationError(f"Couldn't declare variable '{node.name}'", node.line, "VariableDeclaration", self.get_line_from_node(node), e)

    def eval_VariableAssignment(self, node: VariableAssignment):
        try:
            if node.name not in self.environment:
                raise VariableNotDeclaredError(f"Variable '{node.name}' is not declared.", node.line, "VariableAssignment", self.get_line_from_node(node))

            if node.index is not None:
                index = self.evaluate(node.index)
                self.environment[node.name][index] = self.evaluate(node.value)
            else:
                self.environment[node.name] = self.evaluate(node.value)
        except Exception as e:
            raise InvalidOperationError(f"Couldn't assign variable '{node.name}'", node.line, "VariableAssignment", self.get_line_from_node(node), e)

    def eval_VariableReference(self, node: VariableReference):
        try:
            if node.name not in self.environment:
                raise VariableNotDeclaredError(f"Variable '{node.name}' is not declared.", node.line, "VariableReference", self.get_line_from_node(node))

            if node.index is not None:
                index = self.evaluate(node.index)
                return self.environment[node.name][index]

            return self.environment[node.name]
        except Exception as e:
            raise InvalidOperationError(f"Couldn't reference variable '{node.name}'", node.line, "VariableReference", self.get_line_from_node(node), e)

    def eval_UnaryOperation(self, node: UnaryOperation):
        try:
            operand = self.evaluate(node.operand)
            operator = node.operator

            if operator == 'MINUS':
                return -operand

            elif operator == 'NOT':
                return not operand

            elif operator == 'HASH':
                if isinstance(operand, TableEval):
                    return len([entry for entry in operand.entries if entry[0] is not None])
                elif isinstance(operand, str):
                    return len(operand)
                else:
                    raise InvalidOperationError(f"Cannot get length of {type(operand).__name__}", node.line, "UnaryOperation", self.get_line_from_node(node))

            else:
                raise InvalidOperationError(f"Unsupported unary operator: {operator}", node.line, "UnaryOperation", self.get_line_from_node(node))
        except Exception as e:
            raise InvalidOperationError(f"Couldn't evaluate unary operation '{operator}'", node.line, "UnaryOperation", self.get_line_from_node(node), e)

    def eval_BinaryOperation(self, node: BinaryOperation):
        try:
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            operator = node.operator

            try:
                if operator == 'PLUS':
                    return left + right

                elif operator == 'MINUS':
                    return left - right

                elif operator == 'MUL':
                    return left * right

                elif operator == 'DIV':
                    return left / right

                elif operator == 'POW':
                    return left ** right

                elif operator == 'MOD':
                    return left % right

                elif operator == 'EQUAL':
                    return left == right

                elif operator == 'NEQUAL':
                    return left != right

                elif operator == 'LT':
                    return left < right

                elif operator == 'LE':
                    return left <= right

                elif operator == 'GT':
                    return left > right

                elif operator == 'GE':
                    return left >= right

                elif operator == 'AND':
                    return left and right

                elif operator == 'OR':
                    return left or right

                elif operator == 'CONCAT':
                    return str(left) + str(right)

                else:
                    raise InvalidOperationError(f"Unsupported binary operator: {operator}", node.line, "BinaryOperation", self.get_line_from_node(node))
            except TypeError as e:
                raise InvalidOperationError(str(e), node.line, "BinaryOperation", self.get_line_from_node(node), e)
        except Exception as e:
            raise InvalidOperationError(f"Couldn't evaluate binary operation '{operator}'", node.line, "BinaryOperation", self.get_line_from_node(node), e)

    def eval_IfStatement(self, node: IfStatement):
        try:
            condition = self.evaluate(node.condition)
            if condition:
                for stmt in node.then_branch:
                    self.evaluate(stmt)
            else:
                for stmt in node.else_branch:
                    self.evaluate(stmt)
        except Exception as e:
            raise InvalidOperationError(f"Couldn't evaluate if statement", node.line, "IfStatement", self.get_line_from_node(node), e)

    def eval_ForStatement(self, node: ForStatement):
        try:
            iteration_count = 0
            if node.start is not None:
                start = self.evaluate(node.start)
                end = self.evaluate(node.end)
                step = self.evaluate(node.step) if node.step else 1

                for i in range(start, int(end) + 1, step):
                    iteration_count += 1
                    if iteration_count > MAX_LOOP_ITERATIONS:
                        raise MaximumLoopError(f"Maximum loop iterations ({MAX_LOOP_ITERATIONS}) exceeded", node.line, "ForStatement", self.get_line_from_node(node))
                    self.environment[node.var_names[0]] = i
                    for stmt in node.body:
                        if isinstance(stmt, BreakStatement):
                            return
                        self.evaluate(stmt)

            elif node.expr_list is not None:
                expr_list = self.evaluate(node.expr_list)

                if hasattr(expr_list, '__iter__'):  # Check if expr_list is a generator
                    for item in expr_list:
                        self.environment[node.var_names[0]] = item[0]
                        if len(node.var_names) > 1:
                            self.environment[node.var_names[1]] = item[1]
                        for stmt in node.body:
                            if isinstance(stmt, BreakStatement):
                                return
                            self.evaluate(stmt)
                else:
                    raise InvalidOperationError("expr_list is not iterable", node.line, "ForStatement", self.get_line_from_node(node))
        except Exception as e:
            raise InvalidOperationError(f"Couldn't evaluate for statement", node.line, "ForStatement", self.get_line_from_node(node), e)

    def eval_WhileStatement(self, node: WhileStatement):
        try:
            iteration_count = 0
            while self.evaluate(node.condition):
                iteration_count += 1
                if iteration_count > MAX_LOOP_ITERATIONS:
                    raise MaximumLoopError(f"Maximum loop iterations ({MAX_LOOP_ITERATIONS}) exceeded", node.line, "WhileStatement", self.get_line_from_node(node))
                for stmt in node.body:
                    if isinstance(stmt, BreakStatement):
                        return
                    self.evaluate(stmt)
        except Exception as e:
            raise InvalidOperationError(f"Couldn't evaluate while statement", node.line, "WhileStatement", self.get_line_from_node(node), e)

    def eval_FunctionDeclaration(self, node: FunctionDeclaration):
        try:
            self.environment[node.name] = node
        except Exception as e:
            raise InvalidOperationError(f"Couldn't declare function '{node.name}'", node.line, "FunctionDeclaration", self.get_line_from_node(node), e)

    def eval_FunctionCall(self, node: FunctionCall):
        try:
            function = self.environment.get(node.name)

            if not function:
                raise FunctionNotDeclaredError(f"Function '{node.name}' is not declared.", node.line, "FunctionCall", self.get_line_from_node(node))

            if callable(function):
                args = [self.evaluate(arg) for arg in node.arguments]
                return function(*args)

            if not isinstance(function, FunctionDeclaration):
                raise InvalidOperationError(f"'{node.name}' is not a function.", node.line, "FunctionCall", self.get_line_from_node(node))

            local_env = self.environment.copy()
            if len(node.arguments) != len(function.params):
                raise FunctionArgumentError(f"Function '{node.name}' expects {len(function.params)} arguments but got {len(node.arguments)}.", node.line, "FunctionCall", self.get_line_from_node(node))

            for param, arg in zip(function.params, node.arguments):
                local_env[param] = self.evaluate(arg)

            self.environment_stack.append(self.environment)
            self.environment = local_env
            self.return_value = None

            try:
                for stmt in function.body:
                    self.evaluate(stmt)
                    if self.return_value is not None:
                        break

                result = self.return_value
                self.return_value = None
                return result
            finally:
                self.environment = self.environment_stack.pop()
        except Exception as e:
            raise FunctionCallingError(f"Error occurred while calling a function", node.line, "FunctionCall", self.get_line_from_node(node), e)

    def eval_ReturnStatement(self, node: ReturnStatement):
        try:
            self.return_value = self.evaluate(node.value)
        except Exception as e:
            raise ReturnError(f"Couldn't return", node.line, "ReturnStatement", self.get_line_from_node(node), e)

    def eval_BreakStatement(self, node: BreakStatement):
        pass

    def eval_Object(self, node: Object):
        try:
            return self.environment.get(node.name)
        except Exception as e:
            raise InvalidOperationError(f"Couldn't evaluate object '{node.name}'", node.line, "Object", self.get_line_from_node(node), e)

    def eval_MethodChain(self, node: MethodChain):
        try:
            parent = self.evaluate(node.parent)
            if isinstance(parent, Library):
                attribute = parent.attributes.get(node.name)
                if attribute is not None:
                    return attribute
                method = parent.methods.get(node.name)
                if method is not None:
                    return method
            raise FunctionNotDeclaredError(f"'{node.name}' not found in library '{parent.name}'", node.line, "MethodChain", self.get_line_from_node(node))
        except Exception as e:
            raise InvalidOperationError(f"Couldn't evaluate method chain '{node.name}'", node.line, "MethodChain", self.get_line_from_node(node), e)

    def eval_MethodCall(self, node: MethodCall):
        try:
            parent = self.evaluate(node.parent)

            if parent is None:
                raise FunctionNotDeclaredError(f"Parent library or method '{node.parent}' not found", node.line, "MethodCall", self.get_line_from_node(node))

            method = parent.methods.get(node.name)

            if not callable(method):
                raise InvalidOperationError(f"'{node.name}' is not a callable method", node.line, "MethodCall", self.get_line_from_node(node))
            args = [self.evaluate(arg) for arg in node.arguments]
            return method(*args)
        except Exception as e:
            raise InvalidOperationError(f"Couldn't call method '{node.name}'", node.line, "MethodCall", self.get_line_from_node(node), e)