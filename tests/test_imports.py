from pathlib import Path

from arbitrary_imports import ArbitraryImporter


def create_importer():
    tests_root = Path(__name__).parent.resolve()
    test_modules = tests_root.joinpath("test_modules")
    importer = ArbitraryImporter(test_modules)

    return importer


def test_imports():
    importer = create_importer()
    modules = importer.modules

    assert "files" in [str(k) for k in modules.keys()]
    assert "processes" in [str(k) for k in modules.keys()]

    files_module = modules.get("files")
    assert "read_file_line" in [str(k) for k in files_module.keys()]
    assert "write_file_line" in [str(k) for k in files_module.keys()]

    processes_module = modules.get("processes")
    assert "get_process" in [str(k) for k in processes_module.keys()]
    assert "kill_process" in [str(k) for k in processes_module.keys()]


def test_serialization():
    importer = create_importer()
    modules = importer.modules
    assert modules

    serialized_modules = [importer.get_module(k) for k in modules.keys()]
    assert serialized_modules


def test_function_retrieval():
    importer = create_importer()
    modules = importer.modules

    funcs = []
    for k, v in modules.items():
        for item in v.values():
            funcs.append(item)
    assert funcs

    arg_list = [
        "path=something,line_no=2",
        "path=something,line_no=2,data=something else",
        "process_name=something",
        "process_name=something,signal=SIGHUP"
    ]
    func_list = []
    for func, args in zip(funcs, arg_list):
        func_list.append(importer.get_function_validations(func, args))

    assert len(func_list) == 4


def test_function_execution():
    importer = create_importer()
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
    for item in argument_list:
        mod = item.get("module")
        func = item.get("function")
        arg = item.get("args")
        result = importer.execute_function(mod, func, arg)
        assert result

