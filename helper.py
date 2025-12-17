"""Helper module for HLT to HLP conversion.

This module provides utility functions for interacting with Ixia's HLTAPI and NGPF APIs.
It supports both Python and Tcl interfaces, handles command execution, and provides
parsing utilities for Tcl data structures (lists and dictionaries).
"""

import sys, os
from tkinter import Tcl, TclError

ixn_ngpf = None
ixn_hlt  = None

tcl = Tcl()

def log(msg: str) -> None:
    """Log a message to stdout with immediate flush.
    
    Args:
        msg: The message string to log.
    """
    print(msg, flush=True)

def eval_cmd(cmd: str) -> str:
    """Eval a single Tcl command and log it."""
    log(f"% {cmd}")
    try:
        result = tcl.eval(cmd)
        # if result:
        #     log(result)
        return result
    except TclError as e:
        log(f"TclError: {e}")
        raise

def execute_tcl(command: str, args: str):
    """Execute a Tcl command with arguments.
    
    Args:
        command: The Tcl command to execute.
        args: The arguments to pass to the command.
        
    Returns:
        The result of the Tcl command execution.
    """
    command = command + " " + args
    return eval_cmd(command)

def init_hl_package(module: str):
    """Initialize the HLTAPI package for either Python or Tcl interface.
    
    Args:
        module: Either "python" or "tcl" to specify which interface to initialize.
        
    Note:
        For Python module, initializes IxiaHlt and IxiaNgpf objects.
        For Tcl module, loads the Ixia package.
    """
    if module == "python":
        global ixn_ngpf
        global ixn_hlt
        from ixiatcl   import IxiaTcl
        from ixiahlt   import IxiaHlt
        from ixiangpf  import IxiaNgpf
        from ixiaerror import IxiaError
        
        if os.name == 'nt':
            ixiatcl = IxiaTcl()
        else:
            tcl_dependencies = [
                '/usr/local/lib/',
                '/usr/lib/',
                '/usr/share/tcl8.5',
                '/usr/lib/tcl8.5',
                '/usr/lib/tk8.5',
                '/usr/share/tk8.5',
            ]
            ixiatcl = IxiaTcl(tcl_autopath=tcl_dependencies)
        tcl_debug = tcl
        tcl_debug.eval("puts $auto_path")

        ixn_hlt = IxiaHlt(ixiatcl)
        ixn_ngpf = IxiaNgpf(ixn_hlt)
    elif module == "tcl":
        eval_cmd("package require Ixia")

def get_hlapi_method(name_space: str, func: str):
    """Retrieve a method from the specified HLAPI namespace.
    
    Args:
        name_space: The namespace to search in ("ixiangpf" or "ixia").
        func: The function name to retrieve.
        
    Returns:
        The method object from the specified namespace.
        
    Raises:
        Exception: If the namespace is invalid or the function is not found.
    """
    global ixn_ngpf
    global ixn_hlt
    name_space_map = {
        'ixiangpf': ixn_ngpf,
        'ixia':  ixn_hlt,
    }
    obj = name_space_map.get(name_space, None)
    if not obj:
        raise Exception(f"Invalid namespace: {name_space}")
    method = getattr(obj, func)
    if not method:
        raise Exception(f"Could not find: {func} in namespace: {name_space}")
    return method

def parse_value(value):
    """Parse a Tcl value and convert it to the appropriate Python type.
    
    Converts Tcl strings to Python types: integers, floats, lists, or strings.
    Handles Tcl list syntax with braces.
    
    Args:
        value: The value to parse (can be a string or other type).
        
    Returns:
        The parsed value as a Python type (int, float, list, or str).
    """
    # here we need to convert tcl values string numbers list to python types
    if not isinstance(value, str):
        return value
    
    value = value.strip()
    
    # Handle Tcl lists: \{item1 item2\} or {item1 item2}
    if value.startswith('\\{') and value.endswith('\\}'):
        # Remove the escaped braces
        inner = value[2:-2].strip()
        return parse_tcl_list(inner)
    elif value.startswith('{') and value.endswith('}'):
        # Remove the braces
        inner = value[1:-1].strip()
        return parse_tcl_list(inner)
    
    # Try to convert to number
    try:
        # Try integer first
        if '.' not in value:
            return int(value)
        else:
            return float(value)
    except ValueError:
        pass
    
    # Return as string
    return value

def parse_tcl_list(tcl_list_str):
    """Parse a Tcl list string into a Python list"""
    if not tcl_list_str:
        return []
    
    result = []
    current = ""
    depth = 0
    i = 0
    
    while i < len(tcl_list_str):
        char = tcl_list_str[i]
        
        if char == '{':
            depth += 1
            if depth > 1:
                current += char
        elif char == '}':
            depth -= 1
            if depth > 0:
                current += char
            elif depth == 0 and current:
                # End of nested list
                result.append(parse_tcl_list(current))
                current = ""
        elif char == ' ' and depth == 0:
            # Space at top level - separator
            if current:
                result.append(parse_value(current))
                current = ""
        else:
            current += char
        
        i += 1
    
    # Add last element
    if current:
        result.append(parse_value(current))
    
    return result

def parse_tcl_dict(tcl_string):
    """
    Parse a Tcl dictionary/list string into a Python dictionary.
    Handles nested structures like: {key1 value1} {key2 {nested_key nested_value}}
    
    Example:
        "{status 1} {log {}} {stream_id TI0-HL-L2}" -> 
        {"status": "1", "log": {}, "stream_id": "TI0-HL-L2"}
    """
    if not isinstance(tcl_string, str):
        return tcl_string
    
    tcl_string = tcl_string.strip()
    
    # If it's not wrapped in braces at top level, parse as dict
    result = {}
    i = 0
    
    while i < len(tcl_string):
        # Skip whitespace
        while i < len(tcl_string) and tcl_string[i] == ' ':
            i += 1
        
        if i >= len(tcl_string):
            break
        
        # Expect opening brace for key-value pair
        if tcl_string[i] != '{':
            break
        
        # Find matching closing brace
        i += 1  # skip opening brace
        depth = 1
        start = i
        
        while i < len(tcl_string) and depth > 0:
            if tcl_string[i] == '{':
                depth += 1
            elif tcl_string[i] == '}':
                depth -= 1
            i += 1
        
        # Extract the key-value pair content
        pair_content = tcl_string[start:i-1].strip()
        
        # Split into key and value (first space separates them)
        parts = pair_content.split(' ', 1)
        if len(parts) == 2:
            key = parts[0]
            value = parts[1].strip()
            
            # Parse the value
            if value.startswith('{') and value.endswith('}'):
                # Check if it's a dict or a list
                inner = value[1:-1].strip()
                if is_tcl_dict(inner):
                    result[key] = parse_tcl_dict(value)
                else:
                    # It's a list
                    result[key] = parse_tcl_list(inner) if inner else []
            else:
                result[key] = parse_value(value)
        elif len(parts) == 1:
            # Just a key with no value
            key = parts[0]
            result[key] = ""
    
    return result

def is_tcl_dict(content):
    """Check if content looks like a Tcl dict (has key-value pairs in braces).
    
    Args:
        content: The string content to check.
        
    Returns:
        True if the content appears to be a Tcl dictionary, False otherwise.
    """
    if not content:
        return False
    
    content = content.strip()
    # A dict starts with { and contains space-separated key-value pairs
    if content.startswith('{'):
        return True
    
    # Check if it has the pattern of multiple {key value} pairs
    brace_count = content.count('{')
    if brace_count >= 2:  # Multiple pairs suggest dict
        return True
    
    return False

def execute_python(command, args):
    """Execute a Python HLAPI method with parsed arguments.
    
    Parses the command namespace and function name, converts Tcl-style arguments
    to Python keyword arguments, and executes the corresponding HLAPI method.
    
    Args:
        command: The command string in format "namespace::function".
        args: The arguments string in Tcl format (-arg value -arg2 value2 ...).
        
    Returns:
        The result of the HLAPI method execution.
    """
    print(f"Executing command: {command} with arguments: {args}")
    namespace, func = command.split("::")[-2:]
    print(f"Resolved namespace: {namespace}, function: {func}")
    method = get_hlapi_method(namespace, func)
    # Parse args into a dictionary its in format -arg value -arg2 value2 ...
    arg_list = args.split(" -")
    arg_dict = {}
    for arg in arg_list:
        if not arg.strip():
            continue
        key_value = arg.strip().split(" ", 1)
        key = key_value[0].replace("-", "")
        val = parse_value(key_value[1]) if len(key_value) > 1 else ""
        arg_dict[key] = val
    print(f"Parsed arguments: {arg_dict}")
    result = method(**arg_dict)
    return result
