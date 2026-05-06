
"""
Petalia Interpreter
A flower-themed programming language.
Team Petalia — Diego Cardenas, Reinaldo Roldan

Usage:
    python interpreter.py <file.petal>
    python interpreter.py --demo
"""

import sys
import re
import math
from typing import Any

# ─────────────────────────────────────────────
#  TOKEN TYPES
# ─────────────────────────────────────────────
TT_KEYWORD   = "KEYWORD"
TT_IDENT     = "IDENT"
TT_INT       = "INT"
TT_FLOAT     = "FLOAT"
TT_STRING    = "STRING"
TT_BOOL      = "BOOL"
TT_OP        = "OP"
TT_ASSIGN    = "ASSIGN"
TT_LPAREN    = "LPAREN"
TT_RPAREN    = "RPAREN"
TT_LBRACE    = "LBRACE"
TT_RBRACE    = "RBRACE"
TT_LBRACKET  = "LBRACKET"
TT_RBRACKET  = "RBRACKET"
TT_COMMA     = "COMMA"
TT_DOT       = "DOT"
TT_NEWLINE   = "NEWLINE"
TT_EOF       = "EOF"
TT_COLON     = "COLON"

KEYWORDS = {
    # Types
    "rose", "tulip", "daisy", "lily", "bouquet", "garden",
    # Control flow
    "if", "else", "while", "for", "in",
    # Functions / output
    "bloom", "return", "new",
    # Boolean literals
    "petal", "wilted",   # true / false
    # Null
    "bare",              # null/None
    # Extra
    "and", "or", "not",
}


#  LEXER

class Token:
    def __init__(self, type_, value, line=0):
        self.type  = type_
        self.value = value
        self.line  = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos    = 0
        self.line   = 1
        self.tokens = []

    def peek(self, offset=0):
        i = self.pos + offset
        return self.source[i] if i < len(self.source) else None

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
        return ch

    def skip_whitespace(self):
        while self.pos < len(self.source) and self.peek() in (" ", "\t", "\r"):
            self.advance()

    def skip_comment(self):
        # # until end of line
        while self.pos < len(self.source) and self.peek() != "\n":
            self.advance()

    def read_string(self):
        quote = self.advance()  # consume opening quote
        s = ""
        while self.pos < len(self.source):
            ch = self.peek()
            if ch == "\\":
                self.advance()
                esc = self.advance()
                s += {"n": "\n", "t": "\t", "\\": "\\", '"': '"', "'": "'"}.get(esc, esc)
            elif ch == quote:
                self.advance()
                break
            else:
                s += self.advance()
        return s

    def read_number(self):
        num = ""
        is_float = False
        while self.pos < len(self.source) and (self.peek().isdigit() or (self.peek() == "." and not is_float)):
            if self.peek() == ".":
                is_float = True
            num += self.advance()
        return float(num) if is_float else int(num)

    def read_ident(self):
        ident = ""
        while self.pos < len(self.source) and (self.peek().isalnum() or self.peek() == "_"):
            ident += self.advance()
        return ident

    def tokenize(self):
        while self.pos < len(self.source):
            self.skip_whitespace()
            if self.pos >= len(self.source):
                break

            ch = self.peek()

            # Comments
            if ch == "#":
                self.skip_comment()
                continue

            # Newlines
            if ch == "\n":
                self.advance()
                self.tokens.append(Token(TT_NEWLINE, "\n", self.line))
                continue

            # Strings
            if ch in ('"', "'"):
                s = self.read_string()
                self.tokens.append(Token(TT_STRING, s, self.line))
                continue

            # Numbers
            if ch.isdigit() or (ch == "-" and self.peek(1) and self.peek(1).isdigit()
                                 and (not self.tokens or self.tokens[-1].type in
                                      (TT_ASSIGN, TT_OP, TT_LPAREN, TT_COMMA, TT_LBRACKET))):
                if ch == "-":
                    self.advance()
                    num = self.read_number()
                    if isinstance(num, float):
                        self.tokens.append(Token(TT_FLOAT, -num, self.line))
                    else:
                        self.tokens.append(Token(TT_INT, -num, self.line))
                else:
                    num = self.read_number()
                    tt = TT_FLOAT if isinstance(num, float) else TT_INT
                    self.tokens.append(Token(tt, num, self.line))
                continue

            # Identifiers / keywords
            if ch.isalpha() or ch == "_":
                ident = self.read_ident()
                if ident in ("petal", "wilted"):
                    self.tokens.append(Token(TT_BOOL, ident == "petal", self.line))
                elif ident == "bare":
                    self.tokens.append(Token(TT_KEYWORD, "bare", self.line))
                elif ident in KEYWORDS:
                    self.tokens.append(Token(TT_KEYWORD, ident, self.line))
                else:
                    self.tokens.append(Token(TT_IDENT, ident, self.line))
                continue

            # Two-char operators
            two = ch + (self.peek(1) or "")
            if two in ("==", "!=", "<=", ">=", "->"):
                self.advance(); self.advance()
                self.tokens.append(Token(TT_OP, two, self.line))
                continue

            # Single-char operators & punctuation
            single_map = {
                "=": TT_ASSIGN, "+": TT_OP, "-": TT_OP, "*": TT_OP,
                "/": TT_OP, "%": TT_OP, "<": TT_OP, ">": TT_OP,
                "(": TT_LPAREN, ")": TT_RPAREN,
                "{": TT_LBRACE,  "}": TT_RBRACE,
                "[": TT_LBRACKET, "]": TT_RBRACKET,
                ",": TT_COMMA, ".": TT_DOT, ":": TT_COLON,
            }
            if ch in single_map:
                self.tokens.append(Token(single_map[ch], ch, self.line))
                self.advance()
                continue

            raise LexerError(f"Line {self.line}: Unknown character {ch!r}")

        self.tokens.append(Token(TT_EOF, None, self.line))
        return self.tokens



#  AST NODES

class Node:
    pass

class ProgramNode(Node):
    def __init__(self, stmts): self.stmts = stmts

class VarDeclNode(Node):
    def __init__(self, type_, name, value): self.type_ = type_; self.name = name; self.value = value

class AssignNode(Node):
    def __init__(self, name, value): self.name = name; self.value = value

class BloomNode(Node):
    def __init__(self, expr): self.expr = expr

class ReturnNode(Node):
    def __init__(self, expr): self.expr = expr

class IfNode(Node):
    def __init__(self, cond, body, else_body): self.cond = cond; self.body = body; self.else_body = else_body

class WhileNode(Node):
    def __init__(self, cond, body): self.cond = cond; self.body = body

class ForNode(Node):
    def __init__(self, var, iterable, body): self.var = var; self.iterable = iterable; self.body = body

class GardenDefNode(Node):
    """Function definition: garden name(params) { body }"""
    def __init__(self, name, params, body): self.name = name; self.params = params; self.body = body

class CallNode(Node):
    def __init__(self, callee, args): self.callee = callee; self.args = args

class MethodCallNode(Node):
    def __init__(self, obj, method, args): self.obj = obj; self.method = method; self.args = args

class AttrAccessNode(Node):
    def __init__(self, obj, attr): self.obj = obj; self.attr = attr

class BinOpNode(Node):
    def __init__(self, left, op, right): self.left = left; self.op = op; self.right = right

class UnOpNode(Node):
    def __init__(self, op, operand): self.op = op; self.operand = operand

class LiteralNode(Node):
    def __init__(self, value): self.value = value

class IdentNode(Node):
    def __init__(self, name): self.name = name

class ListNode(Node):
    def __init__(self, elements): self.elements = elements

class NewNode(Node):
    def __init__(self, type_, args): self.type_ = type_; self.args = args

class IndexNode(Node):
    def __init__(self, obj, index): self.obj = obj; self.index = index

class IndexAssignNode(Node):
    def __init__(self, obj, index, value): self.obj = obj; self.index = index; self.value = value



#  PARSER

class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type != TT_NEWLINE]
        self.pos = 0

    def peek(self, offset=0):
        i = self.pos + offset
        return self.tokens[i] if i < len(self.tokens) else self.tokens[-1]

    def advance(self):
        t = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return t

    def expect(self, type_, value=None):
        t = self.advance()
        if t.type != type_:
            raise ParseError(f"Line {t.line}: Expected {type_} but got {t.type} ({t.value!r})")
        if value is not None and t.value != value:
            raise ParseError(f"Line {t.line}: Expected {value!r} but got {t.value!r}")
        return t

    def match(self, type_, value=None):
        t = self.peek()
        if t.type != type_:
            return False
        if value is not None and t.value != value:
            return False
        return True

    def consume(self, type_, value=None):
        if self.match(type_, value):
            return self.advance()
        return None

    # ── top level ──
    def parse(self):
        stmts = []
        while not self.match(TT_EOF):
            s = self.parse_statement()
            if s: stmts.append(s)
        return ProgramNode(stmts)

    def parse_block(self):
        self.expect(TT_LBRACE)
        stmts = []
        while not self.match(TT_RBRACE) and not self.match(TT_EOF):
            s = self.parse_statement()
            if s: stmts.append(s)
        self.expect(TT_RBRACE)
        return stmts

    def parse_statement(self):
        t = self.peek()

        # garden definition (function)  only if next token after name is LPAREN
        if t.type == TT_KEYWORD and t.value == "garden" and self.peek(1).type == TT_IDENT and self.peek(2).type == TT_LPAREN:
            return self.parse_garden_def()

        # type declaration  including garden as a type
        if t.type == TT_KEYWORD and t.value in ("rose", "tulip", "daisy", "lily", "bouquet", "garden"):
            return self.parse_var_decl()

        # bloom (print)
        if t.type == TT_KEYWORD and t.value == "bloom":
            self.advance()
            expr = self.parse_expr()
            return BloomNode(expr)

        # return
        if t.type == TT_KEYWORD and t.value == "return":
            self.advance()
            expr = self.parse_expr()
            return ReturnNode(expr)

        # if
        if t.type == TT_KEYWORD and t.value == "if":
            return self.parse_if()

        # while
        if t.type == TT_KEYWORD and t.value == "while":
            return self.parse_while()

        # for
        if t.type == TT_KEYWORD and t.value == "for":
            return self.parse_for()

        # assignment or expression statement
        if t.type == TT_IDENT:
            return self.parse_assign_or_expr()

        # skip stray tokens gracefully
        self.advance()
        return None

    def parse_garden_def(self):
        self.expect(TT_KEYWORD, "garden")
        name = self.expect(TT_IDENT).value
        self.expect(TT_LPAREN)
        params = []
        while not self.match(TT_RPAREN):
            # optional type annotation before param name
            if self.peek().type == TT_KEYWORD and self.peek().value in ("rose","tulip","daisy","lily","bouquet","garden"):
                self.advance()  # consume type
            params.append(self.expect(TT_IDENT).value)
            self.consume(TT_COMMA)
        self.expect(TT_RPAREN)
        body = self.parse_block()
        return GardenDefNode(name, params, body)

    def parse_var_decl(self):
        type_ = self.advance().value
        name  = self.expect(TT_IDENT).value
        value = None
        if self.consume(TT_ASSIGN):
            value = self.parse_expr()
        return VarDeclNode(type_, name, value)

    def parse_assign_or_expr(self):
        # Could be: ident = expr  OR  ident[i] = expr  OR  expr
        expr = self.parse_expr()
        if self.consume(TT_ASSIGN):
            value = self.parse_expr()
            if isinstance(expr, IdentNode):
                return AssignNode(expr.name, value)
            elif isinstance(expr, IndexNode):
                return IndexAssignNode(expr.obj, expr.index, value)
            else:
                raise ParseError("Invalid assignment target")
        return expr  # expression statement

    def parse_if(self):
        self.expect(TT_KEYWORD, "if")
        self.expect(TT_LPAREN)
        cond = self.parse_expr()
        self.expect(TT_RPAREN)
        body = self.parse_block()
        else_body = []
        if self.match(TT_KEYWORD, "else"):
            self.advance()
            if self.match(TT_KEYWORD, "if"):
                else_body = [self.parse_if()]
            else:
                else_body = self.parse_block()
        return IfNode(cond, body, else_body)

    def parse_while(self):
        self.expect(TT_KEYWORD, "while")
        self.expect(TT_LPAREN)
        cond = self.parse_expr()
        self.expect(TT_RPAREN)
        body = self.parse_block()
        return WhileNode(cond, body)

    def parse_for(self):
        self.expect(TT_KEYWORD, "for")
        self.expect(TT_LPAREN)
        var = self.expect(TT_IDENT).value
        self.expect(TT_KEYWORD, "in")
        iterable = self.parse_expr()
        self.expect(TT_RPAREN)
        body = self.parse_block()
        return ForNode(var, iterable, body)

    # ── expressions ──
    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.match(TT_KEYWORD, "or"):
            op = self.advance().value
            right = self.parse_and()
            left = BinOpNode(left, op, right)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.match(TT_KEYWORD, "and"):
            op = self.advance().value
            right = self.parse_not()
            left = BinOpNode(left, op, right)
        return left

    def parse_not(self):
        if self.match(TT_KEYWORD, "not"):
            op = self.advance().value
            return UnOpNode(op, self.parse_not())
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_additive()
        while self.peek().type == TT_OP and self.peek().value in ("==","!=","<",">","<=",">="):
            op = self.advance().value
            right = self.parse_additive()
            left = BinOpNode(left, op, right)
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.peek().type == TT_OP and self.peek().value in ("+", "-"):
            op = self.advance().value
            right = self.parse_multiplicative()
            left = BinOpNode(left, op, right)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.peek().type == TT_OP and self.peek().value in ("*", "/", "%"):
            op = self.advance().value
            right = self.parse_unary()
            left = BinOpNode(left, op, right)
        return left

    def parse_unary(self):
        if self.peek().type == TT_OP and self.peek().value == "-":
            op = self.advance().value
            return UnOpNode(op, self.parse_unary())
        return self.parse_postfix()

    def parse_postfix(self):
        expr = self.parse_primary()
        while True:
            if self.match(TT_DOT):
                self.advance()
                attr = self.expect(TT_IDENT).value
                if self.match(TT_LPAREN):
                    self.advance()
                    args = self.parse_args()
                    self.expect(TT_RPAREN)
                    expr = MethodCallNode(expr, attr, args)
                else:
                    expr = AttrAccessNode(expr, attr)
            elif self.match(TT_LBRACKET):
                self.advance()
                index = self.parse_expr()
                self.expect(TT_RBRACKET)
                expr = IndexNode(expr, index)
            elif self.match(TT_LPAREN) and isinstance(expr, IdentNode):
                self.advance()
                args = self.parse_args()
                self.expect(TT_RPAREN)
                expr = CallNode(expr.name, args)
            else:
                break
        return expr

    def parse_primary(self):
        t = self.peek()

        if t.type == TT_INT:    self.advance(); return LiteralNode(t.value)
        if t.type == TT_FLOAT:  self.advance(); return LiteralNode(t.value)
        if t.type == TT_STRING: self.advance(); return LiteralNode(t.value)
        if t.type == TT_BOOL:   self.advance(); return LiteralNode(t.value)

        if t.type == TT_KEYWORD and t.value == "bare":
            self.advance(); return LiteralNode(None)

        if t.type == TT_KEYWORD and t.value == "new":
            self.advance()
            type_ = self.advance().value
            self.expect(TT_LPAREN)
            args = self.parse_args()
            self.expect(TT_RPAREN)
            return NewNode(type_, args)

        if t.type == TT_LBRACKET:
            self.advance()
            elements = []
            while not self.match(TT_RBRACKET):
                elements.append(self.parse_expr())
                self.consume(TT_COMMA)
            self.expect(TT_RBRACKET)
            return ListNode(elements)

        if t.type == TT_LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.expect(TT_RPAREN)
            return expr

        if t.type == TT_IDENT:
            self.advance()
            return IdentNode(t.value)

        raise ParseError(f"Line {t.line}: Unexpected token {t.type} ({t.value!r})")

    def parse_args(self):
        args = []
        while not self.match(TT_RPAREN) and not self.match(TT_EOF):
            args.append(self.parse_expr())
            self.consume(TT_COMMA)
        return args


# ─────────────────────────────────────────────
#  RUNTIME VALUES
# ─────────────────────────────────────────────
class PetaliaFunction:
    def __init__(self, name, params, body, closure):
        self.name    = name
        self.params  = params
        self.body    = body
        self.closure = closure

    def __repr__(self):
        return f"<garden {self.name}>"


class BouquetObject:
    """A collection of (flower_type, label) pairs — the visual output object."""
    def __init__(self):
        self.flowers = []  # list of (flower_type: str, label: str)

    def add(self, flower_type, label=""):
        self.flowers.append((str(flower_type), str(label)))

    def render(self):
        lines = ["🌸 Bouquet:"]
        flower_emojis = {
            "rose": "🌹", "tulip": "🌷", "daisy": "🌼",
            "lily": "🌺", "orchid": "🌸", "sunflower": "🌻",
            "daffodil": "💐", "default": "🌿"
        }
        for ftype, label in self.flowers:
            emoji = flower_emojis.get(ftype.lower(), flower_emojis["default"])
            lines.append(f"  {emoji} [{ftype}] {label}")
        return "\n".join(lines)

    def __repr__(self):
        return self.render()


class GardenObject:
    """A full renderable scene — collection of bouquets/flowers."""
    def __init__(self):
        self.items = []  # list of (flower_type, label)

    def add(self, flower_type, label=""):
        self.items.append((str(flower_type), str(label)))

    def render(self):
        flower_emojis = {
            "rose": "🌹", "tulip": "🌷", "daisy": "🌼",
            "lily": "🌺", "orchid": "🌸", "sunflower": "🌻",
            "daffodil": "💐", "default": "🌿"
        }
        if not self.items:
            return "🌱 (empty garden)"
        cols = min(5, len(self.items))
        lines = [""]
        lines.append("┌─────────────────────────────────────┐")
        lines.append("│           🌻 PETALIA GARDEN 🌻         │")
        lines.append("├─────────────────────────────────────┤")
        row = []
        for ftype, label in self.items:
            emoji = flower_emojis.get(ftype.lower(), flower_emojis["default"])
            row.append(f"{emoji} {label}")
            if len(row) == cols:
                lines.append("│  " + "  ".join(f"{r:<8}" for r in row) + "│")
                row = []
        if row:
            lines.append("│  " + "  ".join(f"{r:<8}" for r in row) + "│")
        lines.append("└─────────────────────────────────────┘")
        return "\n".join(lines)

    def __repr__(self):
        return self.render()



#  ENVIRONMENT

class Environment:
    def __init__(self, parent=None):
        self.vars   = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Undefined variable: '{name}'")

    def set(self, name, value):
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent and self.parent.has(name):
            self.parent.set(name, value)
            return
        self.vars[name] = value

    def define(self, name, value):
        self.vars[name] = value

    def has(self, name):
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.has(name)
        return False



#  RETURN SIGNAL

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value



#  INTERPRETER / EVALUATOR

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self._setup_builtins()

    def _setup_builtins(self):
        # Built-in functions
        self.global_env.define("len",   lambda args: len(args[0]))
        self.global_env.define("str",   lambda args: str(args[0]))
        self.global_env.define("int",   lambda args: int(args[0]))
        self.global_env.define("float", lambda args: float(args[0]))
        self.global_env.define("range", lambda args: list(range(*[int(a) for a in args])))
        self.global_env.define("abs",   lambda args: abs(args[0]))
        self.global_env.define("max",   lambda args: max(args[0]) if len(args)==1 else max(args))
        self.global_env.define("min",   lambda args: min(args[0]) if len(args)==1 else min(args))
        self.global_env.define("sqrt",  lambda args: math.sqrt(args[0]))
        self.global_env.define("input", lambda args: input(args[0] if args else ""))

    def run(self, program: ProgramNode):
        self.exec_block(program.stmts, self.global_env)

    def exec_block(self, stmts, env):
        for stmt in stmts:
            self.exec_stmt(stmt, env)

    def exec_stmt(self, node, env):
        if node is None:
            return

        if isinstance(node, VarDeclNode):
            val = self.eval_expr(node.value, env) if node.value is not None else self._default(node.type_)
            env.define(node.name, val)

        elif isinstance(node, AssignNode):
            val = self.eval_expr(node.value, env)
            env.set(node.name, val)

        elif isinstance(node, IndexAssignNode):
            obj   = self.eval_expr(node.obj, env)
            index = self.eval_expr(node.index, env)
            val   = self.eval_expr(node.value, env)
            obj[index] = val

        elif isinstance(node, BloomNode):
            val = self.eval_expr(node.expr, env)
            self._bloom(val)

        elif isinstance(node, ReturnNode):
            val = self.eval_expr(node.expr, env)
            raise ReturnSignal(val)

        elif isinstance(node, IfNode):
            cond = self.eval_expr(node.cond, env)
            if self._truthy(cond):
                self.exec_block(node.body, Environment(env))
            elif node.else_body:
                self.exec_block(node.else_body, Environment(env))

        elif isinstance(node, WhileNode):
            while self._truthy(self.eval_expr(node.cond, env)):
                self.exec_block(node.body, Environment(env))

        elif isinstance(node, ForNode):
            iterable = self.eval_expr(node.iterable, env)
            for item in iterable:
                loop_env = Environment(env)
                loop_env.define(node.var, item)
                self.exec_block(node.body, loop_env)

        elif isinstance(node, GardenDefNode):
            fn = PetaliaFunction(node.name, node.params, node.body, env)
            env.define(node.name, fn)

        elif isinstance(node, (CallNode, MethodCallNode, BinOpNode, UnOpNode,
                               LiteralNode, IdentNode, NewNode, IndexNode)):
            self.eval_expr(node, env)  # expression statement

        else:
            pass  # ignore unknown nodes

    def _default(self, type_):
        defaults = {"rose": 0, "tulip": "", "daisy": False, "lily": [], "bouquet": BouquetObject(), "garden": GardenObject()}
        return defaults.get(type_, None)

    def _truthy(self, val):
        if val is None: return False
        if isinstance(val, bool): return val
        if isinstance(val, (int, float)): return val != 0
        if isinstance(val, str): return len(val) > 0
        if isinstance(val, list): return len(val) > 0
        return True

    def _bloom(self, val):
        """The bloom keyword: render visual output."""
        if isinstance(val, (BouquetObject, GardenObject)):
            print(val.render())
        elif isinstance(val, bool):
            print("🌸 petal" if val else "🥀 wilted")
        elif val is None:
            print("🌱 bare")
        else:
            print(f"🌷 {val}")

    def eval_expr(self, node, env):
        if isinstance(node, LiteralNode):
            return node.value

        if isinstance(node, IdentNode):
            val = env.get(node.name)
            if callable(val):
                return val  # builtin function reference
            return val

        if isinstance(node, ListNode):
            return [self.eval_expr(e, env) for e in node.elements]

        if isinstance(node, NewNode):
            if node.type_ == "bouquet":
                return BouquetObject()
            if node.type_ == "garden":
                return GardenObject()
            if node.type_ == "lily":
                return []
            raise RuntimeError(f"Unknown new type: {node.type_!r}")

        if isinstance(node, IndexNode):
            obj   = self.eval_expr(node.obj, env)
            index = self.eval_expr(node.index, env)
            return obj[index]

        if isinstance(node, BinOpNode):
            left  = self.eval_expr(node.left, env)
            right = self.eval_expr(node.right, env)
            op    = node.op
            if op == "+":
                if isinstance(left, list) and isinstance(right, list):
                    return left + right
                return left + right
            if op == "-":  return left - right
            if op == "*":  return left * right
            if op == "/":
                if right == 0: raise RuntimeError("Division by zero 🥀")
                return left / right
            if op == "%":  return left % right
            if op == "==": return left == right
            if op == "!=": return left != right
            if op == "<":  return left < right
            if op == ">":  return left > right
            if op == "<=": return left <= right
            if op == ">=": return left >= right
            if op == "and": return self._truthy(left) and self._truthy(right)
            if op == "or":  return self._truthy(left) or self._truthy(right)
            raise RuntimeError(f"Unknown operator: {op}")

        if isinstance(node, UnOpNode):
            val = self.eval_expr(node.operand, env)
            if node.op == "-":   return -val
            if node.op == "not": return not self._truthy(val)

        if isinstance(node, CallNode):
            fn   = env.get(node.callee)
            args = [self.eval_expr(a, env) for a in node.args]
            return self._call(fn, args, env)

        if isinstance(node, MethodCallNode):
            obj    = self.eval_expr(node.obj, env)
            args   = [self.eval_expr(a, env) for a in node.args]
            method = node.method
            return self._method_call(obj, method, args)

        if isinstance(node, AttrAccessNode):
            obj = self.eval_expr(node.obj, env)
            return self._attr_get(obj, node.attr)

        raise RuntimeError(f"Cannot evaluate node: {type(node).__name__}")

    def _call(self, fn, args, env):
        if callable(fn):
            return fn(args)
        if isinstance(fn, PetaliaFunction):
            fn_env = Environment(fn.closure)
            for param, arg in zip(fn.params, args):
                fn_env.define(param, arg)
            try:
                self.exec_block(fn.body, fn_env)
            except ReturnSignal as r:
                return r.value
            return None
        raise RuntimeError(f"Not callable: {fn!r}")

    def _method_call(self, obj, method, args):
        # List / lily methods
        if isinstance(obj, list):
            if method == "add":    obj.append(args[0]); return None
            if method == "append": obj.append(args[0]); return None
            if method == "remove": obj.remove(args[0]); return None
            if method == "pop":    return obj.pop(int(args[0]) if args else -1)
            if method == "len":    return len(obj)
            if method == "get":    return obj[int(args[0])]
            if method == "set":    obj[int(args[0])] = args[1]; return None
            if method == "contains": return args[0] in obj
            if method == "join":   return str(args[0]).join(str(x) for x in obj)

        # Bouquet methods
        if isinstance(obj, BouquetObject):
            if method == "add":
                ftype = args[0] if args else "rose"
                label = args[1] if len(args) > 1 else ""
                obj.add(ftype, label); return None
            if method == "render": return obj.render()
            if method == "size":   return len(obj.flowers)

        # Garden methods
        if isinstance(obj, GardenObject):
            if method == "add":
                ftype = args[0] if args else "rose"
                label = args[1] if len(args) > 1 else ""
                obj.add(ftype, label); return None
            if method == "render": return obj.render()
            if method == "size":   return len(obj.items)

        # String methods
        if isinstance(obj, str):
            if method == "upper":   return obj.upper()
            if method == "lower":   return obj.lower()
            if method == "length":  return len(obj)
            if method == "split":   return obj.split(args[0] if args else " ")
            if method == "contains": return args[0] in obj
            if method == "replace": return obj.replace(args[0], args[1])

        raise RuntimeError(f"Unknown method '{method}' on {type(obj).__name__}")

    def _attr_get(self, obj, attr):
        if isinstance(obj, list):
            if attr == "length": return len(obj)
        if isinstance(obj, (BouquetObject, GardenObject)):
            if attr == "size": return len(obj.flowers if isinstance(obj, BouquetObject) else obj.items)
        if isinstance(obj, str):
            if attr == "length": return len(obj)
        raise RuntimeError(f"Unknown attribute '{attr}' on {type(obj).__name__}")



#  ENTRY POINT

def run_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    run_source(source, filename=path)

def run_source(source: str, filename="<stdin>"):
    try:
        lexer  = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast    = parser.parse()
        interp = Interpreter()
        interp.run(ast)
    except LexerError as e:
        print(f"🥀 Lexer Error in {filename}: {e}", file=sys.stderr)
        sys.exit(1)
    except ParseError as e:
        print(f"🥀 Parse Error in {filename}: {e}", file=sys.stderr)
        sys.exit(1)
    except ReturnSignal:
        pass
    except (RuntimeError, NameError, TypeError, IndexError, KeyError) as e:
        print(f"🥀 Runtime Error in {filename}: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py <file.petal>")
        print("       python interpreter.py --demo")
        sys.exit(1)

    if sys.argv[1] == "--demo":
        import os
        demo_dir = os.path.join(os.path.dirname(__file__), "programs")
        for fname in sorted(os.listdir(demo_dir)):
            if fname.endswith(".petal"):
                print(f"\n{'═'*50}")
                print(f"  Running: {fname}")
                print(f"{'═'*50}")
                run_file(os.path.join(demo_dir, fname))
        return

    run_file(sys.argv[1])

if __name__ == "__main__":
    main()
