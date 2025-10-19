import os
import sys
import ast
import inspect
import importlib
import time

from pdb_copy import Pdb
from profiler.Profiler import profiler
from profiler.flame_graph import FlameGraph


class ProfilingVisitor(ast.NodeTransformer):
    def __init__(self):
        self.decorated = set()
        self.context_stack = []
        self.to_decorate = set()
        self.modules = set()

    def get_function_name(self, node_func: ast.expr | ast.stmt) -> str:
        if isinstance(node_func, ast.Name):
            return node_func.id
        elif isinstance(node_func, ast.Attribute):
            base_name = self.get_function_name(node_func.value)
            if base_name:
                return f"{base_name}.{node_func.attr}"
            else:
                return node_func.attr
        elif isinstance(node_func, ast.FunctionDef) or isinstance(node_func, ast.AsyncFunctionDef):
            return ".".join(self.context_stack)
        elif isinstance(node_func, ast.Lambda):
            return None
        else:
            return None

    def lookupmodule(self, filename: str): # скопировал из pdb
        if os.path.isabs(filename) and os.path.exists(filename):
            return filename
        f = os.path.join(sys.path[0], filename)
        root, ext = os.path.splitext(filename)
        if ext == '':
            filename = filename + '.py'
        if os.path.isabs(filename):
            return filename
        for dirname in sys.path:
            while os.path.islink(dirname):
                dirname = os.readlink(dirname)
            fullname = os.path.join(dirname, filename)
            if os.path.exists(fullname):
                return fullname
        return None

    def visit_Import(self, node):
        for mod_name in node.names:
            # print("import", self.lookupmodule(mod_name.name))
            self.modules.add(self.lookupmodule(mod_name.name))
        return node

    def visit_Call(self, node: ast.Call):
        self.generic_visit(node)
        func_name = self.get_function_name(node.func)
        if func_name and func_name not in self.decorated:
            profile_attribute = ast.Attribute(
                value=ast.Name(id='profiler', ctx=ast.Load()),
                attr='profile',
                ctx=ast.Load()
            )
            ast.copy_location(profile_attribute, node)
            call_to_profile_func = ast.Call(
                func=profile_attribute,
                args=[node.func],
                keywords=[]
            )
            ast.copy_location(call_to_profile_func, node)
            wrapped_call_node = ast.Call(
                func=call_to_profile_func,
                args=node.args,
                keywords=node.keywords
            )
            ast.copy_location(wrapped_call_node, node)
            return wrapped_call_node
        return node


def wrap_module_functions(module_name: str, profiler_decorator):
    try:
        module = importlib.import_module(module_name)
        wrapped_module = type(module)()
        for name in dir(module):
            obj = getattr(module, name)
            if callable(obj) and not inspect.isclass(obj):
                try:
                    wrapped_obj = profiler_decorator(obj)
                    setattr(wrapped_module, name, wrapped_obj)
                except Exception as e:
                    print(f"Warning: Could not wrap {module_name}.{name}: {e}", file=sys.stderr)
                    setattr(wrapped_module, name, obj)
            else:
                setattr(wrapped_module, name, obj)
        return wrapped_module
    except ImportError:
        print(f"Warning: Module '{module_name}' not found, cannot wrap its functions.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Warning: Error wrapping module '{module_name}': {e}", file=sys.stderr)
        return None


def decorate_program(script_path):
    with open(script_path, "r") as file:
        code = file.read()
    tree = ast.parse(code)
    # print(ast.dump(tree))
    profiling_visitor = ProfilingVisitor()
    modified_tree = profiling_visitor.visit(tree)
    ast.fix_missing_locations(modified_tree)
    compiled_code = compile(modified_tree, filename=f"{script_path}_mod", mode='exec')
    return compiled_code


def run_profiled_script(script_path: str, args):
    sys.argv = args[1:]
    script_globals = {
        '__name__': '__main__',
        '__file__': script_path,
        'profiler': profiler
    }
    with open(script_path, "r") as file:
        code = file.read()
    tree = ast.parse(code)
    # print(ast.dump(tree))
    profiling_visitor = ProfilingVisitor()
    modified_tree = profiling_visitor.visit(tree)
    ast.fix_missing_locations(modified_tree)
    compiled_code = compile(modified_tree, filename=f"{script_path}_mod", mode='exec')
    start = time.perf_counter()
    exec(compiled_code, script_globals)
    end = time.perf_counter()
    total_time = end - start
    profiler.print_stat()
    graph = FlameGraph.build_flame_graph(total_time, profiler.full_call_stack)
    for line in graph:
        print(line)