from typing import List


class LircResponse:
    """
    A response from the LIRC server.

    Stores the command that had been sent
    and the parsed reply packet data.
    """

    def __init__(self, command: str, data: List[str]) -> None:
        self.command = command
        self.data = data

    def __repr__(self) -> str:
        return f"LircResponse(command={self.command}, data={self.data})"
