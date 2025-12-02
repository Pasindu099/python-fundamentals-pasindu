from typing import Dict, Any, List
from src.utils import greet_user


def main() -> None:
    name: str = "Pasindu"
    age: str = "26"
    hobbies: List[str] = ["Reading", "Trading", "Traveling"]
    birth_date: str = "1999-11-04"

    profile: Dict[str, Any] = {
        "Name": name,
        "Age": int(age),
        "Hobbies": hobbies,
        "Birth Date": birth_date,
    }

    print(id(profile))

    age_int: int = profile["Age"]
    print("Am I an adult?")
    if age_int < 30:
        print("You are a young adult.")
    elif age_int < 18:
        print("You are a minor.")
    else:
        print("You are an adult.")

    print("\nHobbies:")
    for hobby in hobbies:
        print(f"Hobby: {hobby}")

    count: int = 0
    while count < len(hobbies):
        print(f"Hobby {count + 1}: {hobbies[count]}")
        count += 1

    print("\nUsing enumerate and range:")
    for index, hobby in enumerate(hobbies):
        print(f"Hobby {index + 1}: {hobby}")

    for number in range(1, 6):
        print(f"Number: {number}")

    greeting_message: str = greet_user(name)
    print(greeting_message)


if __name__ == "__main__":
    main()
