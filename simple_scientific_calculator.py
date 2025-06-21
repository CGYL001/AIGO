import math

print("START_SCIENTIFIC_CALCULATOR")

# Basic operations
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# Scientific operations
def power(a, b):
    return math.pow(a, b)

def square_root(a):
    if a < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return math.sqrt(a)

def sin_deg(degrees):
    return math.sin(math.radians(degrees))

def cos_deg(degrees):
    return math.cos(math.radians(degrees))

def log10(a):
    if a <= 0:
        raise ValueError("Cannot calculate logarithm of non-positive number")
    return math.log10(a)

# Demo
print("===== SIMPLE SCIENTIFIC CALCULATOR =====")

# Basic operations
print("SECTION_1_BASIC_OPERATIONS")
print("Addition: 5 + 3 =", add(5, 3))
print("Subtraction: 10 - 4 =", subtract(10, 4))
print("Multiplication: 6 * 7 =", multiply(6, 7))
print("Division: 20 / 4 =", divide(20, 4))
print("END_SECTION_1")

# Scientific operations
print("SECTION_2_SCIENTIFIC_OPERATIONS")
print("Power: 2^3 =", power(2, 3))
print("Square Root: sqrt(16) =", square_root(16))
print("Sine: sin(30 degrees) =", sin_deg(30))
print("Cosine: cos(60 degrees) =", cos_deg(60))
print("Log10: log10(100) =", log10(100))
print("END_SECTION_2")

# Error handling
print("SECTION_3_ERROR_HANDLING")
try:
    print("Attempting to divide by zero:")
    result = divide(10, 0)
    print("Result:", result)  # This line won't execute
except ValueError as e:
    print("Error caught:", e)

try:
    print("Attempting to calculate square root of -1:")
    result = square_root(-1)
    print("Result:", result)  # This line won't execute
except ValueError as e:
    print("Error caught:", e)
print("END_SECTION_3")

print("END_SCIENTIFIC_CALCULATOR") 