# Console Input Skill

**Purpose**: Handle user inputs in Python console apps with validation.

## When to Use
- When prompting user for input (e.g., title, ID).
- Autonomous trigger: If task involves user prompts or validation.

## Instructions
Use this for getting and validating inputs. Example code patterns:

```python
def get_user_input(prompt: str) -> str:
    return input(prompt).strip()

def get_int_input(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Invalid input. Enter a number.")
```
