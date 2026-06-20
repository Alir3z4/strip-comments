"""Module docstring."""
import os
import sys

# A line comment
x = 1  # inline comment

def hello(name: str) -> None:
    """Function docstring."""
    print(f"Hello, {name}")

class Greeter:
    """Class docstring."""

    def greet(self) -> str:
        # method comment
        return "hi"
