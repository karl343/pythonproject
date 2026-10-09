from __future__ import annotations

from models.data_manager import DataManager

class AuthController:

    def __init__(self, data_manager: DataManager) -> None:
        self._dm = data_manager

    def login(self, username: str, password: str) -> tuple[bool, str]:
        username = username.strip()
        password = password.strip()

        if not username or not password:
            return False, "Please fill in all fields."

        user = self._dm.find_user(username)
        if user is None or user["password"] != password:
            return False, "Invalid username or password."

        return True, ""
