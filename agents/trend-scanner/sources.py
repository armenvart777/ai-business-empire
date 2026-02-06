"""
Источники данных для Trend Scanner агента.

Интеграции:
- Google Trends API
- Reddit API
- Product Hunt API
"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging


logger = logging.getLogger(__name__)


class GoogleTrendsSource:
    """
    Google Trends интеграция.

    Использует pytrends (неофициальная библиотека).
    """

    def __init__(self):
        """Инициализация Google Trends клиента."""
        try:
            from pytrends.request import TrendReq
            self.pytrends = TrendReq(hl='en-US', tz=360)
            logger.info("Google Trends client initialized")
        except ImportError:
            logger.warning("pytrends not installed. Install: pip install pytrends")
            self.pytrends = None

    async def get_trending_searches(
        self,
        geo: str = "US",
        timeframe: str = "now 1-d"
    ) -> List[Dict[str, Any]]:
        """
        Получить trending searches.

        Args:
            geo: География (US, GB, etc.)
            timeframe: Временной интервал

        Returns:
            List[Dict]: Список трендов с метриками
        """
        if not self.pytrends:
            logger.warning("pytrends not available")
            return []

        try:
            # Получаем trending searches
            trending_df = self.pytrends.trending_searches(pn=geo.lower())

            trends = []
            for query in trending_df[0].tolist()[:20]:  # Топ-20
                trends.append({
                    "query": query,
                    "geo": geo,
                    "interest": 100  # Все trending имеют высокий interest
                })

            logger.info(f"Found {len(trends)} trending searches from Google Trends")
            return trends

        except Exception as e:
            logger.error(f"Error fetching Google Trends: {e}")
            return []

    async def get_related_queries(self, query: str) -> List[str]:
        """
        Получить related queries для тренда.

        Args:
            query: Поисковый запрос

        Returns:
            List[str]: Связанные запросы
        """
        if not self.pytrends:
            return []

        try:
            # Получаем interest over time для контекста
            self.pytrends.build_payload(
                [query],
                cat=0,
                timeframe='today 3-m',
                geo='US'
            )

            # Получаем related queries
            related = self.pytrends.related_queries()

            if query in related and related[query]['top'] is not None:
                return related[query]['top']['query'].tolist()[:5]

            return []

        except Exception as e:
            logger.error(f"Error fetching related queries: {e}")
            return []


class RedditSource:
    """
    Reddit интеграция.

    Использует PRAW (Python Reddit API Wrapper).
    """

    def __init__(self):
        """Инициализация Reddit клиента."""
        try:
            import praw
            # Используем read-only mode (не требует авторизации)
            self.reddit = praw.Reddit(
                client_id="YOUR_CLIENT_ID",  # TODO: Получить из .env
                client_secret="YOUR_CLIENT_SECRET",
                user_agent="TrendScanner/1.0"
            )
            logger.info("Reddit client initialized")
        except ImportError:
            logger.warning("praw not installed. Install: pip install praw")
            self.reddit = None
        except Exception as e:
            logger.error(f"Error initializing Reddit client: {e}")
            self.reddit = None

    async def get_top_posts(
        self,
        subreddit: str,
        time_filter: str = "day",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Получить топ-посты из subreddit.

        Args:
            subreddit: Название subreddit
            time_filter: Фильтр времени (hour, day, week, month, year, all)
            limit: Количество постов

        Returns:
            List[Dict]: Список постов с метриками
        """
        if not self.reddit:
            logger.warning("Reddit client not available")
            return self._get_mock_reddit_data(subreddit, limit)

        try:
            subreddit_obj = self.reddit.subreddit(subreddit)
            top_posts = subreddit_obj.top(time_filter=time_filter, limit=limit)

            posts = []
            for post in top_posts:
                posts.append({
                    "title": post.title,
                    "selftext": post.selftext,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "url": post.url,
                    "created_utc": post.created_utc,
                    "subreddit": subreddit
                })

            logger.info(f"Found {len(posts)} posts from r/{subreddit}")
            return posts

        except Exception as e:
            logger.error(f"Error fetching Reddit posts: {e}")
            return self._get_mock_reddit_data(subreddit, limit)

    def _get_mock_reddit_data(self, subreddit: str, limit: int) -> List[Dict[str, Any]]:
        """Mock data для тестирования без API."""
        return [
            {
                "title": f"[Mock] Post from r/{subreddit}",
                "selftext": "This is mock data. Install praw and configure Reddit API.",
                "score": 100,
                "num_comments": 50,
                "url": f"https://reddit.com/r/{subreddit}",
                "created_utc": datetime.now().timestamp(),
                "subreddit": subreddit
            }
        ] * min(limit, 3)


class ProductHuntSource:
    """
    Product Hunt интеграция.

    Использует GraphQL API.
    """

    def __init__(self):
        """Инициализация Product Hunt клиента."""
        self.api_url = "https://api.producthunt.com/v2/api/graphql"
        self.access_token = None  # TODO: Получить из .env
        logger.info("Product Hunt client initialized")

    async def get_recent_products(
        self,
        days: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Получить недавние продукты.

        Args:
            days: За сколько дней

        Returns:
            List[Dict]: Список продуктов
        """
        if not self.access_token:
            logger.warning("Product Hunt API token not configured")
            return self._get_mock_product_hunt_data()

        try:
            import aiohttp

            query = """
            query GetPosts($after: String) {
              posts(order: VOTES, after: $after) {
                edges {
                  node {
                    id
                    name
                    tagline
                    description
                    votesCount
                    topics {
                      edges {
                        node {
                          name
                        }
                      }
                    }
                    url
                  }
                }
              }
            }
            """

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json={"query": query},
                    headers=headers
                ) as response:
                    data = await response.json()

            # Парсим результаты
            products = []
            edges = data.get("data", {}).get("posts", {}).get("edges", [])

            for edge in edges:
                node = edge.get("node", {})
                topics = [
                    t["node"]["name"]
                    for t in node.get("topics", {}).get("edges", [])
                ]

                products.append({
                    "name": node.get("name", ""),
                    "tagline": node.get("tagline", ""),
                    "description": node.get("description", ""),
                    "votes": node.get("votesCount", 0),
                    "topics": topics,
                    "url": node.get("url", "")
                })

            logger.info(f"Found {len(products)} products from Product Hunt")
            return products

        except Exception as e:
            logger.error(f"Error fetching Product Hunt data: {e}")
            return self._get_mock_product_hunt_data()

    def _get_mock_product_hunt_data(self) -> List[Dict[str, Any]]:
        """Mock data для тестирования без API."""
        return [
            {
                "name": "Mock Product 1",
                "tagline": "AI-powered tool for developers",
                "description": "This is mock data. Configure Product Hunt API token.",
                "votes": 500,
                "topics": ["AI", "Developer Tools", "Productivity"],
                "url": "https://producthunt.com"
            },
            {
                "name": "Mock Product 2",
                "tagline": "No-code automation platform",
                "description": "Another mock product for testing.",
                "votes": 350,
                "topics": ["No-Code", "Automation", "SaaS"],
                "url": "https://producthunt.com"
            }
        ]


# Пример использования
if __name__ == "__main__":
    async def main():
        # Google Trends
        print("=== Google Trends ===")
        google = GoogleTrendsSource()
        trends = await google.get_trending_searches(geo="US")
        for trend in trends[:5]:
            print(f"- {trend['query']}")

        # Reddit
        print("\n=== Reddit ===")
        reddit = RedditSource()
        posts = await reddit.get_top_posts("SaaS", limit=5)
        for post in posts:
            print(f"- {post['title'][:60]}... ({post['score']} upvotes)")

        # Product Hunt
        print("\n=== Product Hunt ===")
        ph = ProductHuntSource()
        products = await ph.get_recent_products()
        for product in products[:5]:
            print(f"- {product['name']}: {product['tagline']}")

    asyncio.run(main())
