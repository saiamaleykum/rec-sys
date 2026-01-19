from fastapi import Depends

from src.app.repository import DataRepository
from src.app.services import RecommendationService


def get_repo() -> DataRepository:
    return DataRepository()

def get_service(repo: DataRepository = Depends(get_repo)) -> RecommendationService:
    return RecommendationService(repo)
