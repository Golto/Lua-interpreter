# ===============================================
# Lua execution
# Author: Guillaume FOUCAUD
# Date: 07/05/2024
# Description: Executes Lua code.
# ===============================================

from typing import Any, Dict, Callable, Tuple, List

from ._lexer import Lexer, rules
from ._parser import Parser
from .evaluator import Evaluator


from .native import Library

lexer = Lexer(rules)

class Interpreter:

    language = "Lua"

    def __init__(self, libraries: List[Library] = []) -> None:

        self.evaluator = Evaluator(libraries)
    
    @property
    def libraries(self):
        return self.evaluator.libraries

    @property
    def logs(self):
        return self.evaluator.logs
    
    @property
    def environment(self):
        return self.evaluator.environment
    
    def clear_logs(self):
        self.evaluator.logs = ""

    def reset_environment(self):
        self.evaluator.environment = {}
        self.evaluator.environment_stack = []
        self.evaluator._add_native_functions()
        self.evaluator._add_native_libs()

    def reset(self):
        self.clear_logs()
        self.reset_environment()

    def exec(self, code: str) -> Tuple[str, bool]:
        try:
            tokens = lexer.tokenize(code)
            ast = Parser(tokens, code).parse()
            self.evaluator.set_code(code)
            result = self.evaluator.evaluate(ast)
            return result, True
        
        except Exception as error:
            return error, False

# ===============================================

import re
def find_lua(text: str) -> List[str]:
        """
        Find all Lua code snippets between ```lua and ``` in a given text.
        The search is case-insensitive.
        
        Args:
            text (str): The input text containing possible Lua code blocks.
        
        Returns:
            List[str]: A list of Lua code snippets found in the text.
        """
        pattern = r"```lua(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        return [match.strip() for match in matches]


