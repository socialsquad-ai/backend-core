from data_adapter.db import BaseModel
from playhouse.postgres_ext import (
    CharField,
    DateTimeField,
    TextField,
)
from peewee import ForeignKeyField
from datetime import datetime, timezone
from data_adapter.user import User


class Integration(BaseModel):
    user = ForeignKeyField(User, backref="integrations")
    platform = CharField(max_length=50, null=False)  # e.g., 'instagram', 'youtube'
    access_token = TextField(null=False)
    refresh_token = TextField(null=True)  # Not all platforms provide refresh tokens
    expires_at = DateTimeField(null=True)  # When the access token expires
    token_type = CharField(max_length=50, null=False)
    scope = TextField(null=False)  # The scopes granted as a comma-separated string

    class Meta:
        db_table = "integrations"

    @classmethod
    def get_all_for_user(cls, user):
        return cls.select_query().where(cls.user == user)

    @classmethod
    def get_by_uuid_for_user(cls, uuid, user):
        return cls.select_query().where(cls.uuid == uuid, cls.user == user).limit(1)

    @classmethod
    def create_integration(
        cls,
        user,
        platform,
        access_token,
        refresh_token,
        expires_at,
        token_type,
        scope,
    ):
        return cls.create(
            user=user,
            platform=platform,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            token_type=token_type,
            scope=scope,
        )

    def get_details(self):
        return {
            "uuid": str(self.uuid),
            "platform": self.platform,
            "status": "active"
            if self.expires_at > datetime.now(timezone.utc)
            else "inactive",
            "token_type": self.token_type,
            "created_at": self.created_at,
        }
