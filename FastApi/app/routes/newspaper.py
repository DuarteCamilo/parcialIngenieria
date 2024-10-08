from fastapi import APIRouter, Body
from models.newspaper_schema import Newspaper  # Modelo Pydantic
from database import NewspaperModel  # Modelo de la base de datos

newspaper_route = APIRouter()

@newspaper_route.post("/")
def create_newspaper(newspaper: Newspaper = Body(...)):
    NewspaperModel.create(
        name=newspaper.name, 
        email_contact=newspaper.email_contact
    )
    return {"message": "Newspaper created successfully"}

@newspaper_route.get("/")
def get_newspapers():
    newspapers = NewspaperModel.select().dicts()
    return list(newspapers)

@newspaper_route.get("/{newspaper_id}")
def get_newspaper(newspaper_id: int):
    try:
        newspaper = NewspaperModel.get(NewspaperModel.id == newspaper_id)
        return newspaper
    except NewspaperModel.DoesNotExist:
        return {"error": "Newspaper not found"}

@newspaper_route.put("/{newspaper_id}")
def update_newspaper(newspaper_id: int, newspaper: Newspaper = Body(...)):
    try:
        existing_newspaper = NewspaperModel.get(NewspaperModel.id == newspaper_id)
        existing_newspaper.name = newspaper.name
        existing_newspaper.email_contact = newspaper.email_contact
        existing_newspaper.save()
        return {"message": "Newspaper updated successfully"}
    except NewspaperModel.DoesNotExist:
        return {"error": "Newspaper not found"}

@newspaper_route.delete("/{newspaper_id}")
def delete_newspaper(newspaper_id: int):
    rows_deleted = NewspaperModel.delete().where(NewspaperModel.id == newspaper_id).execute()
    if rows_deleted:
        return {"message": "Newspaper deleted successfully"}
    else:
        return {"error": "Newspaper not found"}
