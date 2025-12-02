from utils import greet_user


#demostration of variables
def main():
    name = "Pasindu"
    age = "26"
    hobbies = ["Reading", "Trading", "Traveling"]
    birth_date = "1999-11-04"

    profile = {
        "Name": name,
        "Age": age,
        "Hobbies": hobbies,
        "Birth Date": birth_date
    }

    age_int = int(age)
    profile["Age"] = age_int

    print(id(profile))

#demonstration of conditional statements
    print("Am I an adult?")
    if age_int < 30:
        print("You are a young adult.")
    elif age_int < 18:
        print("You are a minor.")
    else:
        print("You are an adult.")
        
    
#demonstration of loops
    print("\nHobbies:")
    for hobby in hobbies:
        print(f"Hobby: {hobby}")    

    count = 0
    while count < len(hobbies):
        print(f"Hobby {count + 1}: {hobbies[count]}")
        count += 1

#demonstration of built-in functions
    print("\nUsing enumerate and range:")
    for index, hobby in enumerate(hobbies):
        print(f"Hobby {index + 1}: {hobby}")

    for number in range(1, 6):
        print(f"Number: {number}")


    greeting_message = greet_user(name)
    print(greeting_message)


if __name__ == "__main__":
    main()
