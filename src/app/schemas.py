from pydantic import BaseModel
from typing import List


class RecommendationResponse(BaseModel):
    uid: int
    products: List[int]
    