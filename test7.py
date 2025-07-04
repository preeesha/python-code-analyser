import math
from datetime import datetime
 
PI = 3.14159
 
def add(a, b):
    """Add two numbers."""
    return a + b
 
def get_current_time():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")
 
class Circclearle:
    def __init__(self, radius):
        self.radius = radius
 
    def area(self):
        return PI * self.radius ** 2
 
    def perimeter(self):
        return 2 * PI * self.radius
 
def main():
    c = Circclearle(5)
    print("Area:", c.area())
    print("Perimeter:", c.perimeter())
 
    if c.radius > 10:
        print("Big circle")
    else:
        print("Small circle")
 
if __name__ == "__main__":
    main()
 