from data_adapter.db import BaseModel
from playhouse.postgres_ext import CharField


class Account(BaseModel):
    name = CharField(max_length=255, unique=True)
    email = CharField(max_length=255, unique=True)

    class Meta:
        db_table = "accounts"

    @classmethod
    def get_by_email(cls, email):
        return cls.select_query().where(cls.email == email).limit(1)

    @classmethod
    def get_or_create_account(cls, name, email):
        try:
            account = cls.get_by_email(email)
            if not account:
                account = cls.create(name=name, email=email)
        except Exception as e:
            raise e
        return account

    def get_details(self):
        return {
            "name": self.name,
            "email": self.email,
        }
