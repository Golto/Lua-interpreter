
from typing import Any, List, Dict, Union, Optional, Tuple

# -----------------------------------------------------------------------------------------

class ASTNode:
    """ Base class for all AST nodes. """
    def __init__(self, line: int):
        self.line = line

# -----------------------------------------------------------------------------------------

class Root(ASTNode):
    def __init__(self, body: List[ASTNode], line: int = 0):
        super().__init__(line)
        self.body = body

    def __repr__(self):
        return f"Root(body=[{', '.join(repr(b) for b in self.body)}], line={self.line})"

# -----------------------------------------------------------------------------------------

class Literal(ASTNode):
    def __init__(self, value: Union[str, int, float, bool], type_: str, line: int):
        super().__init__(line)
        self.value = value
        self.type = type_

    def __repr__(self):
        return f"Literal(value={repr(self.value)}, type={self.type}, line={self.line})"

class Table(ASTNode):
    def __init__(self, entries: List[List[ASTNode]], is_array=True, line: int = 0):
        super().__init__(line)
        self.entries = entries
        self.is_array = is_array

    def __repr__(self):
        if self.is_array:
            values = [self.entries[i][1] for i in range(len(self.entries))]
            return f"Table({values}, line={self.line})"
        else:
            return f"Table({self.entries}, line={self.line})"
        
class VariableDeclaration(ASTNode):
    def __init__(self, name: str, value: Optional[ASTNode], line: int):
        super().__init__(line)
        self.name = name
        self.value = value

    def __repr__(self):
        if self.value is not None:
            return f"VariableDeclaration(name='{self.name}', value={repr(self.value)}, line={self.line})"
        else:
            return f"VariableDeclaration(name='{self.name}', value=None, line={self.line})"
        
class VariableAssignment(ASTNode):
    def __init__(self, name: str, value: ASTNode, index=None, line: int = 0):
        super().__init__(line)
        self.name = name
        self.value = value
        self.index = index

    def __repr__(self):
        if self.index is not None:
            return f"VariableAssignment(name={repr(self.name)}[{self.index}], value={repr(self.value)}, line={self.line})"
        return f"VariableAssignment(name={repr(self.name)}, value={repr(self.value)}, line={self.line})"

class VariableReference(ASTNode):
    def __init__(self, name, index=None, line: int = 0):
        super().__init__(line)
        self.name = name
        self.index = index

    def __repr__(self):
        if self.index is not None:
            return f"VariableReference({self.name}[{self.index}], line={self.line})"
        return f"VariableReference({self.name}, line={self.line})"
    
# -----------------------------------------------------------------------------------------

class UnaryOperation(ASTNode):
    def __init__(self, operator: str, operand: ASTNode, line: int):
        super().__init__(line)
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"UnaryOperation(operator='{self.operator}', operand={repr(self.operand)}, line={self.line})"

class BinaryOperation(ASTNode):
    def __init__(self, left: ASTNode, operator: str, right: ASTNode, line: int):
        super().__init__(line)
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinaryOperation({repr(self.left)}, '{self.operator}', {repr(self.right)}, line={self.line})"

class TernaryOperation(ASTNode):
    def __init__(self, condition: ASTNode, true_expr: ASTNode, false_expr: ASTNode, line: int):
        super().__init__(line)
        self.condition = condition
        self.true_expr = true_expr
        self.false_expr = false_expr

    def __repr__(self):
        return (f"TernaryOperation(condition={repr(self.condition)}, "
                f"true_expr={repr(self.true_expr)}, false_expr={repr(self.false_expr)}, line={self.line})")

# -----------------------------------------------------------------------------------------

class IfStatement(ASTNode):
    def __init__(self, condition: ASTNode, then_branch: List[ASTNode], else_branch: List[ASTNode], elseif_branches: Optional[List[Tuple[ASTNode, List[ASTNode]]]] = None, line: int = 0):
        super().__init__(line)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
        self.elseif_branches = elseif_branches if elseif_branches else []

    def __repr__(self):
        elseif_repr = ', '.join(f"(condition={repr(cond)}, branch=[{', '.join(repr(b) for b in branch)}])" for cond, branch in self.elseif_branches)
        return (f"IfStatement(condition={repr(self.condition)}, then_branch=[{', '.join(repr(t) for t in self.then_branch)}], "
                f"else_branch=[{', '.join(repr(e) for e in self.else_branch)}], elseif_branches=[{elseif_repr}], line={self.line})")

class ForStatement(ASTNode):
    def __init__(self, var_names: List[str], start: Optional[ASTNode], end: Optional[ASTNode], step: Optional[ASTNode], expr_list: Optional[ASTNode], body: List[ASTNode], line: int):
        super().__init__(line)
        self.var_names = var_names
        self.start = start
        self.end = end
        self.step = step
        self.expr_list = expr_list
        self.body = body

    def __repr__(self):
        if self.start is not None:
            return (f"ForStatement(var_names={self.var_names}, start={repr(self.start)}, end={repr(self.end)}, "
                    f"step={repr(self.step)}, body=[{', '.join(repr(stmt) for stmt in self.body)}], line={self.line})")
        else:
            return (f"ForStatement(var_names={self.var_names}, expr_list={repr(self.expr_list)}, "
                    f"body=[{', '.join(repr(stmt) for stmt in self.body)}], line={self.line})")

class WhileStatement(ASTNode):
    def __init__(self, condition: ASTNode, body: List[ASTNode], line: int):
        super().__init__(line)
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileStatement(condition={repr(self.condition)}, body=[{', '.join(repr(b) for b in self.body)}], line={self.line})"
    
class BreakStatement(ASTNode):
    def __init__(self, line: int):
        super().__init__(line)

    def __repr__(self):
        return f"BreakStatement(line={self.line})"

# -----------------------------------------------------------------------------------------

class FunctionDeclaration(ASTNode):
    def __init__(self, name: str, params: List[str], body: List[ASTNode], line: int):
        super().__init__(line)
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        return f"FunctionDeclaration(name={self.name}, params={self.params}, body=[{', '.join(repr(b) for b in self.body)}], line={self.line})"

class FunctionCall(ASTNode):
    def __init__(self, name: str, arguments: List[ASTNode], line: int):
        super().__init__(line)
        self.name = name
        self.arguments = arguments

    def __repr__(self):
        args_repr = ', '.join(repr(arg) for arg in self.arguments)
        return f"FunctionCall(name='{self.name}', arguments=[{args_repr}], line={self.line})"

class ReturnStatement(ASTNode):
    def __init__(self, value: ASTNode, line: int):
        super().__init__(line)
        self.value = value

    def __repr__(self):
        return f"ReturnStatement(value={repr(self.value)}, line={self.line})"

# -----------------------------------------------------------------------------------------

class Object(ASTNode):
    def __init__(self, name: str, line: int = 0):
        super().__init__(line)
        self.name = name

    def __repr__(self):
        return f"Object(name='{self.name}', line={self.line})"

class MethodChain(ASTNode):
    def __init__(self, name: str, parent: ASTNode, line: int = 0):
        super().__init__(line)
        self.name = name
        self.parent = parent

    def __repr__(self):
        return f"MethodChain(name='{self.name}', parent={self.parent}, line={self.line})"
    
class MethodCall(ASTNode):
    def __init__(self, name: str, parent: ASTNode, arguments: List[ASTNode], line: int = 0):
        super().__init__(line)
        self.name = name
        self.parent = parent
        self.arguments = arguments

    def __repr__(self):
        args_repr = ', '.join(repr(arg) for arg in self.arguments)
        return f"MethodCall(name='{self.name}', parent={self.parent}, arguments=[{args_repr}], line={self.line})"
