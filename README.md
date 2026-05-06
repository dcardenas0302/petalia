# 🌸 Petalia — A Programming Language That Blooms

**Team Petalia** — Diego Cardenas, Reinaldo Roldan  
CS420 Final Project

---

## Overview

Petalia is a flower-themed educational programming language. Data types are named after flowers, output is rendered as visual bouquets and gardens, and the syntax is designed to be readable and beginner-friendly.

---

## Language Reference

### Types

| Keyword    | Meaning              | Example                        |
|------------|----------------------|--------------------------------|
| `rose`     | Integer / Float      | `rose x = 42`                  |
| `tulip`    | String               | `tulip name = "Alice"`         |
| `daisy`    | Boolean              | `daisy flag = petal`           |
| `lily`     | List                 | `lily nums = [1, 2, 3]`        |
| `bouquet`  | Output collection    | `bouquet b = new bouquet()`    |
| `garden`   | Full scene / function| `garden myFn(x) { ... }`       |

### Boolean Literals
- `petal` → `true`
- `wilted` → `false`

### Null
- `bare` → `null / None`

### Output
```
bloom <expression>
```
Renders the value — strings print as text, bouquets and gardens render as visual flower displays.

### Functions
```
garden functionName(tulip param1, rose param2) {
    ...
    return value
}
```

### Control Flow
```
if (condition) { ... } else { ... }
while (condition) { ... }
for (item in list) { ... }
```

### Built-in Functions
- `len(list)` — length of a list
- `str(x)` — convert to string
- `int(x)` — convert to integer
- `range(n)` / `range(start, end)` — generate number range
- `abs(x)`, `max(...)`, `min(...)`, `sqrt(x)`

### List (lily) Methods
- `.add(value)` — append
- `.remove(value)` — remove
- `.pop(index)` — remove and return at index
- `.len()` — length
- `.contains(value)` — membership check

### Bouquet Methods
- `.add(flower_type, label)` — add a flower with label
- `.render()` — get string rendering
- `.size()` — number of flowers

### Garden Methods
- `.add(flower_type, label)` — add a flower
- `.render()` — get visual rendering
- `.size()` — number of items

---

## Running Programs

### Requirements
- Python 3.7+

### Run a single file
```bash
python interpreter.py programs/hello_world.petal
```

### Run all demos
```bash
python interpreter.py --demo
```

---

## Programs

| File                          | Description                              | Type    |
|-------------------------------|------------------------------------------|---------|
| `programs/hello_world.petal`  | Hello World with bouquet rendering       | Simple  |
| `programs/calculator.petal`   | Arithmetic operations with rose numbers  | Simple  |
| `programs/greet.petal`        | Custom greeting function (from spec)     | Simple  |
| `programs/fizzbuzz.petal`     | FizzBuzz 1–15 with flower mapping        | FizzBuzz|
| `programs/fibonacci_garden.petal` | Fibonacci + Bubble Sort as gardens   | Complex |
| `programs/grade_tracker.petal`| Student grade tracker with garden output | Complex |

---

## Sample Output

```
🌷 Hello, World!

🌸 Bouquet:
  🌷 [tulip] Hello, World!
  🌹 [rose]  Welcome to Petalia!
  🌼 [daisy] Where code blooms 🌸
```

```
┌─────────────────────────────────────┐
│           🌻 PETALIA GARDEN 🌻         │
├─────────────────────────────────────┤
│  🌹 1       🌹 2       🌻 Fizz   💐 Buzz   🌸 FizzBuzz │
└─────────────────────────────────────┘
```

---

## Language Design Notes

- **Lexical scoping** with block-level visibility
- **Interpreted** — runs top to bottom
- Supports **Imperative** (while/for loops), **Functional** (garden functions, return values), and **Declarative** (bouquet/garden composition) paradigms
- `.petal` file extension
