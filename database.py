from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy import create_engine
from config import settings
DATABASE_URL=settings.DATABASE_URL
engine=create_engine(DATABASE_URL)#oturum ile içeri girince hangi veritabanı olduğuna bakacak
Sessionlocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)#oturum açacak işlem yapmak için
Base=declarative_base()#veritabanındaki tablo için
def get_db():
    db=Sessionlocal()
    try:
        yield db
    finally:
        db.close()