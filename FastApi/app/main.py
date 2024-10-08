from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import database as connection  # Tu conexión a la base de datos
from routes.newspaper import newspaper_route  # Ruta para los diarios
from routes.article import article_route  # Ruta para los artículos
from routes.upload_history import upload_history_route  # Ruta para el historial de cargas

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Abrir la conexión a la base de datos al iniciar la app
    if connection.is_closed():
        connection.connect()

    try:
        yield  # Aquí yield permite que la app se ejecute mientras está abierta la conexión

    finally:
        # Cerrar la conexión a la base de datos cuando se termine la app
        if not connection.is_closed():
            connection.close()

# Crear la instancia de FastAPI y manejar el ciclo de vida de la app
app = FastAPI(lifespan=lifespan)

# Incluir las rutas necesarias para el proyecto
app.include_router(newspaper_route, prefix="/newspapers", tags={"newspapers"})
app.include_router(article_route, prefix="/articles", tags={"articles"})
app.include_router(upload_history_route, prefix="/upload-history", tags={"upload_history"})
