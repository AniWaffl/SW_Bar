from databases import Database
from support.db.base import database


class BaseRepository:
    database: Database = database

    def change_database(self, database: Database):
        self.database = database
