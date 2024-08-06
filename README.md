

SublimeLinter self-contained plugin collection
================================


A collection of simple self-contained plugins for [SublimeLinter](https://github.com/SublimeLinter/SublimeLinter), that each check Python files for compliance with a single rule, either through Regular Expressions or the Python `tokenize` module.
They do not connect SublimeLinter to an external linter, all logic is described in each plugin's `linter.py`.
The idea is to keep the plugins simple, readable, and easy to modify rather than efficient.

Many thanks to my co-author, ChatGPT, and also to the author of the only self-contained SublimeLinter plugin that I could find on the internet, the lovely [SublimeLinter-annotations](https://github.com/SublimeLinter/SublimeLinter-annotations) package, which helped me get started.

### Dependencies
SublimeLinter must be installed in order to use these plugins.
Please use [Package Control](https://packagecontrol.io) to install the linter plugin.

##### SublimeLinter.sublime-settings
The optional SublimeLinter settings file links to icons in the [LSP package](https://github.com/sublimelsp/LSP), which will fail to load if the package is not installed.


### Installation
To use the plugins, simply copy each folder to your Sublime Text `Packages` folder.
On Linux systems, this folder is typically located at `~/.config/sublime-text/Packages/`.

Note that the SublimeLinter package only looks for linters one level below the `Packages` folder.
That is, it will find a linter located at `Packages/SublimeLinter-mylinter/linter.py`,
but not one located at `Packages/myfolder/SublimeLinter-mylinter/linter.py`.

