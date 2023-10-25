import logging
from inspect import getdoc, signature
from typing import Any
from pydantic import create_model,  Field

logger = logging.getLogger(__name__)


def get_arg_model(arg_defs: dict) -> Any:
    annotated_defs = {arg_name: (arg_type, Field()) for arg_name, arg_type in arg_defs.items()}
    args_class = create_model('DynamicArgModel', **annotated_defs)

    class ArgClass(args_class):
        pass

    return ArgClass


def get_arg_defs(function):
    signatures = str(signature(function)).strip("()").split(",")
    print(signatures)
    type_map = {
        "str": str,
        "int": int,
        "float": float,
        "dict": dict,
        "list": list
    }

    arg_defs = {}
    for sig in signatures:
        arg_name, arg_type = sig.split(":")
        arg_name = arg_name.lstrip()
        arg_type = arg_type.lstrip()
        arg_defs.update({arg_name: type_map[arg_type]})

    return arg_defs


def get_arg_annotations(func):
    docstring = getdoc(func) if getdoc(func) else ""
    docs = docstring.replace('\n', '').replace('\t', '')
    arguments = func.__annotations__ if len(func.__annotations__) else {}
    return docs, arguments


def coerse_arg_types(arg_defs: dict, args: dict) -> dict:
    return {arg_name: arg_defs[arg_name](arg_value) for arg_name, arg_value in args.items()}





