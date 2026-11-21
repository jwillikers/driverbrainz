# Minimal type stubs for wikitextparser covering only the API used by this project.
# wikitextparser doesn't ship a py.typed marker or stubs.
from collections.abc import Iterable

class Argument:
    @property
    def value(self) -> str: ...

class WikiList:
    @property
    def items(self) -> list[str]: ...
    @property
    def templates(self) -> list[Template]: ...

class WikiText:
    @property
    def string(self) -> str: ...
    @property
    def templates(self) -> list[Template]: ...
    def get_lists(self, pattern: str | Iterable[str] = ...) -> list[WikiList]: ...

class Template(WikiText):
    @property
    def arguments(self) -> list[Argument]: ...
    def normal_name(
        self,
        rm_namespaces: Iterable[str] = ...,
        *,
        code: str | None = ...,
        capitalize: bool = ...,
    ) -> str: ...
    def get_arg(self, name: str) -> Argument | None: ...

def parse(string: str) -> WikiText: ...
