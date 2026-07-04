"""Tab-completion for the redink REPL: slash commands, /rerun dimensions,
/review paths + arXiv stub."""
from prompt_toolkit.completion import Completer, Completion, PathCompleter
from prompt_toolkit.document import Document

COMMANDS = {
    "/review": "review a paper — <path.md> or <arxiv-url>",
    "/report": "re-show the last verdict",
    "/rerun":  "re-run one dimension of the last review",
    "/clear":  "clear the screen",
    "/help":   "show tips",
    "/exit":   "quit",
}

_ARXIV_STUB = "https://arxiv.org/abs/"


class RedinkCompleter(Completer):
    def __init__(self, get_dimensions):
        # callable returning the current review's dimensions (or [])
        self._get_dimensions = get_dimensions
        self._paths = PathCompleter(expanduser=True)

    def get_completions(self, document: Document, complete_event):
        text = document.text_before_cursor
        # a plain question (no leading slash) → no completion, just type
        if not text.startswith("/"):
            return

        parts = text.split(maxsplit=1)
        cmd = parts[0]

        # still typing the command word → complete command names
        if len(parts) == 1 and not text.endswith(" "):
            for name, meta in COMMANDS.items():
                if name.startswith(cmd):
                    yield Completion(name, start_position=-len(cmd), display_meta=meta)
            return

        arg = parts[1] if len(parts) > 1 else ""

        # /rerun <dimension> → complete from the current review's dimensions
        if cmd == "/rerun":
            for dim in self._get_dimensions():
                if dim.startswith(arg):
                    yield Completion(dim, start_position=-len(arg), display_meta="dimension")
            return

        # /review <path|url> → path completion, plus an arXiv URL stub
        if cmd == "/review":
            if not arg and complete_event.completion_requested:
                yield Completion(_ARXIV_STUB, start_position=0, display_meta="arXiv paper")
            if not arg.startswith(("http", "www")):
                sub = Document(arg, cursor_position=len(arg))
                for c in self._paths.get_completions(sub, complete_event):
                    yield c
            return
