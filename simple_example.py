def add(a, b):
    """Add two numbers and return the result."""
    result = a + b
    return result

def subtract(a, b):
    """Subtract b from a and return the result."""
    result = a - b
    return result

def multiply(a, b):
    """Multiply two numbers and return the result."""
    result = a * b
    return result

def divide(a, b):
    """Divide a by b and return the result."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    result = a / b
    return result

def main():
    """Run the calculator example."""
    output = []
    output.append("===== SIMPLE CALCULATOR DEMO =====")
    output.append("Starting execution...")
    
    output.append("\nAddition Test:")
    result = add(1, 2)
    output.append(f"1 + 2 = {result}")
    
    output.append("\nSubtraction Test:")
    result = subtract(5, 3)
    output.append(f"5 - 3 = {result}")
    
    output.append("\nMultiplication Test:")
    result = multiply(4, 6)
    output.append(f"4 * 6 = {result}")
    
    output.append("\nDivision Test:")
    result = divide(10, 2)
    output.append(f"10 / 2 = {result}")
    
    output.append("\nError Handling Test:")
    try:
        output.append("Attempting to execute: 10 / 0")
        result = divide(10, 0)
        output.append(f"10 / 0 = {result}")  # This line will not execute
    except ValueError as e:
        output.append(f"Error caught: {e}")
    
    output.append("\nDemo execution completed!")
    
    # Write output to file
    with open("calculator_output.txt", "w", encoding="utf-8") as f:
        for line in output:
            f.write(line + "\n")
    
    # Also print to console
    for line in output:
        print(line)
    
    return "Calculation completed and saved to calculator_output.txt"

if __name__ == "__main__":
    print("Program execution started...")
    result = main()
    print("\n" + result)
    print("Program execution finished!") 