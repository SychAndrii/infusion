from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable
import functools


class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

    @abstractmethod
    def perimeter(self) -> float:
        pass


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius**2

    def perimeter(self) -> float:
        return 2 * 3.14159 * self.radius


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class ShapeFactory:
    @staticmethod
    def create_shape(type: str, **kwargs) -> Shape:
        if type == "circle":
            return Circle(**kwargs)
        elif type == "rectangle":
            return Rectangle(**kwargs)
        else:
            raise ValueError(f"Unknown shape type: {type}")


def log_execution(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Executing {func.__name__} with args={args} kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result

    return wrapper


@log_execution
def calculate_area(shape: Shape) -> float:
    return shape.area()


@log_execution
def calculate_perimeter(shape: Shape) -> float:
    return shape.perimeter()


class MathUtils:
    @staticmethod
    def add(a: float, b: float) -> float:
        return a + b

    @staticmethod
    def subtract(a: float, b: float) -> float:
        return a - b


class Cache:
    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value

    def clear(self) -> None:
        self._cache.clear()


def run_example():
    circle = ShapeFactory.create_shape("circle", radius=5)
    rect = ShapeFactory.create_shape("rectangle", width=4, height=3)

    print("Circle Area:", calculate_area(circle))
    print("Rectangle Area:", calculate_area(rect))

    cache = Cache()
    cache.set("circle_area", circle.area())
    cache.set("rect_area", rect.area())
    print("Cache contents:", cache._cache)


if __name__ == "__main__":
    run_example()
