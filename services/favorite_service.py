from api_client import get_favorites, toggle_favorite

class FavoriteService:
    def list_user_favorites(self, token):
        return get_favorites(token)

    def toggle(self, token, news_id, saved_title=None, saved_text=None):
        return toggle_favorite(token, news_id, saved_title, saved_text)
