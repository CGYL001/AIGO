def add(a, b):
    """Add two numbers and return the result."""
    return a + b

def subtract(a, b):
    """Subtract b from a and return the result."""
    return a - b

def multiply(a, b):
    """Multiply two numbers and return the result."""
    return a * b

def divide(a, b):
    """Divide a by b and return the result."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(a, b):
    """Raise a to the power of b and return the result."""
    return a ** b

def modulo(a, b):
    """Return the remainder of a divided by b."""
    if b == 0:
        raise ValueError("Cannot perform modulo with zero")
    return a % b

def calculator():
    """Interactive calculator function."""
    operations = {
        '1': ('Addition', add),
        '2': ('Subtraction', subtract),
        '3': ('Multiplication', multiply),
        '4': ('Division', divide),
        '5': ('Power', power),
        '6': ('Modulo', modulo)
    }
    
    print("\nInteractive Calculator")
    print("=====================")
    
    while True:
        print("\nAvailable operations:")
        for key, (name, _) in operations.items():
            print(f"{key}: {name}")
        print("q: Quit")
        
        choice = input("\nEnter operation (1-6, q to quit): ")
        
        if choice.lower() == 'q':
            print("Thank you for using the calculator. Goodbye!")
            break
            
        if choice not in operations:
            print("Invalid choice. Please try again.")
            continue
            
        try:
            a = float(input("Enter first number: "))
            b = float(input("Enter second number: "))
            
            operation_name, operation_func = operations[choice]
            
            result = operation_func(a, b)
            print(f"\nResult of {operation_name}: {result}")
            
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    print("Simple Calculator Example")
    print(f"2 + 3 = {add(2, 3)}")
    print(f"5 - 2 = {subtract(5, 2)}")
    print(f"4 * 6 = {multiply(4, 6)}")
    print(f"10 / 2 = {divide(10, 2)}")
    print(f"2 ^ 3 = {power(2, 3)}")
    print(f"7 % 3 = {modulo(7, 3)}")
    
    try:
        print(f"5 / 0 = {divide(5, 0)}")
    except ValueError as e:
        print(f"Error: {e}")
        
    # Run the interactive calculator
    calculator() 