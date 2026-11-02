from api_client import register as api_register, login as api_login

class UserInterface:
    def __init__(self):
        self.current_user = None
        self.token = None

    def register(self, username, email, password):
        return api_register(username, email, password)

    def login(self, username, password):
        result = api_login(username, password)
        if result.get("success"):
            self.current_user = result["user"]
            self.token = result["token"]
        return result

    def logout(self):
        self.current_user = None
        self.token = None
        return {"success": True}

    def is_authenticated(self):
        return self.current_user is not None