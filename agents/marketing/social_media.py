"""
Social Media Manager - управление социальными сетями.

Post creation, scheduling, engagement tracking.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
import re


logger = logging.getLogger(__name__)


class SocialMediaManager:
    """
    Менеджер social media.

    Поддерживаемые платформы:
    - Twitter/X
    - LinkedIn
    - Reddit
    - Product Hunt
    - Hacker News
    """

    def __init__(self, llm):
        """
        Args:
            llm: LLM instance
        """
        self.llm = llm

    async def create_posts(
        self,
        business_idea: Dict[str, Any],
        topics: List[str],
        platforms: List[str] = ["twitter", "linkedin", "reddit"]
    ) -> List[Dict[str, Any]]:
        """
        Создать посты для social media.

        Args:
            business_idea: Информация о бизнесе
            topics: Темы для постов
            platforms: Платформы

        Returns:
            List of social media posts
        """
        posts = []

        for topic in topics:
            # Создаем пост для каждой платформы
            for platform in platforms:
                post = await self._create_platform_post(
                    business_idea,
                    topic,
                    platform
                )
                posts.append(post)

        logger.info(f"Created {len(posts)} social media posts")

        return posts

    async def _create_platform_post(
        self,
        business_idea: Dict[str, Any],
        topic: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Создать пост для конкретной платформы.

        Args:
            business_idea: Информация о бизнесе
            topic: Тема поста
            platform: Платформа

        Returns:
            Dict with social media post
        """
        platform_guidelines = {
            "twitter": {
                "max_chars": 280,
                "tone": "Casual, punchy, engaging",
                "hashtags": "1-2 max",
                "format": "Hook + value + CTA",
                "best_time": "9am or 5pm EST"
            },
            "linkedin": {
                "max_chars": 3000,
                "tone": "Professional, insightful",
                "hashtags": "3-5 relevant",
                "format": "Story/insight + learnings + question",
                "best_time": "8am or 12pm EST"
            },
            "reddit": {
                "max_chars": 40000,
                "tone": "Authentic, helpful, not salesy",
                "hashtags": "None",
                "format": "Value-first, mention product only if relevant",
                "best_time": "7-9am EST"
            },
            "product_hunt": {
                "max_chars": 260,
                "tone": "Exciting, clear value prop",
                "hashtags": "None",
                "format": "What it does + why it matters",
                "best_time": "12:01am PST (launch day)"
            }
        }

        guidelines = platform_guidelines.get(platform, platform_guidelines["twitter"])

        prompt = f"""
Create a {platform} post.

Business: {business_idea['name']}
Topic: {topic}
Max characters: {guidelines['max_chars']}
Tone: {guidelines['tone']}
Format: {guidelines['format']}

Guidelines:
- {guidelines['tone']}
- Use {guidelines['hashtags']} hashtags
- Follow format: {guidelines['format']}
- Focus on value, not just promotion
- Include a clear CTA if appropriate

Return as JSON:
{{
    "text": "Post content...",
    "hashtags": ["hashtag1", "hashtag2"],
    "media_suggestion": "Description of suggested image/video",
    "best_time_to_post": "{guidelines['best_time']}",
    "engagement_hooks": ["Hook 1", "Hook 2"]
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.8,
            max_tokens=1000
        )

        post = self._parse_json_response(response)

        # Add metadata
        post["platform"] = platform
        post["topic"] = topic
        post["business_name"] = business_idea["name"]
        post["status"] = "draft"
        post["created_at"] = datetime.now().isoformat()

        return post

    async def create_content_calendar(
        self,
        business_idea: Dict[str, Any],
        duration_weeks: int = 4,
        posts_per_week: int = 7
    ) -> Dict[str, Any]:
        """
        Создать content calendar для social media.

        Args:
            business_idea: Информация о бизнесе
            duration_weeks: Количество недель
            posts_per_week: Постов в неделю

        Returns:
            Dict with content calendar
        """
        total_posts = duration_weeks * posts_per_week

        # Генерация тем
        topics = await self._generate_content_topics(
            business_idea,
            num_topics=total_posts
        )

        # Распределение по дням
        calendar = {
            "start_date": datetime.now().isoformat(),
            "duration_weeks": duration_weeks,
            "posts_per_week": posts_per_week,
            "schedule": []
        }

        current_date = datetime.now()

        for i, topic in enumerate(topics):
            # Определяем дату публикации
            days_offset = i  # По одному посту в день
            post_date = current_date + timedelta(days=days_offset)

            # Определяем платформу (ротация)
            platforms = ["twitter", "linkedin", "reddit"]
            platform = platforms[i % len(platforms)]

            calendar["schedule"].append({
                "date": post_date.isoformat(),
                "day_of_week": post_date.strftime("%A"),
                "topic": topic,
                "platform": platform,
                "status": "scheduled"
            })

        return calendar

    async def _generate_content_topics(
        self,
        business_idea: Dict[str, Any],
        num_topics: int = 28
    ) -> List[str]:
        """
        Генерация тем для social media контента.

        Args:
            business_idea: Информация о бизнесе
            num_topics: Количество тем

        Returns:
            List of content topics
        """
        prompt = f"""
Generate {num_topics} engaging social media content topics.

Business: {business_idea['name']}
Description: {business_idea['description']}
Target Audience: {business_idea.get('target_audience', 'Small teams')}

Content themes (mix these):
1. Educational tips (30%)
2. Behind-the-scenes/product updates (20%)
3. User success stories (15%)
4. Industry insights/trends (15%)
5. Engaging questions/polls (10%)
6. Memes/humor (5%)
7. Product features (5%)

Topics should:
- Provide value to followers
- Spark engagement
- Not be too promotional
- Be varied and interesting

Return as JSON array:
["Topic 1", "Topic 2", ...]
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.8,
            max_tokens=1500
        )

        topics = self._parse_json_array(response)

        logger.info(f"Generated {len(topics)} content topics")

        return topics

    async def create_launch_campaign(
        self,
        business_idea: Dict[str, Any],
        launch_date: str,
        platforms: List[str] = ["twitter", "linkedin", "product_hunt", "reddit"]
    ) -> Dict[str, Any]:
        """
        Создать launch campaign для Product Hunt / социальных сетей.

        Args:
            business_idea: Информация о бизнесе
            launch_date: Дата запуска (ISO format)
            platforms: Платформы для запуска

        Returns:
            Dict with launch campaign
        """
        launch_dt = datetime.fromisoformat(launch_date.replace('Z', '+00:00'))

        campaign = {
            "campaign_name": f"{business_idea['name']} Launch",
            "launch_date": launch_date,
            "platforms": platforms,
            "pre_launch": [],
            "launch_day": [],
            "post_launch": []
        }

        # Pre-launch (7 дней до)
        for days_before in [7, 5, 3, 1]:
            post_date = launch_dt - timedelta(days=days_before)

            teaser_post = {
                "date": post_date.isoformat(),
                "phase": "pre-launch",
                "type": "teaser",
                "content_idea": f"Coming soon teaser - {days_before} days before launch",
                "platforms": ["twitter", "linkedin"]
            }

            campaign["pre_launch"].append(teaser_post)

        # Launch day
        for platform in platforms:
            launch_post = {
                "date": launch_dt.isoformat(),
                "phase": "launch",
                "type": "announcement",
                "platform": platform,
                "content_idea": f"Official launch announcement on {platform}"
            }

            campaign["launch_day"].append(launch_post)

        # Post-launch (3 дня после)
        for days_after in [1, 2, 3]:
            post_date = launch_dt + timedelta(days=days_after)

            follow_up = {
                "date": post_date.isoformat(),
                "phase": "post-launch",
                "type": "follow-up",
                "content_idea": f"Thank you / early results / user feedback - day {days_after}",
                "platforms": ["twitter", "linkedin"]
            }

            campaign["post_launch"].append(follow_up)

        logger.info(f"Created launch campaign with {len(campaign['pre_launch']) + len(campaign['launch_day']) + len(campaign['post_launch'])} posts")

        return campaign

    def analyze_engagement(
        self,
        posts: List[Dict[str, Any]],
        engagement_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Анализ engagement для постов.

        Args:
            posts: List of social media posts
            engagement_data: Actual engagement data (optional)

        Returns:
            Dict with engagement analysis
        """
        # Mock implementation
        # В реальности: API от Twitter, LinkedIn, Reddit

        total_posts = len(posts)

        # Industry averages для SaaS social media
        avg_engagement_rates = {
            "twitter": 0.045,  # 4.5% (likes + retweets / followers)
            "linkedin": 0.054,  # 5.4%
            "reddit": 0.10,  # 10% (upvotes / views)
        }

        analysis = {
            "total_posts": total_posts,
            "platforms": {},
            "best_performing_topics": [],
            "recommendations": []
        }

        # По платформам
        for platform in ["twitter", "linkedin", "reddit"]:
            platform_posts = [p for p in posts if p.get("platform") == platform]

            if platform_posts:
                analysis["platforms"][platform] = {
                    "total_posts": len(platform_posts),
                    "estimated_engagement_rate": avg_engagement_rates.get(platform, 0.05),
                    "best_time_to_post": platform_posts[0].get("best_time_to_post", "9am EST")
                }

        # Recommendations
        analysis["recommendations"] = [
            "Post consistently (daily) for best results",
            "Engage with comments within first hour",
            "Use 1-2 relevant hashtags on Twitter",
            "Share behind-the-scenes content for authenticity",
            "Repurpose top-performing content across platforms"
        ]

        return analysis

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        json_str = re.sub(r'^```(?:json)?\n', '', response.strip())
        json_str = re.sub(r'\n```$', '', json_str)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {}

    def _parse_json_array(self, response: str) -> List[str]:
        """Parse JSON array from LLM response."""
        json_str = re.sub(r'^```(?:json)?\n', '', response.strip())
        json_str = re.sub(r'\n```$', '', json_str)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback
            lines = [
                line.strip().strip('"\',-')
                for line in response.split('\n')
                if line.strip() and not line.strip().startswith(('```', '[', ']'))
            ]
            return [line for line in lines if len(line) > 5]


# Пример использования
if __name__ == "__main__":
    import asyncio
    from agents.base.mock_llm import MockLLM

    async def main():
        llm = MockLLM()
        social_manager = SocialMediaManager(llm=llm)

        business_idea = {
            "name": "TaskFlow AI",
            "description": "AI-powered PM tool for small teams",
            "target_audience": "Freelancers and teams of 2-10"
        }

        # Create content calendar
        calendar = await social_manager.create_content_calendar(
            business_idea=business_idea,
            duration_weeks=4,
            posts_per_week=7
        )

        print(f"Created content calendar:")
        print(f"  - Duration: {calendar['duration_weeks']} weeks")
        print(f"  - Total posts: {len(calendar['schedule'])}")

        # Create launch campaign
        launch_campaign = await social_manager.create_launch_campaign(
            business_idea=business_idea,
            launch_date=datetime.now().isoformat()
        )

        print(f"\nLaunch campaign:")
        print(f"  - Pre-launch posts: {len(launch_campaign['pre_launch'])}")
        print(f"  - Launch day posts: {len(launch_campaign['launch_day'])}")
        print(f"  - Post-launch posts: {len(launch_campaign['post_launch'])}")

    asyncio.run(main())
