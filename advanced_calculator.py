import math

class ScientificCalculator:
    """A scientific calculator that provides basic and advanced mathematical operations."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.last_result = 0
        self.memory = 0
        self.history = []
    
    def add(self, a, b):
        """Add two numbers and return the result."""
        result = a + b
        self._record_operation(f"{a} + {b} = {result}")
        self.last_result = result
        return result
    
    def subtract(self, a, b):
        """Subtract b from a and return the result."""
        result = a - b
        self._record_operation(f"{a} - {b} = {result}")
        self.last_result = result
        return result
    
    def multiply(self, a, b):
        """Multiply two numbers and return the result."""
        result = a * b
        self._record_operation(f"{a} * {b} = {result}")
        self.last_result = result
        return result
    
    def divide(self, a, b):
        """Divide a by b and return the result."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self._record_operation(f"{a} / {b} = {result}")
        self.last_result = result
        return result
    
    def power(self, base, exponent):
        """Raise a number to a power."""
        result = math.pow(base, exponent)
        self._record_operation(f"{base}^{exponent} = {result}")
        self.last_result = result
        return result
    
    def square_root(self, number):
        """Calculate the square root of a number."""
        if number < 0:
            raise ValueError("Cannot calculate square root of a negative number")
        result = math.sqrt(number)
        self._record_operation(f"√{number} = {result}")
        self.last_result = result
        return result
    
    def sin(self, angle_degrees):
        """Calculate the sine of an angle in degrees."""
        angle_rad = math.radians(angle_degrees)
        result = math.sin(angle_rad)
        self._record_operation(f"sin({angle_degrees}°) = {result}")
        self.last_result = result
        return result
    
    def cos(self, angle_degrees):
        """Calculate the cosine of an angle in degrees."""
        angle_rad = math.radians(angle_degrees)
        result = math.cos(angle_rad)
        self._record_operation(f"cos({angle_degrees}°) = {result}")
        self.last_result = result
        return result
    
    def tan(self, angle_degrees):
        """Calculate the tangent of an angle in degrees."""
        # Check if the angle is 90 degrees or equivalent
        if angle_degrees % 180 == 90:
            raise ValueError("Tangent is undefined at 90 degrees (and equivalent angles)")
        angle_rad = math.radians(angle_degrees)
        result = math.tan(angle_rad)
        self._record_operation(f"tan({angle_degrees}°) = {result}")
        self.last_result = result
        return result
    
    def log10(self, number):
        """Calculate the base-10 logarithm of a number."""
        if number <= 0:
            raise ValueError("Cannot calculate logarithm of a non-positive number")
        result = math.log10(number)
        self._record_operation(f"log10({number}) = {result}")
        self.last_result = result
        return result
    
    def ln(self, number):
        """Calculate the natural logarithm of a number."""
        if number <= 0:
            raise ValueError("Cannot calculate logarithm of a non-positive number")
        result = math.log(number)
        self._record_operation(f"ln({number}) = {result}")
        self.last_result = result
        return result
    
    def factorial(self, n):
        """Calculate the factorial of a non-negative integer."""
        if not isinstance(n, int) or n < 0:
            raise ValueError("Factorial is only defined for non-negative integers")
        result = math.factorial(n)
        self._record_operation(f"{n}! = {result}")
        self.last_result = result
        return result
    
    def memory_store(self):
        """Store the last result in memory."""
        self.memory = self.last_result
        self._record_operation(f"M+ = {self.memory}")
        return self.memory
    
    def memory_recall(self):
        """Recall the value stored in memory."""
        self._record_operation(f"MR = {self.memory}")
        return self.memory
    
    def memory_clear(self):
        """Clear the memory."""
        old_value = self.memory
        self.memory = 0
        self._record_operation(f"MC (was {old_value})")
        return 0
    
    def get_history(self):
        """Get the calculation history."""
        return self.history
    
    def clear_history(self):
        """Clear the calculation history."""
        self.history = []
        return True
    
    def _record_operation(self, operation_str):
        """Record an operation in history."""
        self.history.append(operation_str)


def demonstrate_calculator():
    """Demonstrate the scientific calculator functionality."""
    calc = ScientificCalculator()
    results = []
    
    # Basic operations
    results.append("===== SCIENTIFIC CALCULATOR DEMO =====")
    results.append("\n1. Basic Operations:")
    results.append(f"Addition: 5 + 3 = {calc.add(5, 3)}")
    results.append(f"Subtraction: 10 - 4 = {calc.subtract(10, 4)}")
    results.append(f"Multiplication: 6 * 7 = {calc.multiply(6, 7)}")
    results.append(f"Division: 20 / 4 = {calc.divide(20, 4)}")
    
    # Scientific operations
    results.append("\n2. Scientific Operations:")
    results.append(f"Power: 2^3 = {calc.power(2, 3)}")
    results.append(f"Square Root: √16 = {calc.square_root(16)}")
    results.append(f"Sine: sin(30°) = {calc.sin(30)}")
    results.append(f"Cosine: cos(60°) = {calc.cos(60)}")
    results.append(f"Tangent: tan(45°) = {calc.tan(45)}")
    results.append(f"Log10: log10(100) = {calc.log10(100)}")
    results.append(f"Natural Log: ln(e) = {calc.ln(math.e)}")
    results.append(f"Factorial: 5! = {calc.factorial(5)}")
    
    # Memory operations
    results.append("\n3. Memory Operations:")
    calc.add(42, 0)  # Put 42 in last_result
    results.append(f"Store in memory: {calc.memory_store()}")
    calc.add(10, 20)  # Change last_result
    results.append(f"Current result: {calc.last_result}")
    results.append(f"Recall from memory: {calc.memory_recall()}")
    results.append(f"Clear memory: {calc.memory_clear()}")
    
    # Error handling
    results.append("\n4. Error Handling:")
    try:
        results.append("Attempting to divide by zero:")
        calc.divide(10, 0)
    except ValueError as e:
        results.append(f"Error caught: {e}")
        
    try:
        results.append("Attempting to calculate square root of negative number:")
        calc.square_root(-1)
    except ValueError as e:
        results.append(f"Error caught: {e}")
    
    try:
        results.append("Attempting to calculate tangent of 90 degrees:")
        calc.tan(90)
    except ValueError as e:
        results.append(f"Error caught: {e}")
    
    # History
    results.append("\n5. Calculation History:")
    for i, entry in enumerate(calc.get_history(), 1):
        results.append(f"{i}. {entry}")
    
    # Write results to file
    with open("scientific_calculator_output.txt", "w", encoding="utf-8") as f:
        for result in results:
            f.write(f"{result}\n")
    
    # Also print to console
    for result in results:
        print(result)
    
    return "Scientific calculator demonstration completed and saved to scientific_calculator_output.txt"


if __name__ == "__main__":
    print("Starting scientific calculator demonstration...")
    result = demonstrate_calculator()
    print("\n" + result)
    print("Demonstration finished!") 