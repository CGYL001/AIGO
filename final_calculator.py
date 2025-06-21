import math
import statistics
from datetime import datetime

class ScientificCalculator:
    """A comprehensive scientific calculator with history tracking."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.history = []
        self.memory = 0
        self.reset()
    
    def reset(self):
        """Reset the calculator state."""
        self.last_result = 0
        self.record_operation("Calculator Reset")
        return 0
    
    # Basic operations
    def add(self, a, b=None):
        """Add two numbers or add a number to the last result."""
        if b is None:
            b = self.last_result
        result = a + b
        self.record_operation(f"{a} + {b} = {result}")
        self.last_result = result
        return result
    
    def subtract(self, a, b=None):
        """Subtract b from a or subtract a number from the last result."""
        if b is None:
            b = a
            a = self.last_result
        result = a - b
        self.record_operation(f"{a} - {b} = {result}")
        self.last_result = result
        return result
    
    def multiply(self, a, b=None):
        """Multiply two numbers or multiply the last result by a."""
        if b is None:
            b = a
            a = self.last_result
        result = a * b
        self.record_operation(f"{a} * {b} = {result}")
        self.last_result = result
        return result
    
    def divide(self, a, b=None):
        """Divide a by b or divide the last result by a."""
        if b is None:
            b = a
            a = self.last_result
        if b == 0:
            self.record_operation(f"{a} / {b} = Error: Division by zero")
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.record_operation(f"{a} / {b} = {result}")
        self.last_result = result
        return result
    
    # Advanced operations
    def power(self, base, exponent=None):
        """Calculate base raised to exponent or last_result raised to exponent."""
        if exponent is None:
            exponent = base
            base = self.last_result
        result = math.pow(base, exponent)
        self.record_operation(f"{base} ^ {exponent} = {result}")
        self.last_result = result
        return result
    
    def square_root(self, number=None):
        """Calculate the square root of a number or the last result."""
        if number is None:
            number = self.last_result
        if number < 0:
            self.record_operation(f"sqrt({number}) = Error: Negative input")
            raise ValueError("Cannot calculate square root of a negative number")
        result = math.sqrt(number)
        self.record_operation(f"sqrt({number}) = {result}")
        self.last_result = result
        return result
    
    def sin(self, angle_degrees=None):
        """Calculate sine of angle in degrees."""
        if angle_degrees is None:
            angle_degrees = self.last_result
        angle_rad = math.radians(angle_degrees)
        result = math.sin(angle_rad)
        self.record_operation(f"sin({angle_degrees} deg) = {result}")
        self.last_result = result
        return result
    
    def cos(self, angle_degrees=None):
        """Calculate cosine of angle in degrees."""
        if angle_degrees is None:
            angle_degrees = self.last_result
        angle_rad = math.radians(angle_degrees)
        result = math.cos(angle_rad)
        self.record_operation(f"cos({angle_degrees} deg) = {result}")
        self.last_result = result
        return result
    
    def tan(self, angle_degrees=None):
        """Calculate tangent of angle in degrees."""
        if angle_degrees is None:
            angle_degrees = self.last_result
        if angle_degrees % 180 == 90:
            self.record_operation(f"tan({angle_degrees} deg) = Error: Undefined")
            raise ValueError("Tangent undefined at 90, 270, etc. degrees")
        angle_rad = math.radians(angle_degrees)
        result = math.tan(angle_rad)
        self.record_operation(f"tan({angle_degrees} deg) = {result}")
        self.last_result = result
        return result
    
    def log10(self, number=None):
        """Calculate base-10 logarithm."""
        if number is None:
            number = self.last_result
        if number <= 0:
            self.record_operation(f"log10({number}) = Error: Non-positive input")
            raise ValueError("Cannot calculate logarithm of a non-positive number")
        result = math.log10(number)
        self.record_operation(f"log10({number}) = {result}")
        self.last_result = result
        return result
    
    def ln(self, number=None):
        """Calculate natural logarithm."""
        if number is None:
            number = self.last_result
        if number <= 0:
            self.record_operation(f"ln({number}) = Error: Non-positive input")
            raise ValueError("Cannot calculate logarithm of a non-positive number")
        result = math.log(number)
        self.record_operation(f"ln({number}) = {result}")
        self.last_result = result
        return result
    
    def factorial(self, n=None):
        """Calculate factorial."""
        if n is None:
            n = int(self.last_result)
        if not isinstance(n, int) or n < 0:
            self.record_operation(f"{n}! = Error: Invalid input")
            raise ValueError("Factorial is only defined for non-negative integers")
        result = math.factorial(n)
        self.record_operation(f"{n}! = {result}")
        self.last_result = result
        return result
    
    # Statistical functions
    def mean(self, values):
        """Calculate the mean of a list of values."""
        if not values:
            raise ValueError("Cannot calculate mean of empty list")
        result = statistics.mean(values)
        self.record_operation(f"mean({values}) = {result}")
        self.last_result = result
        return result
    
    def median(self, values):
        """Calculate the median of a list of values."""
        if not values:
            raise ValueError("Cannot calculate median of empty list")
        result = statistics.median(values)
        self.record_operation(f"median({values}) = {result}")
        self.last_result = result
        return result
    
    def std_dev(self, values):
        """Calculate the standard deviation of a list of values."""
        if not values or len(values) < 2:
            raise ValueError("Need at least two values for standard deviation")
        result = statistics.stdev(values)
        self.record_operation(f"std_dev({values}) = {result}")
        self.last_result = result
        return result
    
    # Memory functions
    def memory_store(self):
        """Store the last result in memory."""
        self.memory = self.last_result
        self.record_operation(f"M+ = {self.memory}")
        return self.memory
    
    def memory_recall(self):
        """Recall the value stored in memory."""
        self.record_operation(f"MR = {self.memory}")
        self.last_result = self.memory
        return self.memory
    
    def memory_clear(self):
        """Clear the memory."""
        old_value = self.memory
        self.memory = 0
        self.record_operation(f"MC (was {old_value})")
        return 0
    
    # History functions
    def record_operation(self, operation_str):
        """Record an operation in history with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history.append(f"[{timestamp}] {operation_str}")
    
    def get_history(self):
        """Get the calculation history."""
        return self.history
    
    def clear_history(self):
        """Clear the calculation history."""
        self.history = []
        self.record_operation("History Cleared")
        return True


def run_demo():
    print("========================================")
    print("     SCIENTIFIC CALCULATOR DEMO")
    print("========================================")
    
    calc = ScientificCalculator()
    
    print("\n--- BASIC OPERATIONS ---")
    print("Addition: 5 + 3 =", calc.add(5, 3))
    print("Subtraction: 10 - 4 =", calc.subtract(10, 4))
    print("Multiplication: 6 * 7 =", calc.multiply(6, 7))
    print("Division: 20 / 4 =", calc.divide(20, 4))
    
    print("\n--- CHAINED OPERATIONS ---")
    print("Starting with last result:", calc.last_result)
    print("Add 10:", calc.add(10))
    print("Multiply by 2:", calc.multiply(2))
    print("Subtract 5:", calc.subtract(5))
    print("Divide by 3:", calc.divide(3))
    
    print("\n--- SCIENTIFIC OPERATIONS ---")
    print("Power: 2^3 =", calc.power(2, 3))
    print("Square Root of 16 =", calc.square_root(16))
    print("Sine of 30 degrees =", calc.sin(30))
    print("Cosine of 60 degrees =", calc.cos(60))
    print("Tangent of 45 degrees =", calc.tan(45))
    print("Log10 of 100 =", calc.log10(100))
    print("Natural Log of e =", calc.ln(math.e))
    print("Factorial of 5 =", calc.factorial(5))
    
    print("\n--- STATISTICAL OPERATIONS ---")
    data = [4, 7, 2, 9, 6, 3, 5]
    print(f"Sample data: {data}")
    print("Mean:", calc.mean(data))
    print("Median:", calc.median(data))
    print("Standard Deviation:", calc.std_dev(data))
    
    print("\n--- MEMORY OPERATIONS ---")
    calc.add(42, 0)  # Sets last_result to 42
    print("Store in memory:", calc.memory_store())
    calc.add(10, 20)
    print("Current result:", calc.last_result)
    print("Recall from memory:", calc.memory_recall())
    print("After recall, last_result =", calc.last_result)
    print("Clear memory:", calc.memory_clear())
    
    print("\n--- ERROR HANDLING ---")
    try:
        print("Attempting to divide by zero:")
        calc.divide(10, 0)
    except ValueError as e:
        print("  Error caught:", e)
    
    try:
        print("Attempting to calculate square root of -1:")
        calc.square_root(-1)
    except ValueError as e:
        print("  Error caught:", e)
    
    try:
        print("Attempting to calculate tangent of 90 degrees:")
        calc.tan(90)
    except ValueError as e:
        print("  Error caught:", e)
    
    print("\n--- CALCULATION HISTORY ---")
    print("Last 10 operations:")
    for i, entry in enumerate(calc.get_history()[-10:], 1):
        print(f"{i}. {entry}")
    
    print("\nDemo completed!")


if __name__ == "__main__":
    print("Starting scientific calculator demonstration...")
    run_demo()
    print("Demonstration finished!") 