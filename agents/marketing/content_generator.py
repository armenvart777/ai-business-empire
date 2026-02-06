"""
Content Generator - генерация контента для маркетинга.

Blog posts, social media posts, emails, landing pages.
"""

import logging
from typing import Dict, Any, List
import json
import re


logger = logging.getLogger(__name__)


class ContentGenerator:
    """
    Генератор контента с помощью LLM.

    Поддерживает:
    - Blog posts (SEO-optimized)
    - Social media posts
    - Email copy
    - Landing page copy
    """

    def __init__(self, llm):
        """
        Args:
            llm: LLM instance для генерации
        """
        self.llm = llm

    async def generate_content_topics(
        self,
        business_idea: Dict[str, Any],
        channel: str,
        num_topics: int = 10
    ) -> List[str]:
        """
        Генерация тем для контента.

        Args:
            business_idea: Информация о бизнесе
            channel: Канал (blog/email/social/ads)
            num_topics: Количество тем

        Returns:
            List[str]: Темы для контента
        """
        prompt = f"""
Generate {num_topics} compelling content topics for {channel} marketing.

Business: {business_idea['name']}
Description: {business_idea['description']}
Target Audience: {business_idea.get('target_audience', 'Small teams')}
Key Features: {', '.join(business_idea.get('key_features', []))}

Content should:
1. Address user pain points
2. Showcase product benefits
3. Be SEO-friendly (for blog)
4. Drive engagement (for social)
5. Focus on value, not just features

Return topics as JSON array of strings:
["Topic 1", "Topic 2", ...]
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.8,
            max_tokens=1000
        )

        topics = self._parse_json_array(response)

        logger.info(f"Generated {len(topics)} topics for {channel}")

        return topics

    async def generate_blog_post(
        self,
        business_idea: Dict[str, Any],
        topic: str,
        min_words: int = 800
    ) -> Dict[str, Any]:
        """
        Генерация blog post.

        Args:
            business_idea: Информация о бизнесе
            topic: Тема поста
            min_words: Минимум слов

        Returns:
            Dict с blog post (title, content, meta_description, keywords)
        """
        prompt = f"""
Write a comprehensive blog post for this SaaS business.

Business: {business_idea['name']}
Topic: {topic}
Target Audience: {business_idea.get('target_audience', 'Small teams')}
Minimum words: {min_words}

Guidelines:
1. Start with an engaging hook
2. Use clear structure with H2/H3 headings
3. Include actionable tips
4. Mention the product naturally (not pushy)
5. End with a strong CTA
6. SEO-optimized with keywords
7. Write in a friendly, helpful tone

Return as JSON:
{{
    "title": "Blog post title (60 chars max)",
    "meta_description": "SEO meta description (155 chars max)",
    "keywords": ["keyword1", "keyword2", ...],
    "content": "Full markdown content with headings...",
    "cta": "Call to action text",
    "estimated_reading_time": 5
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.7,
            max_tokens=3000
        )

        post = self._parse_json_response(response)

        # Добавляем metadata
        post["topic"] = topic
        post["word_count"] = len(post.get("content", "").split())

        logger.info(f"Generated blog post: {post.get('title', topic)[:50]}...")

        return post

    async def generate_social_post(
        self,
        business_idea: Dict[str, Any],
        topic: str,
        platform: str = "twitter"
    ) -> Dict[str, Any]:
        """
        Генерация social media поста.

        Args:
            business_idea: Информация о бизнесе
            topic: Тема поста
            platform: Платформа (twitter/linkedin/reddit)

        Returns:
            Dict с social post
        """
        char_limits = {
            "twitter": 280,
            "linkedin": 3000,
            "reddit": 40000
        }

        max_chars = char_limits.get(platform, 500)

        prompt = f"""
Write an engaging {platform} post.

Business: {business_idea['name']}
Topic: {topic}
Max characters: {max_chars}

Guidelines for {platform}:
"""

        if platform == "twitter":
            prompt += """
- Short, punchy, attention-grabbing
- Use 1-2 relevant hashtags
- Include a hook in first line
- Optional thread format for complex topics
"""
        elif platform == "linkedin":
            prompt += """
- Professional but personable tone
- Share insights or lessons learned
- Use line breaks for readability
- End with a question to drive engagement
"""
        elif platform == "reddit":
            prompt += """
- Authentic, helpful, not salesy
- Provide real value upfront
- Share specific tips or experiences
- Mention product only if genuinely relevant
"""

        prompt += """
Return as JSON:
{
    "text": "Post content...",
    "hashtags": ["hashtag1", "hashtag2"],
    "image_suggestion": "Description of suggested image",
    "best_time_to_post": "morning/afternoon/evening"
}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.8,
            max_tokens=1000
        )

        post = self._parse_json_response(response)
        post["platform"] = platform
        post["topic"] = topic

        return post

    async def generate_email_copy(
        self,
        business_idea: Dict[str, Any],
        email_type: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Генерация email copy.

        Args:
            business_idea: Информация о бизнесе
            email_type: Тип email (welcome/nurture/promotion/announcement)
            context: Дополнительный контекст

        Returns:
            Dict с email content
        """
        context = context or {}

        prompt = f"""
Write a compelling email for this SaaS business.

Business: {business_idea['name']}
Email Type: {email_type}
Target Audience: {business_idea.get('target_audience', 'Small teams')}

Email should:
1. Have an attention-grabbing subject line
2. Personalized greeting
3. Clear value proposition
4. Specific CTA
5. Professional but friendly tone

Return as JSON:
{{
    "subject_line": "Email subject (50 chars max)",
    "preview_text": "Preview text shown in inbox (90 chars max)",
    "body": "Email body content in HTML...",
    "cta_text": "Call to action button text",
    "cta_url": "/signup or /dashboard",
    "ps": "Optional P.S. message"
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.7,
            max_tokens=2000
        )

        email = self._parse_json_response(response)
        email["email_type"] = email_type

        return email

    async def generate_landing_page_copy(
        self,
        business_idea: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Генерация copy для landing page.

        Args:
            business_idea: Информация о бизнесе

        Returns:
            Dict со всеми секциями landing page
        """
        prompt = f"""
Write compelling copy for a SaaS landing page.

Business: {business_idea['name']}
Tagline: {business_idea.get('tagline', '')}
Description: {business_idea['description']}
Key Features: {', '.join(business_idea.get('key_features', []))}
Pricing: {business_idea.get('pricing', 'Free trial')}

Include these sections:

Return as JSON:
{{
    "hero": {{
        "headline": "Main headline (10 words max)",
        "subheadline": "Supporting text (20 words max)",
        "cta": "Primary CTA button text"
    }},
    "problem": {{
        "headline": "Problem section headline",
        "description": "Pain points description"
    }},
    "solution": {{
        "headline": "Solution section headline",
        "description": "How product solves the problem"
    }},
    "features": [
        {{
            "title": "Feature 1",
            "description": "Feature description",
            "icon": "suggested icon name"
        }}
    ],
    "social_proof": {{
        "headline": "Social proof section",
        "testimonial_placeholders": 3
    }},
    "pricing": {{
        "headline": "Pricing headline",
        "cta": "Pricing CTA"
    }},
    "faq": [
        {{
            "question": "FAQ question",
            "answer": "FAQ answer"
        }}
    ],
    "final_cta": {{
        "headline": "Final CTA headline",
        "subheadline": "Supporting text",
        "button_text": "CTA button"
    }}
}}
"""

        response = await self.llm.generate(
            prompt,
            temperature=0.7,
            max_tokens=3000
        )

        landing_page = self._parse_json_response(response)

        logger.info("Generated landing page copy")

        return landing_page

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        # Убираем markdown code blocks если есть
        json_str = re.sub(r'^```(?:json)?\n', '', response.strip())
        json_str = re.sub(r'\n```$', '', json_str)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Response: {response[:500]}")
            return {}

    def _parse_json_array(self, response: str) -> List[str]:
        """Parse JSON array from LLM response."""
        json_str = re.sub(r'^```(?:json)?\n', '', response.strip())
        json_str = re.sub(r'\n```$', '', json_str)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback: split by newlines if not valid JSON
            lines = [
                line.strip().strip('"\',-')
                for line in response.split('\n')
                if line.strip() and not line.strip().startswith(('```', '[', ']'))
            ]
            return [line for line in lines if len(line) > 10]


# Пример использования
if __name__ == "__main__":
    import asyncio
    from agents.base.mock_llm import MockLLM

    async def main():
        llm = MockLLM()
        generator = ContentGenerator(llm=llm)

        business_idea = {
            "name": "TaskFlow AI",
            "tagline": "Project management that thinks for you",
            "description": "AI-powered PM tool for small teams",
            "target_audience": "Freelancers and teams of 2-10",
            "key_features": [
                "AI task prioritization",
                "Automatic deadline prediction",
                "Smart workflow suggestions"
            ],
            "pricing": "Free + $19/month Pro"
        }

        # Generate topics
        topics = await generator.generate_content_topics(
            business_idea,
            channel="blog",
            num_topics=5
        )

        print(f"Generated topics: {topics}")

        # Generate blog post
        if topics:
            post = await generator.generate_blog_post(
                business_idea,
                topic=topics[0],
                min_words=800
            )

            print(f"\nBlog Post: {post.get('title')}")
            print(f"Words: {post.get('word_count')}")

    asyncio.run(main())
