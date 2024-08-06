import io
import tokenize
import token

from typing import Iterator, Optional

from SublimeLinter.lint import PythonLinter, LintMatch

EXACT_TYPE_STRING_SET = set(token.tok_name.values())

def tname(tok: tokenize.TokenInfo) -> str:
    """return human-readable exact_type string"""
    return token.tok_name[tok.exact_type]

def is_exact_type(tok: Optional[tokenize.TokenInfo], target: str) -> bool:
    """check wether the token has the desired exact_type"""
    assert target in EXACT_TYPE_STRING_SET
    if tok is None:
        return False
    return tname(tok) == target

# def debug_match(row_region: int, col_region: int, tok: tokenize.TokenInfo) -> LintMatch:
#     row_tok, col_tok = tok.start
#     near = tok.string
#     return LintMatch(
#                 line=row_tok+row_region-1,
#                 col=col_tok+col_region,
#                 near=near,
#                 error_type='info',
#                 code='debug match',
#                 message=f'tname: {tname(tok)}'
#                 )


def consume_args(toks: Iterator[tokenize.TokenInfo]) -> None:
    """
    consume function args from token list

    call after encountering the 'def' token

    the next token should be the function name,
    followed by the arguments enclosed by parentheses

    after the function has been called, the next token should be RARROW or COLON

    """
    # the first token should be the function name
    fname_tok = next(toks, None)
    assert is_exact_type(fname_tok, "NAME")

    # then the opening parenthesis
    open_par = next(toks, None)
    assert is_exact_type(open_par, "LPAR")

    # consume all function arguments
    par_stack: list[str] = ["LPAR"]
    while len(par_stack) and (tok := next(toks,None)) is not None:
        curr_tname = tname(tok)
        if curr_tname == "LPAR":
            par_stack.append(curr_tname)
        elif curr_tname == "RPAR":
            par_stack.pop()

    # now the next token should be either RARROW or COLON

class NoReturnType(PythonLinter):
    """Discovers and marks function declarations with no return type annotation."""

    cmd = None
    multiline = True

    # Define your specific regex pattern here
    # regex_pattern = r'def\s+\w+\s*\([^)]*(\([^)]*\)[^)]*)*\)\s*:'

    defaults = {
        'selector': 'source.python',
    }

    def run(self, cmd, code) -> str:
        return 'NoReturnType: something so SublimeLinter will not assume this view to be OK.'

    def find_errors(self, output) -> Iterator[LintMatch]:
        # mark_regex = re.compile(self.regex_pattern, re.MULTILINE)

        regions = self.view.find_by_selector(self.settings['selector'])
        for region in regions:
            region_text = self.view.substr(region)

            row_region, col_region = self.view.rowcol(region.begin())

            toks = tokenize.tokenize(io.BytesIO(region_text.encode('utf-8')).readline)

            # iterate over tokens
            while (tok := next(toks,None)) is not None:
                if tname(tok) == "NAME" and tok.string == "def":
                    # yield debug_match(row_region, col_region, tok)
                    # continue
                    # print("def found", tok)
                    consume_args(toks)
                    # now the next token should be either RARROW or COLON
                    next_tok = next(toks,None)
                    # if next_tok is not None:
                        # yield debug_match(row_region, col_region, next_tok)
                    # print("next_tok", next_tok)
                    if not is_exact_type(next_tok, "RARROW"):
                        # case tokens exhausted
                        if next_tok is None:
                            row_tok, col_tok = tok.start
                            near = tok.line
                        # case COLON
                        elif is_exact_type(next_tok, "COLON"):
                            row_tok, col_tok = next_tok.start
                            near = next_tok.line
                        # case incorrect syntax, ignore
                        else:
                            continue
                        yield LintMatch(
                            line=row_tok+row_region-1,
                            col=0,
                            near=near,
                            error_type='error',
                            code='Missing return type annotation',
                            message='Function definition with missing return type annotation.'
                            )

            # # Ignore everything between the first '#' on each line and the end of the line
            # # Replaces all comments with whitespaces of same length
            # lines: Iterable[str] = region_text.split('\n')
            # processed_lines: Iterable[str] = (line.split('#',maxsplit=1)[0].ljust(len(line)) if '#' in line else line for line in lines)
            # processed_text: str = '\n'.join(processed_lines)

            # matches = mark_regex.finditer(processed_text)
            # for match in matches:
            #     start = region.a + match.start()
            #     row, col = self.view.rowcol(start)
            #     yield LintMatch(
            #         line=row,
            #         col=col,
            #         near=match.group(),
            #         error_type='warning',
            #         code='Missing return type annotation',
            #         message='Function definition with missing return type annotation.'
            #     )
