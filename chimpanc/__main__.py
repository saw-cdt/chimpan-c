"""
Interfaz de línea de comandos de Chimpan-C.

Uso:
    python -m chimpanc programa.chc            # tabla de tokens
    python -m chimpanc programa.chc --json     # tokens en formato JSON
"""

import argparse
import json
import sys

from .lexer import tokenize


def print_table(tokens) -> None:
    print(f"{'#':>4}  {'LÍNEA:COL':<10} {'TIPO':<12} {'LEXEMA':<22} VALOR")
    print("-" * 66)
    for i, tok in enumerate(tokens, start=1):
        position = f"{tok.line}:{tok.column}"
        value = "" if tok.value is None else repr(tok.value)
        print(f"{i:>4}  {position:<10} {tok.type.name:<12} {tok.lexeme:<22} {value}")


def main() -> int:
    parser = argparse.ArgumentParser(prog="chimpanc", description="Analizador léxico de Chimpan-C")
    parser.add_argument("file", help="archivo fuente .chc")
    parser.add_argument("--json", action="store_true", help="imprime los tokens en JSON")
    args = parser.parse_args()

    with open(args.file, encoding="utf-8") as f:
        source = f.read()

    tokens, errors = tokenize(source)

    if args.json:
        data = [{"type": t.type.name, "lexeme": t.lexeme, "value": t.value,
                 "line": t.line, "column": t.column} for t in tokens]
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_table(tokens)
        print(f"\nTotal de tokens: {len(tokens)}")

    if errors:
        print(f"\n{len(errors)} error(es) léxico(s):", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1
    print("Análisis léxico completado sin errores.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
