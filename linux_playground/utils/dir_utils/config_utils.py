from pathlib import Path
from typing import Any

import yaml

def check_instance(obj: Any, type_of_obj: Any):
    obj_type = type(obj)
    if not isinstance(obj, type_of_obj):
        raise ValueError(f"object instance is not the same as the desired type."
                         f"The type is: {obj_type} and the desired type_of_obj: {type_of_obj}")


def file_exists(file: str):
    path_file: Path = Path(file)
    if not path_file.exists:
        raise FileExistsError("File does not exists")

def check_file_naming_suffix(file: str, suffix):
    suffix_with_dot = f".{suffix}"
    return file.endswith(suffix_with_dot)


def config_load_yaml(config_file: str) -> Any:
    """
    loads the yaml file as config file using the pyyaml.
    Validates before the file is exists and the config file given parameter type, 
    And more decorated issues.
    """
    # first validation
    check_instance(obj=config_file, type_of_obj=str)
    file_exists(file=config_file)
    check_file_naming_suffix(file=config_file, suffix="yaml")
    with open(config_file, "r") as f:
        config_data = yaml.safe_load(f)
    return config_data


