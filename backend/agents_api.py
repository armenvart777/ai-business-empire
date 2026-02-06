"""
Agents API - FastAPI backend для вызова AI агентов из веб-интерфейса.

Endpoints:
- POST /api/agents/scan-trends - запустить Trend Scanner
- POST /api/agents/generate-ideas - запустить Business Generator
- POST /api/agents/create-mvp - запустить Developer Agent
- POST /api/agents/create-marketing - запустить Marketing Agent
- POST /api/agents/create-sales - запустить Sales Agent
- POST /api/agents/full-pipeline - запустить весь pipeline
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime
import os
import sys

# Добавляем parent directory в path для импорта агентов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.trend_scanner.agent import TrendScannerAgent
from agents.business_generator.agent import BusinessGeneratorAgent
from agents.developer.agent import DeveloperAgent
from agents.marketing.agent import MarketingAgent
from agents.sales.agent import SalesAgent


# FastAPI app
app = FastAPI(
    title="AI Business Empire - Agents API",
    description="API для управления AI-агентами",
    version="1.0.0"
)

# CORS middleware (для доступа из веб-интерфейса)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production: укажите конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

# In-memory storage для job statuses
# В production: использовать Redis или database
jobs_storage = {}


# === Pydantic Models ===

class TrendScanRequest(BaseModel):
    sources: List[str] = ["google_trends", "reddit", "product_hunt"]
    min_score: int = 60
    limit: int = 20


class BusinessGenerateRequest(BaseModel):
    trend_ids: Optional[List[str]] = None  # Если None, берем последние trends
    ideas_per_trend: int = 5
    min_priority_score: int = 70


class MVPCreateRequest(BaseModel):
    business_id: str
    auto_deploy: bool = True
    auto_merge: bool = True


class MarketingCreateRequest(BaseModel):
    business_id: str
    deployment_url: str
    duration_weeks: int = 4
    channels: List[str] = ["blog", "email", "social"]
    budget: int = 500


class SalesCreateRequest(BaseModel):
    business_id: str
    deployment_url: str
    target_mrr: int = 5000
    channels: List[str] = ["email", "demo", "chat"]
    automation_level: str = "high"


class FullPipelineRequest(BaseModel):
    trend_sources: List[str] = ["google_trends", "reddit"]
    min_trend_score: int = 70
    ideas_per_trend: int = 3
    min_idea_score: int = 75
    auto_deploy: bool = True
    marketing_budget: int = 500
    target_mrr: int = 5000


class JobStatus(BaseModel):
    job_id: str
    status: str  # pending, running, completed, failed
    agent_type: str
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# === Helper Functions ===

def create_job(agent_type: str) -> str:
    """Создать новый job и вернуть ID."""
    job_id = f"{agent_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    jobs_storage[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "agent_type": agent_type,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "result": None,
        "error": None
    }

    return job_id


def update_job(job_id: str, status: str, result: Any = None, error: str = None):
    """Обновить статус job."""
    if job_id in jobs_storage:
        jobs_storage[job_id]["status"] = status

        if status in ["completed", "failed"]:
            jobs_storage[job_id]["completed_at"] = datetime.now().isoformat()

        if result:
            jobs_storage[job_id]["result"] = result

        if error:
            jobs_storage[job_id]["error"] = error


async def load_latest_trends() -> List[Dict[str, Any]]:
    """Загрузить последние trends из data/trends/."""
    import json
    from pathlib import Path

    trends_dir = Path("data/trends")
    latest_file = trends_dir / "latest.json"

    if latest_file.exists():
        with open(latest_file, "r") as f:
            data = json.load(f)
            return data.get("trends", [])

    return []


async def load_business_idea(business_id: str) -> Optional[Dict[str, Any]]:
    """Загрузить бизнес-идею по ID."""
    import json
    from pathlib import Path

    # Check approved ideas
    approved_dir = Path("data/businesses/approved")

    if approved_dir.exists():
        for file in approved_dir.glob("*.json"):
            with open(file, "r") as f:
                idea = json.load(f)
                if idea.get("id") == business_id:
                    return idea

    # Check all ideas
    ideas_dir = Path("data/businesses")
    latest_file = ideas_dir / "latest.json"

    if latest_file.exists():
        with open(latest_file, "r") as f:
            data = json.load(f)
            for idea in data.get("ideas", []):
                if idea.get("id") == business_id:
                    return idea

    return None


# === API Endpoints ===

@app.get("/")
async def root():
    """Health check."""
    return {
        "service": "AI Business Empire - Agents API",
        "status": "running",
        "version": "1.0.0",
        "agents_available": [
            "trend-scanner",
            "business-generator",
            "developer",
            "marketing",
            "sales"
        ]
    }


@app.get("/api/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Получить статус job."""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs_storage[job_id]


@app.get("/api/jobs", response_model=List[JobStatus])
async def list_jobs(agent_type: Optional[str] = None, limit: int = 50):
    """Получить список всех jobs."""
    jobs = list(jobs_storage.values())

    if agent_type:
        jobs = [j for j in jobs if j["agent_type"] == agent_type]

    # Sort by created_at (newest first)
    jobs.sort(key=lambda x: x["created_at"], reverse=True)

    return jobs[:limit]


@app.post("/api/agents/scan-trends")
async def scan_trends(request: TrendScanRequest, background_tasks: BackgroundTasks):
    """
    Запустить Trend Scanner Agent.

    Возвращает job_id для отслеживания статуса.
    """
    job_id = create_job("trend-scanner")

    async def run_trend_scanner():
        try:
            update_job(job_id, "running")

            agent = TrendScannerAgent()

            trends = await agent.scan_trends(
                sources=request.sources,
                min_score=request.min_score,
                limit=request.limit
            )

            update_job(job_id, "completed", result={
                "trends_count": len(trends),
                "trends": trends
            })

        except Exception as e:
            logger.error(f"Trend scanner failed: {e}")
            update_job(job_id, "failed", error=str(e))

    background_tasks.add_task(run_trend_scanner)

    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Trend scanner started"
    }


@app.post("/api/agents/generate-ideas")
async def generate_ideas(request: BusinessGenerateRequest, background_tasks: BackgroundTasks):
    """
    Запустить Business Generator Agent.

    Возвращает job_id для отслеживания статуса.
    """
    job_id = create_job("business-generator")

    async def run_business_generator():
        try:
            update_job(job_id, "running")

            # Load trends
            if request.trend_ids:
                # TODO: Load specific trends by IDs
                trends = await load_latest_trends()
            else:
                trends = await load_latest_trends()

            if not trends:
                raise Exception("No trends found. Run trend scanner first.")

            agent = BusinessGeneratorAgent()

            ideas = await agent.generate_business_ideas(
                trends=trends,
                ideas_per_trend=request.ideas_per_trend,
                min_priority_score=request.min_priority_score
            )

            update_job(job_id, "completed", result={
                "ideas_count": len(ideas),
                "ideas": ideas
            })

        except Exception as e:
            logger.error(f"Business generator failed: {e}")
            update_job(job_id, "failed", error=str(e))

    background_tasks.add_task(run_business_generator)

    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Business generator started"
    }


@app.post("/api/agents/create-mvp")
async def create_mvp(request: MVPCreateRequest, background_tasks: BackgroundTasks):
    """
    Запустить Developer Agent для создания MVP.

    Возвращает job_id для отслеживания статуса.
    """
    job_id = create_job("developer")

    async def run_developer():
        try:
            update_job(job_id, "running")

            # Load business idea
            business_idea = await load_business_idea(request.business_id)

            if not business_idea:
                raise Exception(f"Business idea {request.business_id} not found")

            agent = DeveloperAgent()

            result = await agent.create_mvp(
                business_idea=business_idea,
                auto_deploy=request.auto_deploy,
                auto_merge=request.auto_merge
            )

            update_job(job_id, "completed", result=result)

        except Exception as e:
            logger.error(f"Developer agent failed: {e}")
            update_job(job_id, "failed", error=str(e))

    background_tasks.add_task(run_developer)

    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Developer agent started"
    }


@app.post("/api/agents/create-marketing")
async def create_marketing(request: MarketingCreateRequest, background_tasks: BackgroundTasks):
    """
    Запустить Marketing Agent.

    Возвращает job_id для отслеживания статуса.
    """
    job_id = create_job("marketing")

    async def run_marketing():
        try:
            update_job(job_id, "running")

            # Load business idea
            business_idea = await load_business_idea(request.business_id)

            if not business_idea:
                raise Exception(f"Business idea {request.business_id} not found")

            agent = MarketingAgent()

            campaign = await agent.create_marketing_campaign(
                business_idea=business_idea,
                deployment_url=request.deployment_url,
                duration_weeks=request.duration_weeks,
                channels=request.channels,
                budget=request.budget
            )

            update_job(job_id, "completed", result=campaign)

        except Exception as e:
            logger.error(f"Marketing agent failed: {e}")
            update_job(job_id, "failed", error=str(e))

    background_tasks.add_task(run_marketing)

    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Marketing agent started"
    }


@app.post("/api/agents/create-sales")
async def create_sales(request: SalesCreateRequest, background_tasks: BackgroundTasks):
    """
    Запустить Sales Agent.

    Возвращает job_id для отслеживания статуса.
    """
    job_id = create_job("sales")

    async def run_sales():
        try:
            update_job(job_id, "running")

            # Load business idea
            business_idea = await load_business_idea(request.business_id)

            if not business_idea:
                raise Exception(f"Business idea {request.business_id} not found")

            agent = SalesAgent()

            sales_system = await agent.create_sales_system(
                business_idea=business_idea,
                deployment_url=request.deployment_url,
                target_mrr=request.target_mrr,
                channels=request.channels,
                automation_level=request.automation_level
            )

            update_job(job_id, "completed", result=sales_system)

        except Exception as e:
            logger.error(f"Sales agent failed: {e}")
            update_job(job_id, "failed", error=str(e))

    background_tasks.add_task(run_sales)

    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Sales agent started"
    }


@app.post("/api/agents/full-pipeline")
async def full_pipeline(request: FullPipelineRequest, background_tasks: BackgroundTasks):
    """
    Запустить весь pipeline: trends → ideas → MVP → marketing → sales.

    Возвращает job_id для отслеживания статуса.
    """
    job_id = create_job("full-pipeline")

    async def run_full_pipeline():
        try:
            update_job(job_id, "running")

            result = {
                "trends": [],
                "ideas": [],
                "mvp": None,
                "marketing": None,
                "sales": None
            }

            # 1. Scan trends
            logger.info("Step 1/5: Scanning trends...")
            trend_agent = TrendScannerAgent()
            trends = await trend_agent.scan_trends(
                sources=request.trend_sources,
                min_score=request.min_trend_score,
                limit=10
            )
            result["trends"] = trends

            if not trends:
                raise Exception("No trends found")

            # 2. Generate ideas
            logger.info("Step 2/5: Generating business ideas...")
            business_agent = BusinessGeneratorAgent()
            ideas = await business_agent.generate_business_ideas(
                trends=trends[:3],  # Top 3 trends
                ideas_per_trend=request.ideas_per_trend,
                min_priority_score=request.min_idea_score
            )
            result["ideas"] = ideas

            if not ideas:
                raise Exception("No viable business ideas generated")

            # 3. Create MVP for top idea
            top_idea = ideas[0]
            logger.info(f"Step 3/5: Creating MVP for {top_idea['name']}...")
            developer_agent = DeveloperAgent()
            mvp = await developer_agent.create_mvp(
                business_idea=top_idea,
                auto_deploy=request.auto_deploy,
                auto_merge=True
            )
            result["mvp"] = mvp

            deployment_url = mvp.get("deployment", {}).get("url", "")

            if not deployment_url:
                logger.warning("No deployment URL, skipping marketing and sales")
                update_job(job_id, "completed", result=result)
                return

            # 4. Create marketing campaign
            logger.info("Step 4/5: Creating marketing campaign...")
            marketing_agent = MarketingAgent()
            marketing = await marketing_agent.create_marketing_campaign(
                business_idea=top_idea,
                deployment_url=deployment_url,
                duration_weeks=4,
                channels=["blog", "email", "social"],
                budget=request.marketing_budget
            )
            result["marketing"] = marketing

            # 5. Setup sales system
            logger.info("Step 5/5: Setting up sales system...")
            sales_agent = SalesAgent()
            sales = await sales_agent.create_sales_system(
                business_idea=top_idea,
                deployment_url=deployment_url,
                target_mrr=request.target_mrr,
                channels=["email", "demo", "chat"],
                automation_level="high"
            )
            result["sales"] = sales

            logger.info("✅ Full pipeline completed!")

            update_job(job_id, "completed", result=result)

        except Exception as e:
            logger.error(f"Full pipeline failed: {e}")
            update_job(job_id, "failed", error=str(e))

    background_tasks.add_task(run_full_pipeline)

    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Full pipeline started. This will take 20-60 minutes."
    }


# === Main ===

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
