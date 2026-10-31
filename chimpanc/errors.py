"""
Errores léxicos del compilador Chimpan-C.

Cada error tiene un código único (LEXnnn) para poder documentarlo y probarlo.
"""

from dataclasses import dataclass

# Catálogo de errores léxicos: código -> descripción general
LEXICAL_ERRORS = {
    "LEX001": "Carácter inválido",
    "LEX002": "Cadena sin cerrar",
    "LEX003": "Comentario de bloque sin cerrar",
    "LEX004": "Número mal formado",
    "LEX005": "Identificador demasiado largo",
    "LEX006": "Entero fuera de rango",
    "LEX007": "Secuencia de escape inválida",
}


@dataclass(frozen=True)
class LexicalError:
    """Error detectado durante el análisis léxico."""

    code: str
    message: str
    lexeme: str
    line: int
    column: int

    def __str__(self) -> str:
        title = LEXICAL_ERRORS[self.code]
        return (f"Error léxico [{self.code}] línea {self.line}, columna {self.column}: "
                f"{title}. {self.message}")
