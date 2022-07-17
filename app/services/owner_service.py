from app.daos.owner_dao import OwnerDAO
from app.models.owner import Owner


class OwnerService:
    def __init__(self, dao: OwnerDAO):
        self.dao = dao

    def get_owner(self, owner_id):
        return self.dao.get_owner(owner_id).__dict__

    def get_owners(self):
        return [owner.__dict__ for owner in self.dao.get_owners()]

    def add_owner(self, owner: Owner):
        self.dao.add_owner(owner)

    def replace_owner(self, owner: Owner):
        self.dao.replace_owner(owner)

    def delete_owner(self, owner_id: int):
        self.dao.delete_owner(owner_id)
