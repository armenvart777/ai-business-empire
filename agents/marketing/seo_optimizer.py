"""
SEO Optimizer - оптимизация для поисковых систем.

Keyword research, on-page SEO, technical SEO recommendations.
"""

import logging
from typing import Dict, Any, List
import json
import re


logger = logging.getLogger(__name__)


class SEOOptimizer:
    """
    SEO оптимизация контента и сайта.

    Функции:
    - Keyword research
    - On-page SEO analysis
    - Meta tags optimization
    - Technical SEO recommendations
    - Competitor analysis
    """

    def __init__(self, llm):
        """
        Args:
            llm: LLM instance
        """
        self.llm = llm

    async def create_seo_strategy(
        self,
        business_idea: Dict[str, Any],
        deployment_url: str,
        blog_posts: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Создать полную SEO стратегию.

        Args:
            business_idea: Информация о бизнесе
            deployment_url: URL сайта
            blog_posts: Список blog posts (опционально)

        Returns:
            Dict с SEO стратегией
        """
        blog_posts = blog_posts or []

        # 1. Keyword research
        keywords = await self._keyword_research(business_idea)

        # 2. On-page SEO для главной страницы
        homepage_seo = await self._optimize_homepage_seo(
            business_idea,
            keywords
        )

        # 3. Technical SEO recommendations
        technical_seo = await self._technical_seo_recommendations(
            deployment_url
        )

        # 4. Content SEO для blog posts
        content_seo = []
        for post in blog_posts[:5]:  # Top 5 posts
            post_seo = await self._optimize_blog_post_seo(post, keywords)
            content_seo.append(post_seo)

        # 5. Link building strategy
        link_building = await self._link_building_strategy(business_idea)

        return {
            "keywords": keywords,
            "homepage_seo": homepage_seo,
            "technical_seo": technical_seo,
            "content_seo": content_seo,
            "link_building": link_building,
            "estimated_seo_score": self._calculate_seo_score(
                homepage_seo,
                technical_seo
            )
        }

    async def _keyword_research(
        self,
        business_idea: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Keyword research для бизнеса.

        Returns:
            Dict с primary/secondary/long-tail keywords
        """
        prompt = f"""
Perform keyword research for this SaaS business.

Business: {business_idea['name']}
Description: {business_idea['description']}
Target Audience: {business_idea.get('target_audience', 'Small teams')}
Key Features: {', '.join(business_idea.get('key_features', []))}

Identify:
1. Primary keywords (3-5) - high volume, high intent
2. Secondary keywords (5-10) - medium volume, relevant
3. Long-tail keywords (10-15) - specific, less competitive
4. Question keywords (5-10) - for blog content

For each keyword provide:
- Search intent (informational/navigational/transactional)
- Estimated difficulty (low/medium/high)
- Content type (homepage/landing/blog/FAQ)

Return as JSON:
{{
    "primary_keywords": [
        {{"keyword": "...", "intent": "...", "difficulty": "...", "volume": "high"}}
    ],
    "secondary_keywords": [...],
    "long_tail_keywords": [...],
    "question_keywords": [...]
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.5,
            max_tokens=2000
        )

        keywords = self._parse_json_response(response)

        logger.info(f"Identified {len(keywords.get('primary_keywords', []))} primary keywords")

        return keywords

    async def _optimize_homepage_seo(
        self,
        business_idea: Dict[str, Any],
        keywords: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Оптимизация SEO для главной страницы.

        Returns:
            Dict с SEO рекомендациями для homepage
        """
        primary_keywords = keywords.get("primary_keywords", [])
        primary_kw_list = [kw["keyword"] for kw in primary_keywords[:3]]

        prompt = f"""
Create SEO-optimized meta tags and content for homepage.

Business: {business_idea['name']}
Tagline: {business_idea.get('tagline', '')}
Description: {business_idea['description']}
Primary Keywords: {', '.join(primary_kw_list)}

Return as JSON:
{{
    "title_tag": "SEO title (60 chars, include primary keyword)",
    "meta_description": "Meta description (155 chars, include CTA)",
    "h1": "Main H1 heading (include primary keyword)",
    "h2_suggestions": ["H2 heading 1", "H2 heading 2"],
    "schema_markup": {{
        "@type": "SoftwareApplication",
        "name": "...",
        "description": "...",
        "applicationCategory": "..."
    }},
    "open_graph": {{
        "og:title": "...",
        "og:description": "...",
        "og:image": "suggested image description"
    }}
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.5,
            max_tokens=1500
        )

        return self._parse_json_response(response)

    async def _technical_seo_recommendations(
        self,
        deployment_url: str
    ) -> List[Dict[str, Any]]:
        """
        Technical SEO рекомендации.

        Returns:
            List of technical SEO items to implement
        """
        # Mock implementation
        # В реальности: Lighthouse API, PageSpeed Insights API

        recommendations = [
            {
                "category": "Performance",
                "priority": "high",
                "item": "Enable image optimization",
                "implementation": "Use Next.js Image component with lazy loading",
                "impact": "Improve page load speed by 30-50%"
            },
            {
                "category": "Performance",
                "priority": "high",
                "item": "Implement caching headers",
                "implementation": "Set Cache-Control headers for static assets",
                "impact": "Reduce server load and improve repeat visit speed"
            },
            {
                "category": "Mobile",
                "priority": "high",
                "item": "Ensure mobile responsiveness",
                "implementation": "Test on mobile devices, fix viewport issues",
                "impact": "Essential for Google mobile-first indexing"
            },
            {
                "category": "Indexing",
                "priority": "high",
                "item": "Create and submit sitemap.xml",
                "implementation": "Generate sitemap, submit to Google Search Console",
                "impact": "Help search engines discover all pages"
            },
            {
                "category": "Indexing",
                "priority": "medium",
                "item": "Optimize robots.txt",
                "implementation": "Allow crawling of public pages, block admin",
                "impact": "Control what search engines index"
            },
            {
                "category": "Security",
                "priority": "high",
                "item": "Ensure HTTPS everywhere",
                "implementation": "Force HTTPS redirect, HSTS headers",
                "impact": "Required for Google ranking, user trust"
            },
            {
                "category": "Structure",
                "priority": "medium",
                "item": "Implement breadcrumb navigation",
                "implementation": "Add breadcrumbs with schema markup",
                "impact": "Improve UX and search result display"
            },
            {
                "category": "Content",
                "priority": "medium",
                "item": "Add canonical tags",
                "implementation": "Set canonical URL for all pages",
                "impact": "Prevent duplicate content issues"
            },
            {
                "category": "Speed",
                "priority": "medium",
                "item": "Minimize JavaScript bundle size",
                "implementation": "Code splitting, tree shaking, lazy loading",
                "impact": "Faster initial page load"
            },
            {
                "category": "Analytics",
                "priority": "low",
                "item": "Setup Google Search Console",
                "implementation": "Verify ownership, monitor search performance",
                "impact": "Track SEO progress and issues"
            }
        ]

        logger.info(f"Generated {len(recommendations)} technical SEO recommendations")

        return recommendations

    async def _optimize_blog_post_seo(
        self,
        blog_post: Dict[str, Any],
        keywords: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        SEO оптимизация для blog post.

        Args:
            blog_post: Blog post object
            keywords: Keyword research results

        Returns:
            Dict с SEO рекомендациями для поста
        """
        # Найти релевантные keywords для этого поста
        post_keywords = self._find_relevant_keywords(
            blog_post.get("topic", ""),
            keywords
        )

        return {
            "post_title": blog_post.get("title", ""),
            "recommended_keywords": post_keywords,
            "seo_title": blog_post.get("title", "")[:60],  # Truncate to 60 chars
            "meta_description": blog_post.get("meta_description", "")[:155],
            "url_slug": self._generate_url_slug(blog_post.get("title", "")),
            "internal_linking_opportunities": [],  # Заполняется позже
            "image_alt_text_suggestions": [
                f"Illustration for {blog_post.get('topic', '')}",
                f"{blog_post.get('title', '')} infographic"
            ]
        }

    def _find_relevant_keywords(
        self,
        topic: str,
        keywords: Dict[str, Any]
    ) -> List[str]:
        """
        Найти релевантные keywords для темы.

        Returns:
            List of relevant keywords
        """
        # Простой поиск по совпадениям
        topic_lower = topic.lower()
        relevant = []

        for kw_category in ["primary_keywords", "secondary_keywords", "long_tail_keywords"]:
            for kw_obj in keywords.get(kw_category, []):
                keyword = kw_obj.get("keyword", "") if isinstance(kw_obj, dict) else kw_obj
                if any(word in topic_lower for word in keyword.lower().split()):
                    relevant.append(keyword)

        return relevant[:5]  # Top 5

    async def _link_building_strategy(
        self,
        business_idea: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Стратегия link building.

        Returns:
            Dict со стратегией получения backlinks
        """
        prompt = f"""
Create a link building strategy for this SaaS business.

Business: {business_idea['name']}
Description: {business_idea['description']}
Target Audience: {business_idea.get('target_audience', '')}

Suggest:
1. Guest posting opportunities (5 sites/blogs)
2. Directory submissions (5 relevant directories)
3. Partnership opportunities
4. Content that attracts natural backlinks
5. Community engagement (forums, Reddit, etc.)

Return as JSON:
{{
    "guest_posting": [
        {{"site": "...", "topic_ideas": [...], "difficulty": "low/medium/high"}}
    ],
    "directories": ["directory1", "directory2", ...],
    "partnerships": ["potential partner 1", ...],
    "linkable_content": ["content idea 1", ...],
    "communities": [
        {{"platform": "...", "community": "...", "approach": "..."}}
    ]
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.7,
            max_tokens=2000
        )

        return self._parse_json_response(response)

    def _calculate_seo_score(
        self,
        homepage_seo: Dict[str, Any],
        technical_seo: List[Dict[str, Any]]
    ) -> int:
        """
        Оценить SEO score (0-100).

        Returns:
            int: SEO score
        """
        score = 50  # Base score

        # Homepage SEO elements
        if homepage_seo.get("title_tag"):
            score += 10
        if homepage_seo.get("meta_description"):
            score += 10
        if homepage_seo.get("schema_markup"):
            score += 10

        # Technical SEO (высокоприоритетные)
        high_priority_count = sum(
            1 for rec in technical_seo
            if rec.get("priority") == "high"
        )
        score += min(high_priority_count * 3, 20)

        return min(score, 100)

    def _generate_url_slug(self, title: str) -> str:
        """
        Генерация URL slug из заголовка.

        Args:
            title: Заголовок

        Returns:
            str: URL-friendly slug
        """
        # Lowercase
        slug = title.lower()

        # Remove special characters
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)

        # Replace spaces with hyphens
        slug = re.sub(r'\s+', '-', slug)

        # Remove multiple hyphens
        slug = re.sub(r'-+', '-', slug)

        # Trim hyphens
        slug = slug.strip('-')

        return slug[:60]  # Max 60 chars

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        json_str = re.sub(r'^```(?:json)?\n', '', response.strip())
        json_str = re.sub(r'\n```$', '', json_str)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {}


# Пример использования
if __name__ == "__main__":
    import asyncio
    from agents.base.mock_llm import MockLLM

    async def main():
        llm = MockLLM()
        seo = SEOOptimizer(llm=llm)

        business_idea = {
            "name": "TaskFlow AI",
            "tagline": "Project management that thinks for you",
            "description": "AI-powered PM tool for small teams",
            "target_audience": "Freelancers and teams of 2-10",
            "key_features": [
                "AI task prioritization",
                "Automatic deadline prediction"
            ]
        }

        strategy = await seo.create_seo_strategy(
            business_idea=business_idea,
            deployment_url="https://taskflow-ai.vercel.app",
            blog_posts=[]
        )

        print(f"SEO Score: {strategy['estimated_seo_score']}/100")
        print(f"Primary Keywords: {len(strategy['keywords'].get('primary_keywords', []))}")
        print(f"Technical Recommendations: {len(strategy['technical_seo'])}")

    asyncio.run(main())
