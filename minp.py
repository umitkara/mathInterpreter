from dataclasses import dataclass
from enum import Enum
from typing import Generator
import sys, os, math

WHITESPACE = ' \t\n'

class TokenTypes(Enum):
    NUMBER = 1
    PLUS = 2
    MINUS = 3
    MULTIPLY = 4
    DIVIDE = 5
    LPAREN = 6
    RPAREN = 7
    POW = 8
    MOD = 9
    SIN = 10
    COS = 11
    TAN = 12
    COT = 13
    
class NodeTypes(Enum):
    NUMBER = 1
    PLUS = 2
    MINUS = 3
    MULTIPLY = 4
    DIVIDE = 5
    SIGN_PLUS = 6
    SIGN_MINUS = 7
    POW = 8
    MOD = 9
    SIN = 10
    COS = 11
    TAN = 12
    COT = 13

@dataclass
class Token:
    type: TokenTypes
    value: any = None
    
    def __repr__(self):
        return f'{self.type.name}:{self.value}' if self.value != None else self.type.name

class Node:
    def __init__(self, node_type: NodeTypes, **kwargs):
        self.node_type = node_type
        if self.node_type == NodeTypes.NUMBER:
            self.value = kwargs.get("value")
        elif self.node_type == NodeTypes.PLUS:
            self.sign = "+"
            self.left = kwargs.get("left")
            self.right = kwargs.get("right")
        elif self.node_type == NodeTypes.MINUS:
            self.sign = "-"
            self.left = kwargs.get("left")
            self.right = kwargs.get("right")
        elif self.node_type == NodeTypes.MULTIPLY:
            self.sign = "*"
            self.left = kwargs.get("left")
            self.right = kwargs.get("right")
        elif self.node_type == NodeTypes.DIVIDE:
            self.sign = "/"
            self.left = kwargs.get("left")
            self.right = kwargs.get("right")
        elif self.node_type == NodeTypes.SIGN_PLUS:
            self.sign = "+"
            self.value = kwargs.get("value")
        elif self.node_type == NodeTypes.SIGN_MINUS:
            self.sign = "-"
            self.value = kwargs.get("value")
        elif self.node_type == NodeTypes.POW:
            self.sign = "^"
            self.left = kwargs.get("left")
            self.right = kwargs.get("right")
        elif self.node_type == NodeTypes.MOD:
            self.sign = "%"
            self.left = kwargs.get("left")
            self.right = kwargs.get("right")
        elif self.node_type == NodeTypes.SIN:
            self.sign = "sin"
            self.value = kwargs.get("value")
        elif self.node_type == NodeTypes.COS:
            self.sign = "cos"
            self.value = kwargs.get("value")
        elif self.node_type == NodeTypes.TAN:
            self.sign = "tan"
            self.value = kwargs.get("value")
        elif self.node_type == NodeTypes.COT:
            self.sign = "cot"
            self.value = kwargs.get("value")
    def __repr__(self):
        if self.node_type == NodeTypes.NUMBER:
            return f'{self.value}'
        elif self.node_type in (NodeTypes.PLUS, NodeTypes.MINUS, NodeTypes.MULTIPLY, NodeTypes.DIVIDE, NodeTypes.MOD):
            return f'({self.left} {self.sign} {self.right})'
        elif self.node_type in (NodeTypes.SIGN_PLUS, NodeTypes.SIGN_MINUS):
            return f'({self.sign}{self.value})'
        elif self.node_type == NodeTypes.POW:
            return f'({self.left}){self.sign}({self.right})'
        elif self.node_type in (NodeTypes.SIN, NodeTypes.COS, NodeTypes.TAN, NodeTypes.COT):
            return f'{self.sign}({self.value})'
        else:
            raise Exception("Invalid expression")

class Lexer:
    def __init__(self, expression:str):
        self.expression = iter(expression)
        self._advance()
    def _advance(self):
        try:
            self.current = next(self.expression)
        except StopIteration:
            self.current = None
    
    def generate_tokens(self) -> Generator[Token, None, None]:
        while self.current != None:
            if self.current in WHITESPACE:
                self._advance()
            elif self.current == "." or self.current.isdigit():
                yield self._generate_number_token()
            elif self.current == "+":
                self._advance()
                yield Token(TokenTypes.PLUS)
            elif self.current == "-":
                self._advance()
                yield Token(TokenTypes.MINUS)
            elif self.current == "*":
                self._advance()
                yield Token(TokenTypes.MULTIPLY)
            elif self.current == "/":
                self._advance()
                yield Token(TokenTypes.DIVIDE)
            elif self.current == "(":
                self._advance()
                yield Token(TokenTypes.LPAREN)
            elif self.current == ")":
                self._advance()
                yield Token(TokenTypes.RPAREN)
            elif self.current == "^":
                self._advance()
                yield Token(TokenTypes.POW)
            elif self.current == "%":
                self._advance()
                yield Token(TokenTypes.MOD)
            elif self.current.isalpha():
                f = self.current
                self._advance()
                while self.current != None and self.current.isalpha():
                    f += self.current
                    self._advance()
                if f == "sin":
                    yield Token(TokenTypes.SIN)
                elif f == "cos":
                    yield Token(TokenTypes.COS)
                elif f == "tan":
                    yield Token(TokenTypes.TAN)
                elif f == "cot":
                    yield Token(TokenTypes.COT)
                else:
                    raise Exception("Invalid expression")
            else:
                raise Exception("Invalid expression")
    
    def _generate_number_token(self)->Token:
        fp_count = 0
        num = self.current
        self._advance()
        while self.current != None and (self.current.isdigit() or self.current == "."):
            if self.current == ".":
                fp_count += 1
                if fp_count > 1:
                    raise Exception("Invalid number")
            num += self.current
            self._advance()
        if num.startswith("."):
            num = "0" + num
        elif num.endswith("."):
            num += "0"
        if float(num).is_integer():
            return Token(TokenTypes.NUMBER, int(num))
        return Token(TokenTypes.NUMBER, float(num))

class Parser:
    def __init__(self, tokens:Generator[Token, None, None]):
        self.tokens = iter(tokens)
        self._advance()
    def _advance(self):
        try:
            self.current_token = next(self.tokens)
        except StopIteration:
            self.current_token = None    
    def parse(self):
        if self.current_token == None:
            return None
        result = self._expr_rule()
        if self.current_token != None:
            raise Exception("Invalid expression")
        return result
    def _expr_rule(self)->Node:
        result = self._term_rule()
        while self.current_token != None and self.current_token.type in [TokenTypes.PLUS, TokenTypes.MINUS]:
            if self.current_token.type == TokenTypes.PLUS:
                self._advance()
                result = Node(NodeTypes.PLUS, left=result, right=self._term_rule())
            elif self.current_token.type == TokenTypes.MINUS:
                self._advance()
                result = Node(NodeTypes.MINUS, left=result, right=self._term_rule())    
        return result
    def _term_rule(self)->Node:
        result = self._factor_rule()
        while self.current_token != None and self.current_token.type in [TokenTypes.MULTIPLY, TokenTypes.DIVIDE, TokenTypes.POW, TokenTypes.MOD]:
            if self.current_token.type == TokenTypes.POW:
                self._advance()
                result = Node(NodeTypes.POW, left=result, right=self._factor_rule())
            elif self.current_token.type == TokenTypes.MULTIPLY:
                self._advance()
                result = Node(NodeTypes.MULTIPLY, left=result, right=self._factor_rule())
            elif self.current_token.type == TokenTypes.DIVIDE:
                self._advance()
                result = Node(NodeTypes.DIVIDE, left=result, right=self._factor_rule())
            elif self.current_token.type == TokenTypes.MOD:
                self._advance()
                result = Node(NodeTypes.MOD, left=result, right=self._factor_rule())
        return result
    def _factor_rule(self)->Node:
        tok = self.current_token
        if tok.type == TokenTypes.LPAREN:
            self._advance()
            result = self._expr_rule()
            if self.current_token.type != TokenTypes.RPAREN:
                raise Exception("Invalid expression")
            self._advance()
            return result
        elif tok.type == TokenTypes.NUMBER:
            self._advance()
            return Node(NodeTypes.NUMBER, value=tok.value)
        elif tok.type == TokenTypes.PLUS:
            self._advance()
            return Node(NodeTypes.SIGN_PLUS, value=self._factor_rule())
        elif tok.type == TokenTypes.MINUS:
            self._advance()
            return Node(NodeTypes.SIGN_MINUS, value=self._factor_rule())
        elif tok.type == TokenTypes.SIN:
            self._advance()
            if self.current_token.type != TokenTypes.LPAREN:
                raise Exception("Invalid expression")
            self._advance()
            result = self._expr_rule()
            if self.current_token.type != TokenTypes.RPAREN:
                raise Exception("Invalid expression")
            self._advance()
            return Node(NodeTypes.SIN, value=result)
        elif tok.type == TokenTypes.COS:
            self._advance()
            if self.current_token.type != TokenTypes.LPAREN:
                raise Exception("Invalid expression")
            self._advance()
            result = self._expr_rule()
            if self.current_token.type != TokenTypes.RPAREN:
                raise Exception("Invalid expression")
            self._advance()
            return Node(NodeTypes.COS, value=result)
        elif tok.type == TokenTypes.TAN:
            self._advance()
            if self.current_token.type != TokenTypes.LPAREN:
                raise Exception("Invalid expression")
            self._advance()
            result = self._expr_rule()
            if self.current_token.type != TokenTypes.RPAREN:
                raise Exception("Invalid expression")
            self._advance()
            return Node(NodeTypes.TAN, value=result)
        elif tok.type == TokenTypes.COT:
            self._advance()
            if self.current_token.type != TokenTypes.LPAREN:
                raise Exception("Invalid expression")
            self._advance()
            result = self._expr_rule()
            if self.current_token.type != TokenTypes.RPAREN:
                raise Exception("Invalid expression")
            self._advance()
            return Node(NodeTypes.COT, value=result)

class Interpreter:
    def visit(self, Node:Node):
        func = getattr(self, f"visit_{Node.node_type.name}")
        return func(Node)
    def visit_NUMBER(self, Node:Node):
        return Node.value
    def visit_PLUS(self, Node:Node):
        return self.visit(Node.left) + self.visit(Node.right)
    def visit_MINUS(self, Node:Node):
        return self.visit(Node.left) - self.visit(Node.right)
    def visit_MULTIPLY(self, Node:Node):
        return self.visit(Node.left) * self.visit(Node.right)
    def visit_DIVIDE(self, Node:Node):
        try:
            d:float = self.visit(Node.left) / self.visit(Node.right)
            return int(d) if d.is_integer() else d
        except ZeroDivisionError:
            return float("inf")
        except:
            raise Exception("Invalid expression")
    def visit_SIGN_PLUS(self, Node:Node):
        return self.visit(Node.value)
    def visit_SIGN_MINUS(self, Node:Node):
        return -self.visit(Node.value)
    def visit_POW(self, Node:Node):
        return self.visit(Node.left) ** self.visit(Node.right)
    def visit_MOD(self, Node:Node):
        return self.visit(Node.left) % self.visit(Node.right)
    def visit_SIN(self, Node:Node):
        return math.sin(math.radians(self.visit(Node.value)))
    def visit_COS(self, Node:Node):
        return math.cos(math.radians(self.visit(Node.value)))
    def visit_TAN(self, Node:Node):
        return math.tan(math.radians(self.visit(Node.value)))
    def visit_COT(self, Node:Node):
        return 1 / math.tan(math.radians(self.visit(Node.value)))
    
if __name__ == "__main__":
    while True:
        try:
            exp = input("Minp > ")
            if exp == "exit" or exp == "quit" or exp == "close":
                exit(0)
            if exp == "clear" or exp == "cls":
                os.system("cls")
                continue
            tokens = list(Lexer(exp).generate_tokens())
            tree = Parser(tokens).parse()
            value = Interpreter().visit(tree)
            print(value)
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            print(f"{e} at line {exception_traceback.tb_lineno}")