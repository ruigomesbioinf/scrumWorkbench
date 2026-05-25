class ScrumWorkbenchError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class RoomNotFoundError(ScrumWorkbenchError):
    def __init__(self, room_id: str):
        super().__init__(f"Room with ID {room_id} not found.")


class VotingClosedError(ScrumWorkbenchError):
    def __init__(self, room_id: str):
        super().__init__(f"Room with ID {room_id} is not in voting state. Cannot cast vote.")


class InvalidVoteError(ScrumWorkbenchError):
    def __init__(self, vote_value: str, deck_type: str):
        super().__init__(f"Invalid vote value '{vote_value}' for deck type '{deck_type}'.")


class PlayerNotFoundError(ScrumWorkbenchError):
    def __init__(self, player_id: str, room_id: str):
        super().__init__(f"Player with ID {player_id} not found in room with ID {room_id}.")
