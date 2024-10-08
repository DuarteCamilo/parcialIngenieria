from fastapi import APIRouter, Body
from models.article_schema import Article  # Modelo Pydantic para la validación de datos
from database import ArticleModel, UploadHistoryModel  # Modelos de la base de datos
from datetime import date, timedelta
from statistics import mean, stdev  # Importar funciones para estadísticas
from collections import Counter  # Para el manejo de frecuencias

article_route = APIRouter()

# Función para calcular el promedio, desviación estándar y coeficiente de variación
def calculate_statistics(newspaper_id: int, day_of_week: int):
    six_months_ago = date.today() - timedelta(days=180)
    upload_histories = UploadHistoryModel.select().where(
        (UploadHistoryModel.newspaper_id == newspaper_id) & 
        (UploadHistoryModel.upload_date >= six_months_ago)
    )

    # Filtrar las fechas que coinciden con el día de la semana
    article_counts = [
        history.article_count for history in upload_histories
        if history.upload_date.weekday() == day_of_week
    ]
    
    if article_counts:
        avg = mean(article_counts)
        std_dev = stdev(article_counts) if len(article_counts) > 1 else 0
        cv = (std_dev / avg) * 100 if avg > 0 else 0  # Coeficiente de variación
        return avg, std_dev, cv, article_counts  # Retorna la estadística
    return 0, 0, 0, []  # Retorna 0 si no hay conteos

# Función para calcular el rango intercuartil
def calculate_iqr(article_counts):
    q1 = article_counts[len(article_counts) // 4]  # Primer cuartil
    q3 = article_counts[3 * len(article_counts) // 4]  # Tercer cuartil
    iqr = q3 - q1  # Rango intercuartil
    return q1, q3, iqr

# Función para calcular el promedio de artículos en los últimos 6 meses para el mismo día de la semana
def calculate_average_articles(newspaper_id: int, day_of_week: int):
    six_months_ago = date.today() - timedelta(days=180)
    upload_histories = UploadHistoryModel.select().where(
        (UploadHistoryModel.newspaper_id == newspaper_id) & 
        (UploadHistoryModel.upload_date >= six_months_ago)
    )

    # Filtrar las fechas que coinciden con el día de la semana
    article_counts = [
        history.article_count for history in upload_histories
        if history.upload_date.weekday() == day_of_week
    ]
    
    if article_counts:
        return mean(article_counts), stdev(article_counts) if len(article_counts) > 1 else 0
    return 0, 0

# Ruta para crear un artículo y verificar la cantidad cargada
@article_route.post("/")
def create_article(article: Article = Body(...)):
    # Crear el artículo en la base de datos
    ArticleModel.create(
        title=article.title,
        content=article.content,
        newspaper_id=article.newspaper_id,
        uploaded_at=article.uploaded_at
    )

    # Verificar si la cantidad de artículos subidos está por debajo del promedio
    day_of_week = article.uploaded_at.weekday()  # Día de la semana (lunes = 0, domingo = 6)
    avg, std_dev, cv, article_counts = calculate_statistics(article.newspaper_id, day_of_week)
    umbral = avg * 0.8  # Umbral del 80%

    # Obtener la cantidad de artículos subidos hoy
    today_count = ArticleModel.select().where(
        (ArticleModel.newspaper_id == article.newspaper_id) & 
        (ArticleModel.uploaded_at.cast('date') == article.uploaded_at.date())
    ).count()

    # Preparar el mensaje de respuesta
    if today_count < umbral:
        # Fase 2: Análisis del coeficiente de variación
        if cv > 20:  # Considera alta variabilidad si el CV es mayor al 20%
            # Fase 2: Calcular rango intercuartil (Q1 y Q3)
            q1, q3, iqr = calculate_iqr(sorted(article_counts))
            return {
                "message": f"El diario ha subido {today_count} artículos hoy, lo cual está por debajo del umbral esperado de {umbral:.2f} artículos (80% del promedio de {avg:.2f}).",
                "variabilidad": "Alta variabilidad detectada",
                "rango_intercuartil": {
                    "Q1 (Primer cuartil)": q1,
                    "Q3 (Tercer cuartil)": q3,
                    "IQR (Rango intercuartil)": iqr
                }
            }
        else:
            # Fase 3: Revisar respecto a la tabla de distribución de frecuencias
            return {
                "message": f"El diario ha subido {today_count} artículos hoy, lo cual está por debajo del umbral esperado de {umbral:.2f} artículos (80% del promedio de {avg:.2f}).",
                "variabilidad": "Variación baja detectada, revisa la distribución de frecuencias"
            }

    return {
        "message": "Artículo creado exitosamente y cumple con el umbral esperado.",
        "estadísticas": {
            "promedio": avg,
            "desviación estándar": std_dev,
            "coeficiente de variación": cv,
            "artículos subidos hoy": today_count,
            "umbral esperado": umbral,
        }
    }

# Otras rutas necesarias para el CRUD

# Obtener un artículo por ID
@article_route.get("/{article_id}")
def get_article(article_id: int):
    article = ArticleModel.get_or_none(ArticleModel.id == article_id)
    if not article:
        return {"message": "Article not found."}
    return {
        "title": article.title,
        "content": article.content,
        "newspaper_id": article.newspaper_id,
        "uploaded_at": article.uploaded_at
    }

# Actualizar un artículo por ID
@article_route.put("/{article_id}")
def update_article(article_id: int, updated_article: Article):
    article = ArticleModel.get_or_none(ArticleModel.id == article_id)
    if not article:
        return {"message": "Article not found."}

    # Actualizar campos
    article.title = updated_article.title
    article.content = updated_article.content
    article.newspaper_id = updated_article.newspaper_id
    article.uploaded_at = updated_article.uploaded_at
    article.save()

    return {"message": "Article updated successfully"}

# Eliminar un artículo por ID
@article_route.delete("/{article_id}")
def delete_article(article_id: int):
    article = ArticleModel.get_or_none(ArticleModel.id == article_id)
    if not article:
        return {"message": "Article not found."}
    
    article.delete_instance()
    return {"message": "Article deleted successfully"}

# Reporte semanal por periódico
@article_route.get("/reporte/semanal")
def get_weekly_report(newspaper_id: int):
    today = date.today()
    week_data = []
    total_articles = 0

    for i in range(7):
        date_to_check = today - timedelta(days=i)
        article_count = ArticleModel.select().where(
            (ArticleModel.newspaper_id == newspaper_id) & 
            (ArticleModel.uploaded_at.cast('date') == date_to_check)
        ).count()

        total_articles += article_count
        week_data.append({
            "fecha": date_to_check.isoformat(),
            "cantidad_artículos": article_count
        })

    return {
        "message": f"Reporte de artículos subidos para el periódico con ID {newspaper_id} durante la última semana. Total de artículos subidos: {total_articles}.",
        "reporte": week_data
    }

# Reporte semanal para todos los periódicos
@article_route.get("/reporte/semanal/todos")
def get_weekly_report_all():
    today = date.today()
    week_data = []
    total_articles = 0

    for i in range(7):
        date_to_check = today - timedelta(days=i)
        article_count = ArticleModel.select().where(
            ArticleModel.uploaded_at.cast('date') == date_to_check
        ).count()

        total_articles += article_count
        week_data.append({
            "fecha": date_to_check.isoformat(),
            "cantidad_artículos": article_count
        })

    return {
        "message": f"Reporte de artículos subidos en la última semana para todos los periódicos. Total de artículos subidos: {total_articles}.",
        "reporte": week_data
    }
