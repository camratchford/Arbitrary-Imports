
import logging
import inspect
import importlib.util

from pathlib import Path
from typing import Union

from arbitrary_imports.enumeration import get_arg_annotations, get_arg_defs, get_arg_model, coerse_arg_types

logger = logging.getLogger(__name__)


class ArbitraryImporter(object):
    def __init__(self, path: Union[Path, str]):
        self.path = path
        self.modules = {}

        if Path(self.path).resolve().exists():
            self.modules = self.load_modules_from_dir()

    @classmethod
    def filter_contains_init(cls, path: Path):
        return True if "__init__.py" in [p.name for p in path.iterdir()] else False

    def filter_for_python_module(self, path: Path):
        return [i for i in path.iterdir() if Path(i).is_dir() and self.filter_contains_init(Path(i))]

    @classmethod
    def load_functions_from_dir(cls, directory_path: str):
        func_dict = {}
        path_dir = Path(directory_path)

        for filename in path_dir.iterdir():
            try:
                if filename.suffix == ".py":
                    module_name = filename.name

                    # Load the module
                    spec = importlib.util.spec_from_file_location(module_name, path_dir.joinpath(filename))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Enumerate functions and add to dictionary
                    for name, obj in inspect.getmembers(module):
                        if inspect.isfunction(obj):
                            func_dict[name] = obj
            except Exception as e:
                logger.error(f"Could not import functions from {filename}\n\t{e}")

        return func_dict

    def execute_function(self, module: str, function: str, arg: str):
        mod_func = self.modules .get(module).get(function)
        arg_def_dict, arg_dict, result_model = self.get_function_validations(mod_func, arg)
        validation = result_model(**arg_dict)

        if validation:
            result = mod_func(**arg_dict)
        else:
            raise ValueError(f"Args: {arg_dict} does not match arg type defs {arg_def_dict}")

        return {"results": str(result)}

    def load_modules_from_dir(self):
        module_directory = Path(self.path)
        module_dict = {}

        # Generate the list of modules with pathlib
        module_list = self.filter_for_python_module(module_directory)

        for path in module_list:
            function_list = self.load_functions_from_dir(str(path))
            module_dict[path.name] = function_list

        return module_dict

    @staticmethod
    def get_function_validations(mod_func: str, arg: str):
        arg_list = arg.split(",")
        func_kwargs = {arg_name: arg_value for arg_name, arg_value in [arg.split("=") for arg in arg_list]}

        arg_def_dict = get_arg_defs(mod_func)

        func_kwargs = coerse_arg_types(arg_def_dict, func_kwargs)
        result_model = get_arg_model(arg_def_dict)

        return arg_def_dict, func_kwargs, result_model

    def get_module(self, module_name: str):
        module = {}
        try:
            module = self.modules.get(module_name)
        except IndexError as e:
            logger.error(e)

        if module:
            result = {}
            for func in module.keys():
                func_object = module[func]
                docs, arguments = get_arg_annotations(func_object)
                args = ""
                if arguments:
                    args = [{k: str(v)} for k, v in zip(arguments.keys(), arguments.values()) if v]

                result[func] = {"docstring": docs, "arguments": args}

            return result
