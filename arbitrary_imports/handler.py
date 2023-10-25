
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

        if not Path(self.path).resolve().exists():
            raise FileNotFoundError(f"{path} does not exist")
        self.modules = self.load_modules_from_dir()

    @classmethod
    def filter_contains_init(cls, path: Path):
        """
        Checks if the given path contains a file called "__init__.py"
        """
        return True if "__init__.py" in [p.name for p in path.iterdir()] else False

    def identify_python_modules(self, path: Path):
        """
        Iterates through the given path, producing a list of python modules within.
        """
        python_modules = [i for i in path.iterdir() if Path(i).is_dir() and self.filter_contains_init(Path(i))]
        if not python_modules:
            raise FileNotFoundError(
                f"No Python modules found in {str(path)}. "
                f"Ensure that modules contain a called named __init__.py"
            )
        return python_modules

    @classmethod
    def load_functions_from_dir(cls, directory_path: str):
        """
        Returns a dictionary of functions contained in the given module path.
        """
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
        """
        Executes the given function from the given module with the given arguments.
        Passes the returned value of the executed function.
        """
        mod_func = self.modules .get(module).get(function)
        func_kwargs, arg_def_dict, result_model = self.get_function_validations(mod_func, arg)
        validation = result_model(**func_kwargs)

        if validation:
            result = mod_func(**func_kwargs)
        else:
            raise ValueError(f"Args: {func_kwargs} does not match arg type defs {arg_def_dict}")

        return {"results": result}

    def load_modules_from_dir(self):
        """
        Assembles a dictionary of modules with their contained functions within.
        """
        module_directory = Path(self.path)
        module_dict = {}

        # Generate the list of modules with pathlib
        module_list = self.identify_python_modules(module_directory)

        for path in module_list:
            function_list = self.load_functions_from_dir(str(path))
            module_dict[path.name] = function_list

        return module_dict

    @staticmethod
    def get_function_validations(mod_func: str, arg: str):
        """
        Generates function validation information:
            argument type mapping, dictionary of kwargs,
            and the Pydantic model associated with the given function's execution.
        """
        # Split multiple args separated by a comma
        arg_list = arg.split(",")
        # split the arg name and arg value, making a dictionary
        func_kwargs = {arg_name: arg_value for arg_name, arg_value in [arg.split("=") for arg in arg_list]}
        # Parse the function spec and produce the required argument types
        arg_def_dict = get_arg_defs(mod_func)
        # Coerse the string-based arguments into the required argument type, if necessary
        func_kwargs = coerse_arg_types(arg_def_dict, func_kwargs)
        # Generate a Pydantic model based on the argument type requirements of the given function
        result_model = get_arg_model(arg_def_dict)

        return func_kwargs, arg_def_dict, result_model

    def get_module(self, module_name: str):
        """
        Produces a dictionary of function information on functions contained in the given module:
            The function docstring and its argument's type hints.
        """
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
