from fastapi import APIRouter, Body
from models.article_schema import Article  # Modelo Pydantic
from database import ArticleModel  # Modelo de la base de datos

article_route = APIRouter()

@article_route.post("/")
def create_article(article: Article = Body(...)):
    ArticleModel.create(
        title=article.title, 
        content=article.content, 
        newspaper_id=article.newspaper_id,
        uploaded_at=article.uploaded_at
    )
    return {"message": "Article created successfully"}

@article_route.get("/")
def get_articles():
    articles = ArticleModel.select().dicts()
    return list(articles)

@article_route.get("/{article_id}")
def get_article(article_id: int):
    try:
        article = ArticleModel.get(ArticleModel.id == article_id)
        return article
    except ArticleModel.DoesNotExist:
        return {"error": "Article not found"}

@article_route.put("/{article_id}")
def update_article(article_id: int, article: Article = Body(...)):
    try:
        existing_article = ArticleModel.get(ArticleModel.id == article_id)
        existing_article.title = article.title
        existing_article.content = article.content
        existing_article.newspaper_id = article.newspaper_id
        existing_article.uploaded_at = article.uploaded_at
        existing_article.save()
        return {"message": "Article updated successfully"}
    except ArticleModel.DoesNotExist:
        return {"error": "Article not found"}

@article_route.delete("/{article_id}")
def delete_article(article_id: int):
    rows_deleted = ArticleModel.delete().where(ArticleModel.id == article_id).execute()
    if rows_deleted:
        return {"message": "Article deleted successfully"}
    else:
        return {"error": "Article not found"}
