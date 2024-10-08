from fastapi import APIRouter, Body
from models.upload_history_schema import UploadHistory  # Modelo Pydantic
from database import UploadHistoryModel  # Modelo de la base de datos

upload_history_route = APIRouter()

@upload_history_route.post("/")
def create_upload_history(upload_history: UploadHistory = Body(...)):
    UploadHistoryModel.create(
        newspaper_id=upload_history.newspaper_id, 
        upload_date=upload_history.upload_date, 
        article_count=upload_history.article_count
    )
    return {"message": "Upload history created successfully"}

@upload_history_route.get("/")
def get_upload_histories():
    histories = UploadHistoryModel.select().dicts()
    return list(histories)

@upload_history_route.get("/{history_id}")
def get_upload_history(history_id: int):
    try:
        history = UploadHistoryModel.get(UploadHistoryModel.id == history_id)
        return history
    except UploadHistoryModel.DoesNotExist:
        return {"error": "Upload history not found"}

@upload_history_route.put("/{history_id}")
def update_upload_history(history_id: int, upload_history: UploadHistory = Body(...)):
    try:
        existing_history = UploadHistoryModel.get(UploadHistoryModel.id == history_id)
        existing_history.newspaper_id = upload_history.newspaper_id
        existing_history.upload_date = upload_history.upload_date
        existing_history.article_count = upload_history.article_count
        existing_history.save()
        return {"message": "Upload history updated successfully"}
    except UploadHistoryModel.DoesNotExist:
        return {"error": "Upload history not found"}

@upload_history_route.delete("/{history_id}")
def delete_upload_history(history_id: int):
    rows_deleted = UploadHistoryModel.delete().where(UploadHistoryModel.id == history_id).execute()
    if rows_deleted:
        return {"message": "Upload history deleted successfully"}
    else:
        return {"error": "Upload history not found"}
