from pydantic import BaseModel
from datetime import date

class UploadHistory(BaseModel):
    id: int
    newspaper_id: int
    upload_date: date
    article_count: int
