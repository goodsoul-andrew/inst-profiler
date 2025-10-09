import sys
import ast
from profiler.Profiler import profiler


class ProfilingVisitor(ast.NodeTransformer):
    def __init__(self):
        self.decorated = set()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        func_name = node.name
        has_profile_decorator = False
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute) and decorator.attr == 'profile' and decorator.value == 'profiler':
                has_profile_decorator = True
                break
        if not has_profile_decorator:
            profiler_name = ast.Name(id='profiler', ctx=ast.Load())
            profile_decorator = ast.Attribute(value=profiler_name, attr='profile', ctx=ast.Load())
            new_decorator_list = [profile_decorator] + node.decorator_list
            new_node = ast.FunctionDef(
                name=node.name,
                args=node.args,
                body=node.body,
                decorator_list=new_decorator_list,
                returns=node.returns,
                type_comment=node.type_comment,
            )
            ast.copy_location(new_node, node)
            return new_node
        else:
            return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        func_name = node.name
        has_profile_decorator = False
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute) and decorator.attr == 'profile' and decorator.value == 'profiler':
                has_profile_decorator = True
                break
        if not has_profile_decorator:
            profiler_name = ast.Name(id='profiler', ctx=ast.Load())
            profile_decorator = ast.Attribute(value=profiler_name, attr='profile', ctx=ast.Load())
            new_decorator_list = [profile_decorator] + node.decorator_list
            new_node = ast.AsyncFunctionDef(
                name=node.name,
                args=node.args,
                body=node.body,
                decorator_list=new_decorator_list,
                returns=node.returns,
                type_comment=node.type_comment
            )
            ast.copy_location(new_node, node)
            return new_node
        else:
            return node

    def get_function_name(self, node_func: ast.expr) -> str:
        if isinstance(node_func, ast.Name):
            return node_func.id
        elif isinstance(node_func, ast.Attribute):
            base_name = self.get_function_name(node_func.value)
            if base_name:
                return f"{base_name}.{node_func.attr}"
            else:
                return node_func.attr
        elif isinstance(node_func, ast.Lambda):
            return None
        else:
            return None

    def visit_Call(self, node: ast.Call):
        self.generic_visit(node)
        func_name = self.get_function_name(node.func)
        return node


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
    profiling_visitor = ProfilingVisitor()
    modified_tree = profiling_visitor.visit(tree)
    ast.fix_missing_locations(modified_tree)
    compiled_code = compile(modified_tree, filename=f"{script_path}_mod", mode='exec')
    exec(compiled_code, script_globals)
    print(profiler.stat)