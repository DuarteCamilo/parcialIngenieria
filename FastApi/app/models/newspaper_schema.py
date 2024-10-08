from pydantic import BaseModel

class Newspaper(BaseModel):
    id: int
    name: str
    email_contact: str
