from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends

from src.app.repository import DataRepository
from src.app.services import RecommendationService
from src.app.schemas import RecommendationResponse
from src.app.dependencies import get_service
from src.app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    repo = DataRepository()
    repo.load_from_csv(settings.csv_data_path)
    temp_service = RecommendationService(repo)
    repo.set_global_top(temp_service.calculate_global_top())
    yield

app = FastAPI(
    title="21vek API",
    lifespan=lifespan
)

@app.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    user_id: int,
    service: RecommendationService = Depends(get_service)
):
    return {
        "uid": user_id,
        "products": service.get_recommendations(user_id)
    }
