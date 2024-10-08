from pydantic import BaseModel
from datetime import datetime

class Article(BaseModel):
    id: int
    title: str
    content: str
    newspaper_id: int
    uploaded_at: datetime
