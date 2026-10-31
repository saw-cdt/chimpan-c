"""
Pruebas de tokenización del analizador léxico de Chimpan-C.

Ejecutar desde la raíz del proyecto:
    python -m unittest -v
"""

import unittest
from pathlib import Path

from chimpanc import TokenType as T
from chimpanc import tokenize

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def types(source):
    tokens, _ = tokenize(source)
    return [t.type for t in tokens]


def error_codes(source):
    _, errors = tokenize(source)
    return [e.code for e in errors]


class TestKeywordsAndIdentifiers(unittest.TestCase):
    def test_themed_keywords(self):
        self.assertEqual(types("banan jungle throw grab"),
                         [T.BANAN, T.JUNGLE, T.THROW, T.GRAB, T.EOF])

    def test_standard_keywords(self):
        self.assertEqual(types("if else while break continue print"),
                         [T.IF, T.ELSE, T.WHILE, T.BREAK, T.CONTINUE, T.PRINT, T.EOF])

    def test_types(self):
        self.assertEqual(types("int float bool string void"),
                         [T.INT, T.FLOAT, T.BOOL, T.STRING, T.VOID, T.EOF])

    def test_identifiers(self):
        tokens, errors = tokenize("monkey _tmp x1 bananan")
        self.assertEqual([t.type for t in tokens[:-1]], [T.IDENT] * 4)
        self.assertEqual(errors, [])

    def test_keyword_prefix_is_identifier(self):
        # "banana" empieza con "banan" pero es un identificador (máxima coincidencia)
        self.assertEqual(types("banana"), [T.IDENT, T.EOF])

    def test_keywords_are_case_sensitive(self):
        self.assertEqual(types("Banan IF"), [T.IDENT, T.IDENT, T.EOF])


class TestLiterals(unittest.TestCase):
    def test_integer(self):
        tokens, _ = tokenize("42")
        self.assertEqual((tokens[0].type, tokens[0].value), (T.INT_LIT, 42))

    def test_float(self):
        tokens, _ = tokenize("3.14")
        self.assertEqual((tokens[0].type, tokens[0].value), (T.FLOAT_LIT, 3.14))

    def test_booleans(self):
        tokens, _ = tokenize("true false")
        self.assertEqual([(t.type, t.value) for t in tokens[:2]],
                         [(T.TRUE, True), (T.FALSE, False)])

    def test_string_with_escapes(self):
        tokens, errors = tokenize(r'"hola\n\t\"chango\"\\"')
        self.assertEqual(tokens[0].type, T.STRING_LIT)
        self.assertEqual(tokens[0].value, 'hola\n\t"chango"\\')
        self.assertEqual(errors, [])

    def test_empty_string(self):
        tokens, _ = tokenize('""')
        self.assertEqual((tokens[0].type, tokens[0].value), (T.STRING_LIT, ""))


class TestOperatorsAndDelimiters(unittest.TestCase):
    def test_two_char_operators_win(self):
        self.assertEqual(types("== != <= >= && ||"),
                         [T.EQ, T.NEQ, T.LTE, T.GTE, T.AND, T.OR, T.EOF])

    def test_single_char_operators(self):
        self.assertEqual(types("+ - * / % < > ! ="),
                         [T.PLUS, T.MINUS, T.STAR, T.SLASH, T.PERCENT,
                          T.LT, T.GT, T.NOT, T.ASSIGN, T.EOF])

    def test_no_spaces_needed(self):
        self.assertEqual(types("x<=10&&!y"),
                         [T.IDENT, T.LTE, T.INT_LIT, T.AND, T.NOT, T.IDENT, T.EOF])

    def test_delimiters(self):
        self.assertEqual(types("( ) { } , ;"),
                         [T.LPAREN, T.RPAREN, T.LBRACE, T.RBRACE, T.COMMA, T.SEMICOLON, T.EOF])


class TestCommentsAndPositions(unittest.TestCase):
    def test_line_comment_ignored(self):
        self.assertEqual(types("x // comentario\ny"), [T.IDENT, T.IDENT, T.EOF])

    def test_block_comment_multiline(self):
        tokens, _ = tokenize("a /* uno\ndos\ntres */ b")
        self.assertEqual([t.type for t in tokens], [T.IDENT, T.IDENT, T.EOF])
        self.assertEqual((tokens[1].line, tokens[1].column), (3, 9))

    def test_line_and_column(self):
        tokens, _ = tokenize("jungle {\n    banan int x;\n}")
        positions = [(t.lexeme, t.line, t.column) for t in tokens[:-1]]
        self.assertEqual(positions, [("jungle", 1, 1), ("{", 1, 8), ("banan", 2, 5),
                                     ("int", 2, 11), ("x", 2, 15), (";", 2, 16), ("}", 3, 1)])


class TestLexicalErrors(unittest.TestCase):
    def test_invalid_character(self):
        self.assertEqual(error_codes("banan int $x = 1;"), ["LEX001"])

    def test_single_ampersand(self):
        tokens, errors = tokenize("a & b")
        self.assertEqual(errors[0].code, "LEX001")
        self.assertIn("&&", errors[0].message)

    def test_unclosed_string(self):
        self.assertEqual(error_codes('print("hola);\nx;'), ["LEX002"])

    def test_unclosed_comment(self):
        self.assertEqual(error_codes("x; /* sin cierre"), ["LEX003"])

    def test_malformed_numbers(self):
        self.assertEqual(error_codes("3.14.15 12abc 5."), ["LEX004", "LEX004", "LEX004"])

    def test_identifier_too_long(self):
        self.assertEqual(error_codes("a" * 32), ["LEX005"])
        self.assertEqual(error_codes("a" * 31), [])

    def test_integer_out_of_range(self):
        self.assertEqual(error_codes("2147483648"), ["LEX006"])
        self.assertEqual(error_codes("2147483647"), [])

    def test_invalid_escape(self):
        self.assertEqual(error_codes(r'"hola\q"'), ["LEX007"])

    def test_recovery_continues_after_error(self):
        # Tras el error el scanner sigue reconociendo tokens
        tokens, errors = tokenize("banan int @x = 5;")
        self.assertEqual(len(errors), 1)
        self.assertEqual([t.type for t in tokens],
                         [T.BANAN, T.INT, T.IDENT, T.ASSIGN, T.INT_LIT, T.SEMICOLON, T.EOF])

    def test_error_position(self):
        _, errors = tokenize("jungle {\n  banan int x = 3 # y;\n}")
        self.assertEqual((errors[0].line, errors[0].column), (2, 19))


class TestExampleFiles(unittest.TestCase):
    def test_valid_examples_have_no_errors(self):
        for path in sorted((EXAMPLES / "valid").glob("*.chc")):
            with self.subTest(file=path.name):
                _, errors = tokenize(path.read_text(encoding="utf-8"))
                self.assertEqual(errors, [])

    def test_lexical_invalid_examples_report_errors(self):
        for path in sorted((EXAMPLES / "invalid" / "lexical").glob("*.chc")):
            with self.subTest(file=path.name):
                _, errors = tokenize(path.read_text(encoding="utf-8"))
                self.assertGreater(len(errors), 0)

    def test_syntax_and_semantic_examples_are_lexically_valid(self):
        # Estos errores los detectarán el parser (semana 3) y el analizador semántico (semana 4)
        for folder in ("syntax", "semantic"):
            for path in sorted((EXAMPLES / "invalid" / folder).glob("*.chc")):
                with self.subTest(file=path.name):
                    _, errors = tokenize(path.read_text(encoding="utf-8"))
                    self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
