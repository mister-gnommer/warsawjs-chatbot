from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import clear as clear_screen

HISTORY_FILE = Path.home() / ".warsawjs-chat-history"


def create_repl() -> PromptSession:
    bindings = KeyBindings()

    # TODO: switch to Enter to submit (single-line mode); Meta+Enter for multi-line
    @bindings.add("escape", "enter")
    def _(event):
        event.current_buffer.validate_and_handle()

    return PromptSession(
        history=FileHistory(str(HISTORY_FILE)),
        key_bindings=bindings,
        multiline=True,
        prompt_continuation="... ",
    )


def read_input(session: PromptSession) -> str | None:
    while True:
        try:
            text = session.prompt("> ")
        except KeyboardInterrupt:
            return None

        stripped = text.strip()

        if stripped in ("/quit", "/exit"):
            return None

        if stripped == "/clear":
            clear_screen()
            continue

        return text
