import ast
import os
import sys
from collections import OrderedDict


class ModuleCollectorVisitor(ast.NodeTransformer):
    def __init__(self, current_file: str):
        self.modules: OrderedDict[str, str] = OrderedDict()
        self.current_file = current_file
        self.current_dir = os.path.dirname(os.path.abspath(current_file)) if current_file else os.getcwd()

    def update_modules(self, inner_dependencies: OrderedDict[str, str]):
        for key, value in inner_dependencies.items():
            if key in self.modules:
                self.modules.move_to_end(key)
                self.modules[key] = value
            else:
                self.modules[key] = value

    def lookupmodule(self, filename: str):
        if filename.startswith('.'):
            if not self.current_file:
                return None
            return self._resolve_relative_import(filename)
        if self.current_file:
            possible_paths = [
                os.path.join(self.current_dir, filename + '.py'),
                os.path.join(self.current_dir, filename, '__init__.py'),
                os.path.join(self.current_dir, filename.replace('.', os.path.sep) + '.py'),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return os.path.abspath(path)
        launch_dir = os.getcwd()
        possible_paths = [
            os.path.join(launch_dir, filename + '.py'),
            os.path.join(launch_dir, filename, '__init__.py'),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)
        if os.path.isabs(filename) and os.path.exists(filename):
            return filename
        if not filename.endswith('.py'):
            filename = filename + '.py'
        for dirname in sys.path:
            if os.path.islink(dirname):
                continue
            fullname = os.path.join(dirname, filename)
            if os.path.exists(fullname):
                return fullname
        return None

    def _resolve_relative_import(self, relative_name: str):
        if not self.current_file:
            return None
        level = 0
        while relative_name.startswith('.'):
            level += 1
            relative_name = relative_name[1:]
        target_dir = self.current_dir
        for i in range(level - 1):
            target_dir = os.path.dirname(target_dir)
            if not target_dir:
                return None
        if relative_name:
            module_path = os.path.join(target_dir, relative_name + '.py')
            if os.path.exists(module_path):
                return module_path
            init_path = os.path.join(target_dir, relative_name, '__init__.py') # пакет с __init__.py
            if os.path.exists(init_path):
                return init_path
        else:
            init_path = os.path.join(target_dir, '__init__.py') # from . import something
            if os.path.exists(init_path):
                return init_path
        return None

    def visit_Import(self, node):
        for alias in node.names:
            module_path = self.lookupmodule(alias.name)
            if not module_path:
                continue
            module_key = alias.name
            if module_key not in self.modules:
                self.modules[module_key] = module_path
                # print(f"Found module: {alias.name} -> {module_key} at {module_path}")
                try:
                    with open(module_path, "r", encoding="utf-8") as f:
                        module_code = f.read()
                    module_tree = ast.parse(module_code)
                    # module_visitor = ModuleCollectorVisitor(module_path, self.visited_modules)
                    module_visitor = ModuleCollectorVisitor(module_path)
                    # module_visitor.modules.update(self.modules)
                    module_visitor.visit(module_tree)
                    # self.modules.update(module_visitor.modules)
                    self.update_modules(module_visitor.modules)
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
            try:
                with open(module_path, "r", encoding="utf-8") as f:
                    module_code = f.read()
                module_tree = ast.parse(module_code)
                # module_visitor = ModuleCollectorVisitor(module_path, self.visited_modules)
                module_visitor = ModuleCollectorVisitor(module_path)
                # module_visitor.modules.update(self.modules)
                module_visitor.visit(module_tree)
                # self.modules.update(module_visitor.modules)
                self.update_modules(module_visitor.modules)
            except Exception as e:
                print(f"Error processing module {module_path}: {e}")
        return node


def collect_all_modules(main_script_path):
    main_script_abs = os.path.abspath(main_script_path)
    visitor = ModuleCollectorVisitor(main_script_abs)
    visitor.modules["__main__"] = main_script_abs
    with open(main_script_abs, "r", encoding="utf-8") as f:
        main_code = f.read()
    main_tree = ast.parse(main_code)
    # print(ast.dump(main_tree))
    visitor.visit(main_tree)
    return visitor.modules