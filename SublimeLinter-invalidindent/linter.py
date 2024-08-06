import io
import tokenize
import token

from typing import Iterator

from SublimeLinter.lint import PythonLinter, LintMatch

def tname(tok: tokenize.TokenInfo) -> str:
    """return human-readable exact_type string"""
    return token.tok_name[tok.exact_type]

class InvalidIndent(PythonLinter):
    """
    Detects nonstandard indent.

    The 'num_spaces' setting controls the number of spaces per indent level, default 4.
    """
    # at the time of writing Sublime Text uses Python 3.8.12

    cmd = None
    multiline = True

    defaults = {
        'selector': 'source.python',
        'num_spaces': 4,
    }

    # def get_indent_tokens(self, region) -> Iterator[tokenize.TokenInfo]:
    #     """
    #     yield all indent tokens from given region
    #     """
    #     region_text: str = self.view.substr(region)
    #     for tok in tokenize.tokenize(io.BytesIO(region_text.encode('utf-8')).readline):
    #         if tok.type == 5:
    #             yield tok

    def run(self, cmd, code) -> str:
        return 'InvalidIndent: something so SublimeLinter will not assume this view to be OK.'

    def find_errors(self, output) -> Iterator[LintMatch]:

        try:
            num_spaces = int(self.settings['num_spaces'])
            assert num_spaces > 0
        except:
            num_spaces = 4

        regions = self.view.find_by_selector(self.settings['selector'])
        for region in regions:

            region_text: str = self.view.substr(region)
            row_region, col_region = self.view.rowcol(region.begin())

            # indent stack, for comparison to preceding indent level
            stack: list[str] = [""]

            for tok in tokenize.tokenize(io.BytesIO(region_text.encode('utf-8')).readline):
                if tname(tok) == "INDENT":
                    stack.append(stack[-1]+" "*num_spaces) # add one indent level
                    if tok.string != stack[-1]:
                        row_tok, col_tok = tok.start
                        yield LintMatch(
                            line=row_tok+row_region-1,
                            col=col_tok+col_region,
                            near=tok.string,
                            error_type='error',
                            code='Invalid Indent',
                            message=f'Indent should be {num_spaces} spaces.'
                            )
                elif tname(tok) == "DEDENT":
                    assert len(stack) > 1
                    # to ensure that the stack still contains the zero-indent string
                    # tokenize shouldnt give us more dedents than indents
                    stack.pop()

            # tokens = self.get_indent_tokens(region)

            # for tok in tokens:
            #     if not (set(tok.string) == set(" ") and len(tok.string)%4 == 0):
            #         row_tok, col_tok = tok.start
            #         yield LintMatch(
            #             line=row_tok+row_region-1,
            #             col=col_tok+col_region,
            #             near=tok.string,
            #             error_type='error',
            #             code='Invalid Indent',
            #             message=f'Indent should be spaces only,\n with length divisible by four.\n Currently {repr(tok.string)}, (length {len(tok.string)}).'
            #             )
