from typing import Generic, List, TypeVar

from sqlalchemy.orm import Query

from infrastructor.data.DatabaseSessionManager import DatabaseSessionManager
from infrastructor.dependency.scopes import IScoped
from models.dao.Entity import Entity

T = TypeVar('T', bound=Entity)


class Repository(Generic[T], IScoped):
    def __init__(self, database_session_manager: DatabaseSessionManager):
        self.database_session_manager: DatabaseSessionManager = database_session_manager
        self.type = self.__orig_class__.__args__[0]

    @property
    def table(self):
        return self.database_session_manager.session.query(self.type)

    def insert(self, entity: T):
        self.database_session_manager.session.add(entity)

    def first(self, **kwargs) -> T:
        query: Query = self.table.filter_by(**kwargs)
        return query.first()

    def filter_by(self, **kwargs) -> List[T]:
        query: Query = self.database_session_manager.session.query(self.type)
        return query.filter_by(**kwargs)

    def get(self) -> List[T]:
        query = self.database_session_manager.session.query(self.type)
        return query.all()

    def get_by_id(self, id: int) -> T:
        query = self.database_session_manager.session.query(self.type)
        return query.filter_by(Id=id).first()

    def update(self, id: int, update_entity: T):
        entity = self.get_by_id(id)

    def delete_by_id(self, id: int):
        entity = self.get_by_id(id)
        entity.IsDeleted = 1

    def delete(self, entity: T):
        entity.IsDeleted = 1
