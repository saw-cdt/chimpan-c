"""
Definición de tokens del lenguaje Chimpan-C.

Contiene:
  - TokenType: enumeración de todas las categorías léxicas.
  - KEYWORDS: tabla de palabras reservadas (lexema -> tipo de token).
  - OPERATORS / DELIMITERS: tablas de símbolos (lexema -> tipo de token).
  - Token: estructura que representa un token reconocido por el scanner.
"""

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # --- Palabras reservadas temáticas de Chimpan-C ---
    BANAN = auto()      # declaración de variable   (equivale a "var")
    JUNGLE = auto()     # bloque principal           (equivale a "main")
    THROW = auto()      # retorno de función         (equivale a "return")
    GRAB = auto()       # lectura de entrada         (equivale a "input")

    # --- Palabras reservadas estándar ---
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    BREAK = auto()
    CONTINUE = auto()
    PRINT = auto()

    # --- Tipos de dato ---
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    STRING = auto()
    VOID = auto()

    # --- Literales ---
    INT_LIT = auto()
    FLOAT_LIT = auto()
    STRING_LIT = auto()
    TRUE = auto()
    FALSE = auto()

    # --- Identificadores ---
    IDENT = auto()

    # --- Operadores aritméticos ---
    PLUS = auto()       # +
    MINUS = auto()      # -
    STAR = auto()       # *
    SLASH = auto()      # /
    PERCENT = auto()    # %

    # --- Operadores relacionales ---
    EQ = auto()         # ==
    NEQ = auto()        # !=
    LT = auto()         # <
    LTE = auto()        # <=
    GT = auto()         # >
    GTE = auto()        # >=

    # --- Operadores lógicos ---
    AND = auto()        # &&
    OR = auto()         # ||
    NOT = auto()        # !

    # --- Asignación ---
    ASSIGN = auto()     # =

    # --- Delimitadores ---
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    COMMA = auto()      # ,
    SEMICOLON = auto()  # ;

    # --- Fin de archivo ---
    EOF = auto()


KEYWORDS = {
    "banan": TokenType.BANAN,
    "jungle": TokenType.JUNGLE,
    "throw": TokenType.THROW,
    "grab": TokenType.GRAB,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "print": TokenType.PRINT,
    "int": TokenType.INT,
    "float": TokenType.FLOAT,
    "bool": TokenType.BOOL,
    "string": TokenType.STRING,
    "void": TokenType.VOID,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}

OPERATORS = {
    "==": TokenType.EQ,
    "!=": TokenType.NEQ,
    "<=": TokenType.LTE,
    ">=": TokenType.GTE,
    "&&": TokenType.AND,
    "||": TokenType.OR,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "%": TokenType.PERCENT,
    "<": TokenType.LT,
    ">": TokenType.GT,
    "!": TokenType.NOT,
    "=": TokenType.ASSIGN,
}

DELIMITERS = {
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    ",": TokenType.COMMA,
    ";": TokenType.SEMICOLON,
}


@dataclass(frozen=True)
class Token:
    """Unidad léxica reconocida por el analizador léxico."""

    type: TokenType
    lexeme: str      # texto exacto tal como aparece en el código fuente
    value: object    # valor interpretado (int, float, str, bool) o None
    line: int        # línea donde inicia el token (base 1)
    column: int      # columna donde inicia el token (base 1)

    def __str__(self) -> str:
        return f"<{self.type.name}, '{self.lexeme}', {self.line}:{self.column}>"
