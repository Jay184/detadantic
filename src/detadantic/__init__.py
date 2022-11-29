import os
from typing import Optional, Union
from deta import Deta, _Base
from pydantic import BaseModel, Field
from datetime import datetime


class DetaModel(BaseModel):
    key: Optional[str] = None

    _project_key: Optional[str] = None
    __base_name__: str = ''

    @classmethod
    def set_project_key(cls, project_key: str):
        cls._project_key = project_key

    @classmethod
    def get_base(cls, name: Optional[str] = None) -> Optional[_Base]:
        project_key = cls._project_key or os.environ.get('DETA_PROJECT_KEY')

        if project_key:
            deta = Deta(project_key)
            base = deta.Base(name or cls.db_name)
            return base

    @classmethod
    @property
    def db_name(cls) -> str:
        if hasattr(cls, '__base_name__') and cls.__base_name__:
            return cls.__base_name__
        return cls.__name__.lower()

    @classmethod
    def first(cls, query: Optional[dict] = None):
        db = cls.get_base()
        res = db.fetch(query, limit=1) # TODO how to handle 1MB limit?
        return cls.parse_obj(res.items[0]) if len(res.items) else None

    @classmethod
    def first_or_fail(cls, query: Optional[dict] = None):
        first = cls.first(query)
        if first is None:
            raise Exception('No entries')
        return first

    @classmethod
    def get(cls, key: str):
        db = cls.get_base()
        data = db.get(key)
        return cls.parse_obj(data) if data else None

    @classmethod
    def get_or_fail(cls, key: str):
        entry = cls.get(key)
        if entry is None:
            raise Exception('No entries')
        return entry

    @classmethod
    def enumerate_fetch(cls,
                        query: Optional[dict] = None,
                        limit: int = 1000):
        db = cls.get_base()
        res = db.fetch(query, limit=limit)
        yield from (cls.parse_obj(obj) for obj in res.items)
        
        while res.last:
            res = db.fetch(query, limit=limit, last=res.last)
            yield from (cls.parse_obj(obj) for obj in res.items)

    @classmethod
    def fetch(cls,
              query: Optional[dict] = None,
              limit: int = 1000):
        return list(cls.enumerate_fetch(query, limit))

    @classmethod
    def convert_from(cls, source: Union[dict, BaseModel],
                     update: Optional[dict] = None):
        if isinstance(source, BaseModel):
            obj = cls.from_orm(source)
        elif isinstance(source, dict):
            obj = cls.parse_obj(source)

        return obj
        
    @classmethod
    def create(cls, source: Union[dict, BaseModel],
               *,
               expire_in: Optional[int] = None,
               expire_at: Union[None, int, float, datetime] = None):
        obj = cls.convert_from(source)
        if obj and obj.save(expire_in=expire_in, expire_at=expire_at):
            return obj
            
    @classmethod
    def count(cls, query: Optional[dict] = None) -> int:
        return len(cls.fetch(query))

    @classmethod
    def truncate(cls, query: Optional[dict] = None):
        db = cls.get_base()
        for item in cls.enumerate_fetch(query):
            db.delete(item.key)
    
    @classmethod
    def delete(cls, key: str):
        db = cls.get_base()
        db.delete(key)
    
    @classmethod
    def update(cls, key: str,
               updates: dict,
               *,
               expire_in: Optional[int] = None,
               expire_at: Union[None, int, float, datetime] = None):
        db = cls.get_base()
        db.update(updates, key, expire_in=expire_in, expire_at=expire_at)
    
    @classmethod
    def update_all(cls, updates: dict,
                   query: Optional[dict] = None,
                   *,
                   expire_in: Optional[int] = None,
                   expire_at: Union[None, int, float, datetime] = None):
        db = cls.get_base()
        for item in cls.enumerate_fetch(query):
            db.update(updates, item.key,
                      expire_in=expire_in, expire_at=expire_at)

    @classmethod
    def expire(cls, key: str,
               *,
               expire_in: Optional[int] = None,
               expire_at: Union[None, int, float, datetime] = None):
        db = cls.get_base()
        db.update({}, key, expire_in=expire_in, expire_at=expire_at)

    def save(self, *,
             expire_in: Optional[int] = None,
             expire_at: Union[None, int, float, datetime] = None,
             exclude_none: bool = False,
             exclude_unset: bool = False):
        db = self.get_base()
        data = self.dict(
            exclude_none=exclude_none,
            exclude_unset=exclude_unset,
        )

        returned_data = db.put(data, expire_in=expire_in, expire_at=expire_at)

        for key, value in returned_data.items():
            if hasattr(self, key):
                setattr(self, key, value)

        return self.parse_obj(returned_data)

    def delete(self):
        if self.key:
            db = self.get_base()
            db.delete(self.key)

    def refresh(self):
        if self.key:
            db = self.get_base()
            data = db.get(self.key)
            
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
