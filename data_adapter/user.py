from data_adapter.db import BaseModel
from playhouse.postgres_ext import CharField
import datetime


class User(BaseModel):
    email = CharField(unique=True)
    first_name = CharField()
    last_name = CharField()
    password = CharField(null=True)
    status = CharField(default="pending")
    timezone = CharField(null=True)

    class Meta:
        db_table = "users"

    @classmethod
    def get_by_email(cls, email):
        return cls.select_query().where(cls.email == email)

    @classmethod
    def get_by_pk(cls, pk):
        return cls.select_query().where(cls.id == pk).limit(1)[0]

    @classmethod
    def get_or_create_user(cls, email, timezone, password):
        user, is_created = cls.get_or_create(email=email)
        if not is_created:  # Case when a deleted user is re-invited
            user.status = "active"
        else:
            name = email.split("@")[0]
            # Since we are not asking for first and last name, creating it from
            # email and separating by dot
            names = name.split(".")
            first_name = names[0]
            last_name = ".".join(names[1:]) if len(names) > 1 else ""
            user.first_name = first_name
            user.last_name = last_name
            user.timezone = timezone
            user.password = password
            user.updated_at = datetime.datetime.utcnow()
            user.status = "active"
        user.save()
        return user

    def get_details(self):
        return {
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "timezone": self.timezone,
        }

    @classmethod
    def get_all_users(cls):
        return cls.select_query().limit(100)
