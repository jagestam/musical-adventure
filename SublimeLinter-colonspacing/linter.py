
import re
from typing import Iterator, Iterable
from SublimeLinter.lint import PythonLinter, LintMatch

class ColonSpacing(PythonLinter):
    """Marks spacing on both side of colon."""

    cmd = None
    multiline = True

    # Define your specific regex pattern here
    regex_pattern = r' \: '

    defaults = {
        'selector': 'source.python',
    }

    def run(self, cmd, code) -> str:
        return 'ColonSpacing: something so SublimeLinter will not assume this view to be OK.'

    def find_errors(self, output) -> Iterator[LintMatch]:
        mark_regex = re.compile(self.regex_pattern, re.MULTILINE)

        regions = self.view.find_by_selector(self.settings['selector'])
        for region in regions:
            region_text = self.view.substr(region)

            matches = mark_regex.finditer(region_text)
            for match in matches:
                start = region.a + match.start()
                row, col = self.view.rowcol(start)
                yield LintMatch(
                    line=row,
                    col=col,
                    near=match.group(),
                    error_type='info',
                    code='Inconsistent spacing',
                    message='Inconsistent spacing around colon. Write ": " not " : "'
                )
