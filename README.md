# Chimpan-C

Compilador educativo de un lenguaje simple estilo C con temática de chango.
Proyecto Integrador Académico — Compiladores AD2026.

## Requisitos

- Python 3.10 o superior (no requiere librerías externas)

## Uso

```bash
# Tabla de tokens de un programa
python -m chimpanc examples/valid/factorial.chc

# Tokens en formato JSON
python -m chimpanc examples/valid/factorial.chc --json

# Ejemplo con errores léxicos
python -m chimpanc examples/invalid/lexical/invalid_chars.chc

# Pruebas
python -m unittest -v
```

## Palabras clave temáticas

| Chimpan-C | Equivale a |
|----------|------------|
| `banan`  | `var` (declaración de variable) |
| `jungle` | `main` (bloque principal) |
| `throw`  | `return` |
| `grab`   | `input` (lectura) |

## Estructura

```
chimpanc/
  tokens.py     Tipos de token y tablas de palabras reservadas/operadores
  errors.py     Catálogo de errores léxicos (LEX001–LEX007)
  lexer.py      Analizador léxico basado en expresiones regulares
  __main__.py   Interfaz de línea de comandos
examples/
  valid/                 Programas correctos
  invalid/lexical/       Programas con errores léxicos
  invalid/syntax/        Errores sintácticos (detectados en semana 3)
  invalid/semantic/      Errores semánticos (detectados en semana 4)
tests/
  test_lexer.py Pruebas de tokenización (unittest)
```

## Avance

- [x] Semana 1 — Definición del lenguaje y planeación
- [x] Semana 2 — Análisis léxico
- [ ] Semana 3 — Análisis sintáctico (parser + AST)
- [ ] Semana 4 — Análisis semántico (tabla de símbolos, tipos)
- [ ] Semana 5 — Código intermedio (TAC) y optimización
