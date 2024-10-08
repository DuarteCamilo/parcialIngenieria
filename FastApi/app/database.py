from dotenv import load_dotenv
from peewee import *
import os

# Cargar las variables de entorno
load_dotenv()

# Configuración de la base de datos
database = MySQLDatabase(
    os.getenv('DB_NAME'),  # Nombre de la base de datos
    user=os.getenv('DB_USER'),  # Usuario
    password=os.getenv('DB_PASSWORD'),  # Contraseña
    host=os.getenv('DB_HOST')  # Host de la base de datos
)

# Modelo Newspaper (Diarios)
class NewspaperModel(Model):
    id = AutoField(primary_key=True)
    name = CharField(max_length=100)
    email_contact = CharField(max_length=100)

    class Meta:
        database = database
        table_name = "newspapers"

# Modelo Article (Artículos)
class ArticleModel(Model):
    id = AutoField(primary_key=True)
    title = CharField(max_length=200)
    content = TextField()
    newspaper_id = ForeignKeyField(NewspaperModel, backref='articles', on_delete='CASCADE')
    uploaded_at = DateTimeField()

    class Meta:
        database = database
        table_name = "articles"

# Modelo UploadHistory (Historial de Cargas)
class UploadHistoryModel(Model):
    id = AutoField(primary_key=True)
    newspaper_id = ForeignKeyField(NewspaperModel, backref='upload_history', on_delete='CASCADE')
    upload_date = DateField()
    article_count = IntegerField()

    class Meta:
        database = database
        table_name = "upload_history"

# Conectar a la base de datos y crear las tablas si no existen
def create_tables():
    with database:
        database.create_tables([NewspaperModel, ArticleModel, UploadHistoryModel])

# Ejecutar la creación de las tablas
create_tables()
