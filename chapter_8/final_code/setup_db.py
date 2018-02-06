from sqlalchemy import create_engine

from temp_messenger.dependencies.users import User

engine = create_engine(
    'postgresql+psycopg2://postgres:secret@localhost/'
    'users?client_encoding=utf8'
)

User.metadata.create_all(engine)
