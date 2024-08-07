import io
import tokenize
import token

from typing import Iterator, Optional, List

from SublimeLinter.lint import PythonLinter, LintMatch

EXACT_TYPE_STRING_SET = set(token.tok_name.values())

def tname(tok: Optional[tokenize.TokenInfo]) -> str:
    """return human-readable exact_type string, empty string if tok is None"""
    return "" if tok is None else token.tok_name[tok.exact_type]

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

def consume_until_brace_closed(toks: Iterator[tokenize.TokenInfo], stack: List[str]) -> None:
    """
    stack should contain the opening brace, "(" or "[" or "{"

    will consume tokens until the corresponding closing brace is encountered
    """
    Ls = ["LPAR", "LSQB", "LBRACE"]
    Rs = ["RPAR", "RSQB", "RBRACE"]
    map_ = dict(zip(Rs, Ls))
    assert len(stack) == 1 and stack[-1] in Ls
    while stack and (tok := next(toks,None)) is not None:
        curr_tname = tname(tok)
        if curr_tname in Ls:
            stack.append(curr_tname)
        elif curr_tname in Rs:
            assert stack[-1] == map_[curr_tname]
            stack.pop()


def consume_fname_and_params(toks: Iterator[tokenize.TokenInfo]) -> None:
    """
    consume function name and function parameters from token list

    call after encountering the 'def' token

    the next token should be the function name,
    followed by the type parameters enclosed by braces,
    and then the regular parameters enclosed by parentheses

    after the function has been called, the next token should be RARROW or COLON

    """
    # the first token should be the function name
    fname_tok = next(toks, None)
    assert tname(fname_tok) == "NAME"

    # then the opening parenthesis
    open_par = next(toks, None)
    open_tname = tname(open_par)
    assert open_par and open_tname in ["LSQB", "LPAR"]
    if open_tname == "LSQB":
        # first the type parameters
        consume_until_brace_closed(toks, [open_tname])
        open_par = next(toks, None)
        open_tname = tname(open_par)
    # then regular parameters
    assert open_par and open_tname == "LPAR"
    consume_until_brace_closed(toks, [open_tname])



class NoReturnType(PythonLinter):
    """Discovers and marks function declarations with no return type annotation."""

    cmd = None
    multiline = True

    defaults = {
        'selector': 'source.python',
    }

    def run(self, cmd, code) -> str:
        return 'NoReturnType: something so SublimeLinter will not assume this view to be OK.'

    def find_errors(self, output) -> Iterator[LintMatch]:


        regions = self.view.find_by_selector(self.settings['selector'])
        for region in regions:
            region_text = self.view.substr(region)

            row_region, col_region = self.view.rowcol(region.begin())

            toks = tokenize.tokenize(io.BytesIO(region_text.encode('utf-8')).readline)

            # iterate over tokens
            while (tok := next(toks,None)) is not None:
                if tname(tok) == "NAME" and tok.string == "def":
                    # first, consume the function name and parameters
                    consume_fname_and_params(toks)

                    # now the next token should be either RARROW or COLON
                    next_tok = next(toks,None)
                    if not tname(next_tok) == "RARROW":
                        # case toks is exhausted
                        if next_tok is None:
                            row_tok, col_tok = tok.start
                            near = tok.line
                        # case next_tok is COLON
                        elif tname(next_tok) == "COLON":
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
