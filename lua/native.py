
from typing import Any, List, Dict, Tuple, Callable, Union

import time
import re
from datetime import datetime
import math
import random

# ===============================================
# Evaluated Table
# ===============================================

class TableEval:
    def __init__(self, entries: List[List[Union[int, str]]], is_array = True):
        self.entries = entries
        self.is_array = is_array

    def __getitem__(self, key: Union[int, str]):
        if self.is_array:
            if not isinstance(key, int):
                raise TypeError(f"Key must be an integer for array. Got: {type(key).__name__}")
            for k, v in self.entries:
                if k == key:
                    return v
            raise KeyError(f"Key {key} not found in array.")
        else:
            if not isinstance(key, str):
                raise TypeError(f"Key must be a string for dictionary. Got: {type(key).__name__}")
            for k, v in self.entries:
                if k == key:
                    return v
            raise KeyError(f"Key {key} not found in dictionary.")
    
    def __setitem__(self, key: Union[int, str], value):
        if self.is_array:
            if not isinstance(key, int):
                raise TypeError(f"Key must be an integer for array. Got: {type(key).__name__}")
            for i, (k, v) in enumerate(self.entries):
                if k == key:
                    self.entries[i][1] = value
                    return
            self.entries.append([key, value])
        else:
            if not isinstance(key, str):
                raise TypeError(f"Key must be a string for dictionary. Got: {type(key).__name__}")
            for i, (k, v) in enumerate(self.entries):
                if k == key:
                    self.entries[i][1] = value
                    return
            self.entries.append([key, value])

    def __repr__(self):
        if self.is_array:
            values = [self.entries[i][1] for i in range(len(self.entries))]
            return f"Table({values})"
        else:
            return f"Table({self.entries})"

def table_to_tuple(table: TableEval) -> Tuple:
    """
    Convert a TableEval instance into a tuple.

    This function extracts the values from a TableEval object and returns them as a tuple.
    It assumes that the `TableEval` instance has entries that are either in array-like form 
    (i.e., the table is structured as a list of key-value pairs where the key is an integer index)
    or dictionary-like form (where the key is a string).

    Parameters:
        table (TableEval): The TableEval instance to be converted to a tuple.

    Returns:
        Tuple: A tuple containing the values from the TableEval entries in the same order as in the table.
    """
    return tuple(entry[1] for entry in table.entries)


def tuple_to_table(tuple_: Tuple) -> TableEval:
    """
    Convert a tuple to a TableEval instance with is_array set to True.

    Parameters:
        tuple_ (Tuple): The tuple to be converted.

    Returns:
        TableEval: A TableEval instance representing the tuple with array-like structure.
    """
    entries = [[i, value] for i, value in enumerate(tuple_)]  # Create key-value pairs with index as key
    table = TableEval(entries, is_array=True)
    return table
# ===============================================
# Library
# ===============================================

class Library:
    def __init__(self, name: str, attributes: Dict[str, Any], methods: Dict[str, Callable]):
        self.name = name
        self.attributes = attributes
        self.methods = methods

    def __repr__(self):
        return f"Library(name='{self.name}', attributes={list(self.attributes.keys())}, methods={list(self.methods.keys())})"

# ===============================================
# Coroutine Library
# ===============================================

class CoroutineLib:

    @staticmethod
    def create(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def resume(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def running(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def status(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def wrap(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def yield_(*args, **kwargs):
        raise PermissionError("Unauthorized method")

# ===============================================
# Package Library
# ===============================================

class PackageLib:

    @staticmethod
    def loadlib(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def searchpath(*args, **kwargs):
        raise PermissionError("Unauthorized method")
    
    loaded = "Unauthorized attribute"
    path = "Unauthorized attribute"
    cpath = "Unauthorized attribute"
    preload = "Unauthorized attribute"

# ===============================================
# String Library
# ===============================================

class StringLib:
    @staticmethod
    def byte(s, i=1, j=None):
        if j is None:
            return ord(s[i-1])
        return [ord(s[k-1]) for k in range(i, j+1)]

    @staticmethod
    def char(*args):
        return ''.join(chr(arg) for arg in args)

    @staticmethod
    def find(s, pattern, init=1, plain=False):
        if plain:
            start = s.find(pattern, init-1)
            if start == -1:
                return None
            return start + 1, start + len(pattern)
        match = re.search(pattern, s[init-1:])
        if match:
            return match.start() + init, match.end() + init - 1
        return None

    @staticmethod
    def format(formatstring, *args):
        return formatstring % args

    @staticmethod
    def gmatch(s, pattern):
        return re.finditer(pattern, s)

    @staticmethod
    def gsub(s, pattern, repl, n=0):
        return re.sub(pattern, repl, s, count=n)

    @staticmethod
    def len(s):
        return len(s)

    @staticmethod
    def lower(s):
        return s.lower()

    @staticmethod
    def match(s, pattern, init=1):
        match = re.match(pattern, s[init-1:])
        if match:
            return match.group(0)
        return None

    @staticmethod
    def rep(s, n, sep=''):
        return (s + sep) * n if sep else s * n

    @staticmethod
    def reverse(s):
        return s[::-1]

    @staticmethod
    def sub(s, i, j=None):
        return s[i-1:j]

    @staticmethod
    def upper(s):
        return s.upper()

# ===============================================
# Table Library
# ===============================================

class TableLib:

    @staticmethod
    def from_Table(table: TableEval):
        if table.is_array:
            return [value for _, value in table.entries]
        else:
            return {key: value for key, value in table.entries}
    
    @staticmethod
    def to_Table(t, is_array=True):
        if is_array:
            entries = [[i+1, t[i]] for i in range(len(t))]
        else:
            entries = [[key, value] for key, value in t.items()]
        return TableEval(entries, is_array)

    # -----------------------

    @staticmethod
    def insert(table: TableEval, pos, value=None):
        t = TableLib.from_Table(table)

        if value is None:
            value = pos
            pos = len(t) + 1
        t.insert(pos - 1, value)

        table.entries = TableLib.to_Table(t, table.is_array).entries

    def remove(table: TableEval, pos=None):
        t = TableLib.from_Table(table)
        
        if pos is None:
            value = t.pop()
        else:
            value = t.pop(pos - 1)
        
        table.entries = TableLib.to_Table(t, table.is_array).entries
        return value

    @staticmethod
    def sort(table: TableEval, comp=None):
        t = TableLib.from_Table(table)
        t.sort(key=comp)
        table.entries = TableLib.to_Table(t, table.is_array).entries

    @staticmethod
    def concat(table: TableEval, sep="", i=1, j=None):
        t = TableLib.from_Table(table)

        if j is None:
            j = len(t)
        return sep.join(str(t[k-1]) for k in range(i, j+1))

# ===============================================
# Math
# ===============================================

class MathLib:

    @staticmethod
    def random(m=None, n=None):
        if m is None:
            return random.random()
        elif n is None:
            return random.randint(1, m)
        else:
            return random.randint(m, n)
    
# ===============================================
# IO Library
# ===============================================

class IO_Lib:

    @staticmethod
    def close(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def flush(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def input(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def lines(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def open(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def output(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def popen(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def read(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def tmpfile(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def type(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def write(*args, **kwargs):
        raise PermissionError("Unauthorized method, please use `print` instead.")

# ===============================================
# OS Library
# ===============================================

class OS_Lib:

    @staticmethod
    def clock():
        return time.clock()

    @staticmethod
    def date(format=None, t=None):
        if t is None:
            t = time.time()
        return time.strftime(format if format else "%c", time.localtime(t))

    @staticmethod
    def difftime(t2, t1):
        return time.difftime(t2, t1)

    @staticmethod
    def execute(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def exit(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def getenv(varname):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def remove(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def rename(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def setlocale(*args, **kwargs):
        raise PermissionError("Unauthorized method")

    @staticmethod
    def time(arg=None):
        if arg is None:
            return int(time.time())
        if isinstance(arg, dict):
            year = arg.get('year', 1970)
            month = arg.get('month', 1)
            day = arg.get('day', 1)
            hour = arg.get('hour', 0)
            minute = arg.get('min', 0)
            second = arg.get('sec', 0)
            dt = datetime(year, month, day, hour, minute, second)
            return int(dt.timestamp())
        raise TypeError("os.time() argument must be a dictionary or None")

    @staticmethod
    def tmpname(*args, **kwargs):
        raise PermissionError("Unauthorized method")
    
# ===============================================
# Debug Library
# ===============================================
# ===============================================
# UTF8 Library
# ===============================================
    
# ===============================================
# Functions
# ===============================================

class Functions:

    @staticmethod
    def native_ipairs(table: TableEval, start_index: int = 1):
        """
        ipairs(t) : itère sur les éléments d’un tableau t avec des indices entiers
        ipairs(t, i) : itère sur les éléments d’un tableau t à partir de l’index i
        """
        if not isinstance(table, TableEval):
            raise TypeError(f"ipairs expected a Table, but got {type(table).__name__}")
        
        if not table.is_array:
            raise ValueError("ipairs expected an array, but got a dictionary")

        def iterator():
            index = start_index
            while index <= len(table.entries):
                for key, value in table.entries:
                    if key == index:
                        yield (index, value)
                        index += 1
                        break
                else:
                    break

        return iterator()

    @staticmethod
    def native_pairs(table: TableEval):
        """
        pairs(t) : itère sur les éléments d’un tableau t avec des indices et des valeurs
        """
        if not isinstance(table, TableEval):
            raise TypeError(f"pairs expected a Table, but got {type(table).__name__}")
        
        if table.is_array:
            raise ValueError("pairs expected a dictionary, but got an array")

        def iterator():
            for key, value in table.entries:
                if not isinstance(key, str):
                    raise ValueError(f"pairs found a non-identifier key in the dictionary: {key}")
                yield (key, value)

        return iterator()
    
    @staticmethod
    def native_assert(v, message=None):
        """
        assert(v, [m]) : vérifie si v est vrai, sinon lève une erreur
        """
        if not v:
            raise AssertionError(message)
        return v

    @staticmethod
    def native_error(message):
        """
        error(message) : lève une erreur avec le message message
        """
        raise Exception(message)

    @staticmethod
    def native_next(table: TableEval, key=None):
        """
        next(t, k) : renvoie le prochain élément de la table t à partir de l’index k
        """
        if not isinstance(table, TableEval):
            raise TypeError(f"next expected a Table, but got {type(table).__name__}")

        keys = list(table.entries.keys())
        if key is None:
            return keys[0], table.entries[keys[0]] if keys else None

        try:
            index = keys.index(key) + 1
            if index < len(keys):
                next_key = keys[index]
                return next_key, table.entries[next_key]
            else:
                return None
        except ValueError:
            raise KeyError(f"Key '{key}' not found in table")

    @staticmethod
    def native_select(index, *args):
        """
        select(index, ...) : renvoie les éléments à partir de l'index donné
        """
        if isinstance(index, int):
            if index < 1 or index > len(args):
                raise IndexError("select index out of range")
            return args[index - 1:]
        elif index == '#':
            return len(args)
        else:
            raise TypeError("select index must be an integer or '#'")

    @staticmethod
    def native_type(obj):
        """
        type(object) : renvoie le type de l’objet object
        """
        if isinstance(obj, str):
            return "string"
        elif isinstance(obj, bool):
            return "boolean"
        elif isinstance(obj, int) or isinstance(obj, float):
            return "number"
        elif isinstance(obj, TableEval):
            return "table"
        elif obj is None:
            return "nil"
        elif callable(obj):
            return "function"
        else:
            return "userdata"  # or "thread", depending on context

    @staticmethod
    def native_tonumber(value, base=10):
        """
        tonumber(e [, base]) : convertit une chaîne en nombre, base peut être de 2 à 36
        """
        if isinstance(value, (int, float)):
            return value

        if not isinstance(value, str):
            return None

        try:
            return int(value, base)
        except ValueError:
            return float(value)

    @staticmethod
    def native_tostring(value):
        """
        tostring(v) : convertit un nombre en chaîne de caractères
        """
        return str(value)

    @staticmethod
    def native_rawget(table: TableEval, key):
        """
        rawget(table, index) : renvoie la valeur associée à l'index sans métaméthodes
        """
        if not isinstance(table, TableEval):
            raise TypeError(f"rawget expected a Table, but got {type(table).__name__}")
        return table.entries.get(key, None)

    @staticmethod
    def native_rawset(table: TableEval, key, value):
        """
        rawset(table, index, value) : assigne une valeur à l'index sans métaméthodes
        """
        if not isinstance(table, TableEval):
            raise TypeError(f"rawset expected a Table, but got {type(table).__name__}")
        table.entries[key] = value
        return table

    @staticmethod
    def native_setmetatable(table: TableEval, metatable: TableEval):
        """
        setmetatable(table, metatable) : définit la métatable d'une table
        """
        if not isinstance(table, TableEval):
            raise TypeError(f"setmetatable expected a Table, but got {type(table).__name__}")
        table.metatable = metatable
        return table

    @staticmethod
    def native_getmetatable(table: TableEval):
        """
        getmetatable(table) : renvoie la métatable d'une table
        """
        if not isinstance(table, TableEval):
            raise TypeError(f"getmetatable expected a Table, but got {type(table).__name__}")
        return table.metatable

    @staticmethod
    def native_pcall(func, *args):
        """
        pcall(f, arg1, ...) : appelle la fonction f avec les arguments donnés en mode protégé
        """
        try:
            return True, func(*args)
        except Exception as e:
            return False, str(e)

    @staticmethod
    def native_xpcall(func, err):
        """
        xpcall(f, err) : appelle la fonction f en mode protégé, en utilisant la fonction err comme gestionnaire d'erreurs
        """
        try:
            return True, func()
        except Exception as e:
            return False, err(e)


# ===============================================
# Libraries
# ===============================================

libraries = {
    "coroutine": Library(
        name="coroutine",
        attributes={},
        methods={
            "create": CoroutineLib.create,
            "resume": CoroutineLib.resume,
            "running": CoroutineLib.running,
            "status": CoroutineLib.status,
            "wrap": CoroutineLib.wrap,
            "yield": CoroutineLib.yield_,
        }
    ),
    "package": Library(
        # Gestion des modules et des packages.
        name="package",
        attributes={
            "loaded": PackageLib.loaded,
            "path": PackageLib.path,
            "cpath": PackageLib.cpath,
            "preload": PackageLib.preload,
        },
        methods={
            "loadlib": PackageLib.loadlib,
            "searchpath": PackageLib.searchpath,
        }
    ),
    "string": Library(
        # Manipulation de chaînes de caractères.
        name="string",
        attributes={},
        methods={
            "byte": StringLib.byte,
            "char": StringLib.char,
            "find": StringLib.find,
            "format": StringLib.format,
            "gmatch": StringLib.gmatch,
            "gsub": StringLib.gsub,
            "len": StringLib.len,
            "lower": StringLib.lower,
            "match": StringLib.match,
            "rep": StringLib.rep,
            "reverse": StringLib.reverse,
            "sub": StringLib.sub,
            "upper": StringLib.upper,
        }
    ),
    "table": Library(
        # Manipulation de tables (structures de données similaires aux tableaux ou dictionnaires).
        name="table",
        attributes={},
        methods={
            "insert": TableLib.insert,
            "remove": TableLib.remove,
            "sort": TableLib.sort,
            "concat": TableLib.concat,
        }
    ),
    "math": Library(
        # Fonctions mathématiques (trigonométrie, exponentiation, etc.).
        name="math",
        attributes={
            "pi": math.pi,
            "huge": float('inf'),
            "maxinteger": float('inf'),
            "mininteger": float('-inf'),
            # custom
            "e": math.e,
            "sqrt2": math.sqrt(2),
        },
        methods={
            "abs": math.fabs,
            "acos": math.acos,
            "asin": math.asin,
            "atan": math.atan,
            "atan2": math.atan2,
            "ceil": math.ceil,
            "cos": math.cos,
            "cosh": math.cosh,
            "deg": math.degrees,
            "exp": math.exp,
            "floor": math.floor,
            "fmod": math.fmod,
            "frexp": math.frexp,
            "ldexp": math.ldexp,
            "log": math.log,
            "log10": math.log10,
            "max": max,
            "min": min,
            "modf": math.modf,
            "pow": math.pow,
            "rad": math.radians,
            "random": MathLib.random,
            "randomseed": random.seed,
            "sin": math.sin,
            "sinh": math.sinh,
            "sqrt": math.sqrt,
            "tan": math.tan,
            "tanh": math.tanh,
        }
    ),
    "io": Library(
        name="io",
        attributes={},
        methods={
            "close": IO_Lib.close,
            "flush": IO_Lib.flush,
            "input": IO_Lib.input,
            "lines": IO_Lib.lines,
            "open": IO_Lib.open,
            "output": IO_Lib.output,
            "popen": IO_Lib.popen,
            "read": IO_Lib.read,
            "tmpfile": IO_Lib.tmpfile,
            "type": IO_Lib.type,
            "write": IO_Lib.write
        }
    ),
    "os": Library(
        name="os",
        attributes={},
        methods={
            "clock": OS_Lib.clock,
            "date": OS_Lib.date,
            "difftime": OS_Lib.difftime,
            "execute": OS_Lib.execute,
            "exit": OS_Lib.exit,
            "getenv": OS_Lib.getenv,
            "remove": OS_Lib.remove,
            "rename": OS_Lib.rename,
            "setlocale": OS_Lib.setlocale,
            "time": OS_Lib.time,
            "tmpname": OS_Lib.tmpname
        }
    ),
    "debug": Library( # TODO
        # Fonctions de débogage.
        name="debug",
        attributes={},
        methods={}
    ),
    "utf8": Library( # TODO
        # Fonctions pour manipuler des chaînes UTF-8 (disponible à partir de Lua 5.3).
        name="utf8",
        attributes={},
        methods={}
    )
}

functions = {
    "ipairs": Functions.native_ipairs,
    "pairs": Functions.native_pairs,
    "assert": Functions.native_assert,
    "error": Functions.native_error,
    "next": Functions.native_next,
    "select": Functions.native_select,
    "type": Functions.native_type,
    "tonumber": Functions.native_tonumber,
    "tostring": Functions.native_tostring,
    "rawget": Functions.native_rawget,
    "rawset": Functions.native_rawset,
    "setmetatable": Functions.native_setmetatable,
    "getmetatable": Functions.native_getmetatable,
    "pcall": Functions.native_pcall,
    "xpcall": Functions.native_xpcall,
}