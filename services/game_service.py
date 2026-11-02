from api_client import get_my_games, add_game, delete_game

class GameService:
    def list_games(self, token):
        return get_my_games(token)

    def create_game_for_user(self, token, title):
        return add_game(token, title)

    def delete_game(self, token, game_id):
        return delete_game(token, game_id)
