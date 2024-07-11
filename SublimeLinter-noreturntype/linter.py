
import re
from collections.abc import Iterator
from SublimeLinter.lint import PythonLinter, LintMatch

class NoReturnType(PythonLinter):
    """Discovers and marks functions with no return type annotation."""

    cmd = None
    multiline = True

    # Define your specific regex pattern here
    regex_pattern = r'def\s+\w+\s*\([^)]*(\([^)]*\)[^)]*)*\)\s*:'

    defaults = {
        'selector': 'source.python',
    }

    def run(self, cmd, code) -> str:
        return 'NoReturnType: something so SublimeLinter will not assume this view to be OK.'

    def find_errors(self, output) -> Iterator[LintMatch]:
        mark_regex = re.compile(self.regex_pattern, re.MULTILINE)

        regions = self.view.find_by_selector(self.settings['selector'])
        for region in regions:
            region_text = self.view.substr(region)

            # Ignore everything between the first '#' on each line and the end of the line
            # Replaces all comments with whitespaces of same length
            lines : Iterable[str] = region_text.split('\n')
            processed_lines : Iterable[str] = (line.split('#',maxsplit=1)[0].ljust(len(line)) if '#' in line else line for line in lines)
            processed_text : str = '\n'.join(processed_lines)

            matches = mark_regex.finditer(processed_text)
            for match in matches:
                start = region.a + match.start()
                row, col = self.view.rowcol(start)
                yield LintMatch(
                    line=row,
                    col=col,
                    near=match.group(),
                    error_type='warning',
                    code='Missing return type annotation',
                    message='Function definition with missing return type annotation.'
                )
