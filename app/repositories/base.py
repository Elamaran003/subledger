from sqlalchemy.orm import Session


class BaseRepository:
    """Repositories do data access only. No business rules live here."""

    def __init__(self, db: Session):
        self.db = db

    def _add(self, obj):
        self.db.add(obj)
        self.db.flush()  # assigns PKs, does not commit
        return obj

    def save(self, obj):
        self.db.flush()
        return obj

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
