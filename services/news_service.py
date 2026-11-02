from api_client import get_news, get_news_detail

class NewsService:
    def list_news_for_user(self, token, limit=100, source_name=None):
        return get_news(token, source=source_name, limit=limit)

    def search_news_for_user(self, token, query):
        return get_news(token, search=query)

    def get_news_detail(self, token, news_id):
        return get_news_detail(token, news_id)
