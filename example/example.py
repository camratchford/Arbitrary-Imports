from pathlib import Path
from arbitrary_imports import ArbitraryImporter

example_root = Path(__name__).parent.resolve()
test_modules = example_root.parent.joinpath("tests/test_modules")

importer = ArbitraryImporter(test_modules)

# Made to simulate input received from elsewhere (cli, http request, etc)
argument_list = [
    {
        "module": "files",
        "function": "read_file_line",
        "args": "path=something,line_no=2"
    }, {
        "module": "files",
        "function": "write_file_line",
        "args": "path=something,line_no=2,data=something else"
    }, {
        "module": "processes",
        "function": "get_process",
        "args": "process_name=something"
    }, {
        "module": "processes",
        "function": "kill_process",
        "args": "process_name=something,signal=SIGHUP"
    }
]

# Create a list of module names
modules = importer.modules.keys()

# Display list of modules with their functions
for m in modules:
    print(f"Module: {m}")
    print(importer.get_module(m))

# Display a list of functions within a given modules
funcs = list(importer.modules.get("files").keys())
print("\n")
print("functions in module 'files'")
print(funcs)

# Perform pre-execution validation
print("\n")
for item in argument_list:
    mod = item.get("module")
    func = item.get("function")
    args = item.get("args")
    mod_func = importer.modules.get(mod).get(func)
    func_kwargs, arg_def_dict, result_model = importer.get_function_validations(mod_func, args)
    validation = result_model(**func_kwargs)
    print(f"{func} validation object:")
    print(validation)

# Execute
print("\n")
for item in argument_list:
    mod = item.get("module")
    func = item.get("function")
    arg = item.get("args")
    result = importer.execute_function(mod, func, arg)
    print(result)
