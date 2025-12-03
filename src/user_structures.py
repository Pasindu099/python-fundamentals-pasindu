from typing import TypedDict, Callable, TypeVar, Any, List
from collections import namedtuple
from dataclasses import dataclass
from pydantic import BaseModel
import numpy as np
from numpy.typing import NDArray
import time
import pandas as pd
import json
import yaml
import os
import xml.etree.ElementTree as ET

# Directory of this file → src/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Project root → one level above src/
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Data directory
DATA_DIR = os.path.join(PROJECT_ROOT, "data")


# user data structures


class UserTypedDict(TypedDict):
    name: str
    age: int
    email: str


UserNamedTuple = namedtuple("UserNamedTuple", ["name", "age", "email"])


@dataclass
class UserDataclass:
    name: str
    age: int
    email: str


class UserPydantic(BaseModel):
    name: str
    age: int
    email: str


# execution time decorator

T = TypeVar("T")


def measure_time(func: Callable[..., T]) -> Callable[..., T]:
    def wrapper(*args: Any, **kwargs: Any) -> T:
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} execution time: {end - start:.6f} seconds")
        return result

    return wrapper


# scalar multiplication functions


@measure_time
def python_list_scalar_mult(data: List[int], scalar: int) -> List[int]:
    return [scalar * x for x in data]


@measure_time
def numpy_scalar_mult(data: NDArray[np.int64], scalar: int) -> NDArray[np.int64]:
    return data * scalar


# CSV loading function
def load_csv_to_dataframe(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} does not exist")
    return pd.read_csv(file_path)


# Main execution


def main() -> None:
    print("\n--- USER STRUCTURE DEMO ---")

    user_td: UserTypedDict = {"name": "Alice", "age": 30, "email": "alice@gmail.com"}
    print("TypedDict:", user_td)

    user_nt = UserNamedTuple("Alice", 30, "alice@gmail.com")
    print("NamedTuple:", user_nt)

    user_dc = UserDataclass("Alice", 30, "alice@gmail.com")
    print("Dataclass:", user_dc)

    user_pd = UserPydantic(name="Alice", age=30, email="alice@gmail.com")
    print("Pydantic:", user_pd)

    print("\n--- PYTHON LIST vs NUMPY ---")

    N = 1_000_000
    scalar = 5

    py_list = list(range(N))
    np_array: NDArray[np.int64] = np.arange(N, dtype=np.int64)

    python_list_scalar_mult(py_list, scalar)
    numpy_scalar_mult(np_array, scalar)

    # JSON loading
    print("\n--- LOADING JSON ---")
    json_path = os.path.join(DATA_DIR, "users.json")
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        print(json_data)

    # YAML loading
    print("\n--- LOADING YAML ---")
    yaml_path = os.path.join(DATA_DIR, "users.yaml")
    with open(yaml_path, "r", encoding="utf-8") as f:
        yaml_data = yaml.safe_load(f)
        print(yaml_data)

    # XML loading
    print("\n--- LOADING XML ---")
    xml_path = os.path.join(DATA_DIR, "users.xml")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    users_xml: list[UserDataclass] = []

    for user in root.findall("user"):
        name_el = user.find("name")
        age_el = user.find("age")
        email_el = user.find("email")

        name = name_el.text if name_el is not None and name_el.text else ""
        age = int(age_el.text) if age_el is not None and age_el.text else 0
        email = email_el.text if email_el is not None and email_el.text else ""

        users_xml.append(UserDataclass(name=name, age=age, email=email))

    print(users_xml)

    # CSV loading
    print("\n--- LOADING CSV INTO PANDAS ---")
    csv_path = os.path.join(DATA_DIR, "users.csv")
    df = load_csv_to_dataframe(csv_path)
    print(df)


if __name__ == "__main__":
    main()
