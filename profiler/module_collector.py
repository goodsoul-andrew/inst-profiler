import ast
import os
import sys


class ModuleCollectorVisitor(ast.NodeTransformer):
    def __init__(self, visited_modules: set = None):
        self.modules: dict[str, str] = {}
        self.compiled_modules = {}
        self.visited_modules = visited_modules if visited_modules is not None else set()

    def lookupmodule(self, filename: str):  # скопировал из pdb
        if os.path.isabs(filename) and os.path.exists(filename):
            return filename
        f = os.path.join(sys.path[0], filename)
        root, ext = os.path.splitext(filename)
        if ext == '':
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

    def visit_Import(self, node):
        for alias in node.names:
            module_path = self.lookupmodule(alias.name)
            if not module_path:
                continue
            module_key = alias.asname or alias.name
            if module_key not in self.modules:
                self.modules[module_key] = module_path
                print(f"Found module: {alias.name} -> {module_key} at {module_path}")
            if module_path not in self.visited_modules:
                self.visited_modules.add(module_path)
                try:
                    with open(module_path, "r", encoding="utf-8") as f:
                        module_code = f.read()
                    module_tree = ast.parse(module_code)
                    module_visitor = ModuleCollectorVisitor(self.visited_modules)
                    module_visitor.modules.update(self.modules)
                    module_visitor.visit(module_tree)
                    self.modules.update(module_visitor.modules)
                except Exception as e:
                    print(f"Error processing module {module_path}: {e}")
        return node

    def visit_ImportFrom(self, node):
        module_path = self.lookupmodule(node.module)
        if not module_path:
            return node
        if node.module not in self.modules:
            self.modules[node.module] = module_path
            # print(f"Found module in from-import: {node.module} at {module_path}")
        if module_path not in self.visited_modules:
            self.visited_modules.add(module_path)
            try:
                with open(module_path, "r", encoding="utf-8") as f:
                    module_code = f.read()
                module_tree = ast.parse(module_code)
                module_visitor = ModuleCollectorVisitor(self.visited_modules)
                module_visitor.modules.update(self.modules)
                module_visitor.visit(module_tree)
                self.modules.update(module_visitor.modules)
            except Exception as e:
                print(f"Error processing module {module_path}: {e}")
        return node


def collect_all_modules(main_script_path):
    main_script_abs = os.path.abspath(main_script_path)
    visitor = ModuleCollectorVisitor()
    visitor.modules["__main__"] = main_script_abs
    visitor.visited_modules.add(main_script_abs)
    with open(main_script_abs, "r", encoding="utf-8") as f:
        main_code = f.read()
    main_tree = ast.parse(main_code)
    visitor.visit(main_tree)
    return visitor.modules