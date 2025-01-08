# Lua Interpreter

This project demonstrates a Python-based Lua interpreter. It allows you to integrate Lua scripting within Python applications and extend Lua with custom Python functions and libraries.

> **Note**
> This project is primarily a first attempt at building an interpreter and should not be used for serious projects.

## Getting Started

### Initialization

```python
from lua.interpreter import Interpreter, Library

def add_five(n):
    return n + 5

libraries = [
    Library(
        name="custom",
        attributes={
            "version": "1.2.3",
            "doc": "A custom Library"
        },
        methods={
            "print_python": print,
            "add_five": add_five
        }
    )
]

interpreter = Interpreter(libraries)
```

### Example: Finding Prime Numbers

The following Lua script uses the Sieve of Eratosthenes algorithm to find all prime numbers up to a given number:

```python
CODE_PRIMES = """
function find_primes_up_to(n)
    if n < 2 then
        return {}
    end

    -- Initialise a table to mark numbers
    local is_prime = {}
    for i = 2, n do
        is_prime[i] = true
    end

    -- Apply Sieve of Eratosthenes
    for i = 2, math.sqrt(n) do
        if is_prime[i] then
            for j = i * i, n, i do
                is_prime[j] = false
            end
        end
    end

    -- Collect all prime numbers
    local primes = {}
    for i = 2, n do
        if is_prime[i] then
            table.insert(primes, i)
        end
    end

    return primes
end

-- Test the function
local n = 50
local primes = find_primes_up_to(n)
print("Prime numbers up to " .. n .. ":")
for _, prime in ipairs(primes) do
    print(prime)
end
"""
```

### Executing Lua Code

Run custom Lua code using the interpreter:

```python
code = """
local custom = require('custom')

local name = "John"
local number = 32

print("New number is " .. custom.add_five(number))

custom.print_python("The name is " .. name) -- print `name` Python-side
"""

result, success = interpreter.exec(code)
```

### Reading the Lua Console

Print the logs from the Lua console:

```python
print(
    f"""# Lua Console:
```plaintext
{interpreter.logs}
```"""
)
```

### Accessing Variables and Functions in Lua Context

You can inspect the Lua environment to list all variables and functions defined:

```python
for key, value in interpreter.environment.items():
    print(key, value)
```

### Resetting the Interpreter

Clear logs or reset the environment to start fresh:

```python
interpreter.clear_logs() # Clear the Lua console
interpreter.reset_environment() # Reset all variables and functions defined in Lua context

interpreter.reset() # Reset both Lua console and context
