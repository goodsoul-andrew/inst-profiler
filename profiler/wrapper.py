import sys
import ast
from keyword import kwlist

from profiler.Profiler import profiler


class ProfilingVisitor(ast.NodeTransformer):
    def __init__(self):
        self.decorated = set()
        self.context_stack = []
        self.to_decorate = set()

    '''def visit_ClassDef(self, node):
        self.context_stack.append(node.name)
        self.generic_visit(node)
        self.context_stack.pop()
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.context_stack.append(node.name)
        self.generic_visit(node)
        func_name = self.get_function_name(node)
        result = node
        has_profile_decorator = False
        for decorator in node.decorator_list:
            if (isinstance(decorator, ast.Attribute) and decorator.attr == 'profile' and
                    isinstance(decorator.value, ast.Name) and decorator.value.id == 'profiler'):
                has_profile_decorator = True
                break
        if not has_profile_decorator:
            profiler_name = ast.Name(id='profiler', ctx=ast.Load())
            profile_decorator = ast.Attribute(value=profiler_name, attr='profile', ctx=ast.Load())
            self.decorated.add(func_name)
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
            result = new_node
        self.context_stack.pop()
        return result

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.context_stack.append(node.name)
        self.generic_visit(node)
        func_name = self.get_function_name(node)
        result = node
        has_profile_decorator = False
        for decorator in node.decorator_list:
            if (isinstance(decorator, ast.Attribute) and decorator.attr == 'profile' and
                    isinstance(decorator.value, ast.Name) and decorator.value.id == 'profiler'):
                has_profile_decorator = True
                break
        if not has_profile_decorator:
            profiler_name = ast.Name(id='profiler', ctx=ast.Load())
            profile_decorator = ast.Attribute(value=profiler_name, attr='profile', ctx=ast.Load())
            self.decorated.add(func_name)
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
            result = new_node
        self.context_stack.pop()
        return result'''

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
    print(profiling_visitor.decorated)
    print(profiling_visitor.to_decorate)
    ast.fix_missing_locations(modified_tree)
    compiled_code = compile(modified_tree, filename=f"{script_path}_mod", mode='exec')
    exec(compiled_code, script_globals)
    profiler.print_stat()