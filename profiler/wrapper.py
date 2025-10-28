import os
import sys
import ast
import inspect
import importlib
import time
import types

from profiler.Profiler import profiler
from profiler.flame_graph import FlameGraph
from profiler.module_collector import collect_all_modules
from profiler.stat_analyzer import StatAnalyzer


class ProfilingVisitor(ast.NodeTransformer):
    def __init__(self, decorate_imports=True, modules: dict[str, str]=None):
        self.decorated = set()
        self.context_stack = []
        self.to_decorate = set()
        self.decorate_imports = decorate_imports
        self.modules: dict[str, str] = {}
        if modules:
            self.modules = modules

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
        if ext == "":
            filename = filename + ".py"
        if os.path.isabs(filename):
            return filename
        for dirname in sys.path:
            if os.path.islink(dirname):
                continue
            '''while os.path.islink(dirname):
                dirname = os.readlink(dirname)'''
            fullname = os.path.join(dirname, filename)
            if os.path.exists(fullname):
                return fullname
        return None

    def visit_Call(self, node: ast.Call):
        self.generic_visit(node)
        func_name = self.get_function_name(node.func)
        if func_name and func_name not in self.decorated:
            profile_attribute = ast.Attribute(
                value=ast.Name(id="profiler", ctx=ast.Load()),
                attr="profile",
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


def decorate_all_modules(all_modules):
    decorated_modules = {}
    for module_name, module_path in all_modules.items():
        if not os.path.exists(module_path):
            continue
        try:
            with open(module_path, "r", encoding="utf-8") as f:
                code = f.read()
            tree = ast.parse(code)
            profiling_visitor = ProfilingVisitor()
            modified_tree = profiling_visitor.visit(tree)
            ast.fix_missing_locations(modified_tree)
            compiled_code = compile(modified_tree, filename=f"{module_path}_mod", mode="exec")
            decorated_modules[module_name] = compiled_code
        except Exception as e:
            print(f"Error decorating module {module_name}: {e}")
    return decorated_modules


def replace_sys_modules(all_modules, decorated_modules):
    print(all_modules)
    # print(*sys.modules, sep="\n")
    for module_name in list(decorated_modules.keys())[::-1]:
        print(module_name)
        compiled_code = decorated_modules[module_name]
        if module_name == "__main__":
            continue
        try:
            module_obj = types.ModuleType(module_name)
            module_globals = {
                "__name__": module_name,
                "__file__": all_modules[module_name],
                "profiler": profiler
            }
            exec(compiled_code, module_globals)
            for name, obj in module_globals.items():
                if not name.startswith('__'):
                    setattr(module_obj, name, obj)
            sys.modules[module_name] = module_obj
        except Exception as e:
            print(f"Error replacing module {module_name}: {e}")
    # print("new modules")
    # print(*sys.modules, sep="\n")


def run_profiled_script(script_path: str, args):
    sys.argv = args[1:]
    all_modules = collect_all_modules(script_path)
    decorated_modules = decorate_all_modules(all_modules)
    replace_sys_modules(all_modules, decorated_modules)
    script_globals = {
        "__name__": "__main__",
        "__file__": script_path,
        "profiler": profiler
    }
    start = time.perf_counter()
    try:
        if "__main__" in decorated_modules:
            exec(decorated_modules["__main__"], script_globals)
        else:
            print("Warning: Main module not found in decorated modules")
    except Exception as e:
        print(f"Error executing decorated script: {e}")
        import traceback
        traceback.print_exc()
    end = time.perf_counter()
    total_time = end - start
    profiler.print_stat()
    graph = FlameGraph.build_flame_graph(total_time, profiler.full_call_stack)
    for line in graph:
        print(line)
    profiler.save_stat("stats.json")
    analyzer = StatAnalyzer("stats.json")
    print(analyzer.top_slowest_tottime(analyzer.get_top_number()))