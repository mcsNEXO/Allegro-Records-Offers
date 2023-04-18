from sqlalchemy import Column, String, Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import text
from os import environ

user = environ.get("POSTGRES_USER")
password = environ.get("POSTGRES_PASSWORD")
host = environ.get("POSTGRES_HOST")
port = environ.get("POSTGRES_PORT")
db = environ.get("POSTGRES_DB")

if not user:
    user = "postgres"
    password = "admin"
    host = "localhost"
    port = "5432"
    db = "postgres"

# Create database
SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base = declarative_base()

class Credentials(Base):
        __tablename__ = "credentials"

        id = Column(Integer, primary_key=True, index=True, autoincrement=True)

        api_imagekit_id = Column(String)
        api_imagekit_secret = Column(String)
        api_imagekit_endpoint = Column(String)

        api_azure_subscription_key = Column(String)
        api_azure_endpoint = Column(String)

        api_discogs_id = Column(String)
        api_discogs_secret = Column(String)
        api_discogs_token = Column(String)

        api_allegro_id = Column(String)
        api_allegro_secret = Column(String)
        api_allegro_token = Column(String)

class Image_Data(Base):
    __tablename__ = "image_data"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text_from_image = Column(String)
    url = Column(String)

Base.metadata.create_all(engine)

# Database scripts

def post_credentials(allegro_id: str, allegro_secret: str, allegro_token: str) -> None:
    if not all([allegro_id, allegro_secret, allegro_token]):
        raise ValueError("Allegro credentials are missing")
    
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        data_to_insert = {
            "api_imagekit_id": environ.get("API_IMAGEKIT_ID"),
            "api_imagekit_secret": environ.get("API_IMAGEKIT_SECRET"),
            "api_imagekit_endpoint": environ.get("API_IMAGEKIT_ENDPOINT"),
            "api_azure_subscription_key": environ.get("API_AZURE_SUBSCRIPTION_KEY"),
            "api_azure_endpoint": environ.get("API_AZURE_ENDPOINT"),
            "api_discogs_id": environ.get("API_DISCOGS_ID"),
            "api_discogs_secret": environ.get("API_DISCOGS_SECRET"),
            "api_discogs_token": environ.get("API_DISCOGS_TOKEN"),
            "api_allegro_id": allegro_id,
            "api_allegro_secret": allegro_secret,
            "api_allegro_token": allegro_token
        }       

        credentials_data = Credentials(**data_to_insert)
        session.add(credentials_data)
        session.commit()


def get_credentials() -> list:
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        # Get credentials from database
        row = session.query(Credentials).order_by(Credentials.id.desc()).limit(1).first()
        credentials = row.__dict__
        del credentials['_sa_instance_state']

    return credentials

def post_text_from_image(text_from_images: list) -> None:
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # Delete all rows from the table
        session.query(Image_Data).delete()

        # Create a dictionary of the data to be inserted into the image_data
        for data_item in text_from_images:
            session.add(Image_Data(text_from_image=data_item['text_from_image'], url=data_item['url']))

        session.commit()

def get_text_from_image() -> dict:
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # Get all rows from the image_data table
        rows = session.query(Image_Data).all()
        data_image = [{"text_from_image": row.text_from_image, "url": row.url} for row in rows]
        session.commit()

    return data_image

def truncate_image_data():
    Session = sessionmaker(bind=engine)

    with Session() as session:
        session.execute(text('TRUNCATE image_data'))
        session.commit()

