"""
Analizador léxico (scanner) de Chimpan-C.

Estrategia:
  1. Cada categoría léxica se describe con una expresión regular.
  2. Todas se combinan en una sola expresión maestra con grupos con nombre
     (?P<NOMBRE>patrón). El orden importa: en cada posición gana la primera
     alternativa que coincide, por eso los patrones más específicos van primero
     (comentarios antes que '/', flotantes antes que enteros, etc.).
  3. Se recorre el código fuente de izquierda a derecha con re.match en la
     posición actual (principio de "máxima coincidencia" por patrón).
  4. Las palabras reservadas se reconocen como identificadores y luego se
     buscan en la tabla KEYWORDS.
  5. Los errores no detienen el análisis: se registran y el scanner continúa
     desde el siguiente carácter (recuperación en "modo pánico").
"""

import re

from .errors import LexicalError
from .tokens import DELIMITERS, KEYWORDS, OPERATORS, Token, TokenType

MAX_IDENT_LENGTH = 31
MAX_INT = 2**31 - 1
VALID_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}

# Especificación de tokens: (nombre del grupo, expresión regular)
TOKEN_SPEC = [
    ("BLOCK_COMMENT",    r"/\*[\s\S]*?\*/"),
    ("UNCLOSED_COMMENT", r"/\*[\s\S]*"),
    ("LINE_COMMENT",     r"//[^\n]*"),
    ("NEWLINE",          r"\n"),
    ("SKIP",             r"[ \t\r\f]+"),
    ("FLOAT_LIT",        r"\d+\.\d+(?![\w.])"),
    ("INT_LIT",          r"\d+(?![\w.])"),
    ("BAD_NUMBER",       r"\d[\w.]*"),
    ("STRING_LIT",       r'"(?:[^"\\\n]|\\.)*"'),
    ("UNCLOSED_STRING",  r'"[^\n]*'),
    ("IDENT",            r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OPERATOR",         r"==|!=|<=|>=|&&|\|\||[+\-*/%<>!=]"),
    ("DELIMITER",        r"[(){},;]"),
    ("MISMATCH",         r"."),
]

MASTER_PATTERN = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))

# Sugerencias para caracteres inválidos comunes
HINTS = {
    "&": "¿Quisiste escribir '&&'?",
    "|": "¿Quisiste escribir '||'?",
    "'": "Las cadenas en Chimpan-C usan comillas dobles (\").",
    "#": "Los comentarios en Chimpan-C usan // o /* */.",
}


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.errors: list[LexicalError] = []
        self.line = 1
        self.line_start = 0  # índice del primer carácter de la línea actual

    def tokenize(self) -> tuple[list[Token], list[LexicalError]]:
        pos = 0
        while pos < len(self.source):
            match = MASTER_PATTERN.match(self.source, pos)
            kind = match.lastgroup
            lexeme = match.group()
            column = pos - self.line_start + 1
            self._handle(kind, lexeme, column)
            self._advance_lines(lexeme, pos)
            pos = match.end()

        eof_column = len(self.source) - self.line_start + 1
        self.tokens.append(Token(TokenType.EOF, "", None, self.line, eof_column))
        return self.tokens, self.errors

    # ------------------------------------------------------------------
    def _handle(self, kind: str, lexeme: str, column: int) -> None:
        if kind in ("SKIP", "NEWLINE", "LINE_COMMENT", "BLOCK_COMMENT"):
            return
        if kind == "IDENT":
            self._identifier(lexeme, column)
        elif kind == "INT_LIT":
            self._integer(lexeme, column)
        elif kind == "FLOAT_LIT":
            self._add(TokenType.FLOAT_LIT, lexeme, float(lexeme), column)
        elif kind == "STRING_LIT":
            self._string(lexeme, column)
        elif kind == "OPERATOR":
            self._add(OPERATORS[lexeme], lexeme, None, column)
        elif kind == "DELIMITER":
            self._add(DELIMITERS[lexeme], lexeme, None, column)
        elif kind == "BAD_NUMBER":
            self._error("LEX004", f"'{lexeme}' no es un número válido.", lexeme, column)
        elif kind == "UNCLOSED_STRING":
            self._error("LEX002", "Falta la comilla de cierre (\") antes del fin de línea.",
                        lexeme, column)
        elif kind == "UNCLOSED_COMMENT":
            self._error("LEX003", "Falta '*/' para cerrar el comentario.", lexeme[:2], column)
        elif kind == "MISMATCH":
            hint = HINTS.get(lexeme, "")
            if not lexeme.isascii():
                hint = "Fuera de cadenas solo se permiten caracteres ASCII (sin acentos ni ñ)."
            self._error("LEX001", f"'{lexeme}' no pertenece al alfabeto de Chimpan-C. {hint}".strip(),
                        lexeme, column)

    def _identifier(self, lexeme: str, column: int) -> None:
        if lexeme in KEYWORDS:
            token_type = KEYWORDS[lexeme]
            value = {"true": True, "false": False}.get(lexeme)
            self._add(token_type, lexeme, value, column)
        elif len(lexeme) > MAX_IDENT_LENGTH:
            self._error("LEX005", f"'{lexeme[:12]}...' tiene {len(lexeme)} caracteres "
                        f"(máximo {MAX_IDENT_LENGTH}).", lexeme, column)
        else:
            self._add(TokenType.IDENT, lexeme, None, column)

    def _integer(self, lexeme: str, column: int) -> None:
        value = int(lexeme)
        if value > MAX_INT:
            self._error("LEX006", f"{lexeme} excede el máximo permitido ({MAX_INT}).", lexeme, column)
        else:
            self._add(TokenType.INT_LIT, lexeme, value, column)

    def _string(self, lexeme: str, column: int) -> None:
        # Se interpreta el contenido entre comillas resolviendo secuencias de escape
        content = lexeme[1:-1]
        value = []
        i = 0
        while i < len(content):
            char = content[i]
            if char == "\\":
                escape = content[i + 1]
                if escape in VALID_ESCAPES:
                    value.append(VALID_ESCAPES[escape])
                else:
                    self._error("LEX007", f"'\\{escape}' no es un escape válido "
                                "(se permiten \\n \\t \\r \\\" \\\\).",
                                f"\\{escape}", column + 1 + i)
                    value.append(escape)
                i += 2
            else:
                value.append(char)
                i += 1
        self._add(TokenType.STRING_LIT, lexeme, "".join(value), column)

    # ------------------------------------------------------------------
    def _add(self, token_type: TokenType, lexeme: str, value, column: int) -> None:
        self.tokens.append(Token(token_type, lexeme, value, self.line, column))

    def _error(self, code: str, message: str, lexeme: str, column: int) -> None:
        self.errors.append(LexicalError(code, message, lexeme, self.line, column))

    def _advance_lines(self, lexeme: str, start: int) -> None:
        # Actualiza el contador de líneas (los comentarios de bloque pueden abarcar varias)
        newlines = lexeme.count("\n")
        if newlines:
            self.line += newlines
            self.line_start = start + lexeme.rindex("\n") + 1


def tokenize(source: str) -> tuple[list[Token], list[LexicalError]]:
    """Atajo: analiza `source` y regresa (tokens, errores)."""
    return Lexer(source).tokenize()
