class LircResponse:
    """
    A response from the LIRC daemon. Stores the command that had
    been sent, whether or not it was successful, and the parsed
    reply packet data.
    """

    def __init__(self, command: str, success: bool, data: list) -> None:
        self.command = command
        self.success = success
        self.data = data

    def __repr__(self) -> str:
        return (
            f"LircResponse(command={self.command}, "
            f"success={self.success}, "
            f"data={self.data})"
        )
