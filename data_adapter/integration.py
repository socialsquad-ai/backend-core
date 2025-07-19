from data_adapter.db import BaseModel
from playhouse.postgres_ext import CharField, DateTimeField, TextField, JSONField
from peewee import ForeignKeyField
from datetime import datetime, timezone
from data_adapter.user import User


class Integration(BaseModel):
    user = ForeignKeyField(User, backref="integrations")
    platform_user_id = CharField(
        max_length=50, null=False
    )  # e.g., 'instagram_user_id', 'youtube_channel_id'
    platform = CharField(max_length=50, null=False)  # e.g., 'instagram', 'youtube'
    access_token = TextField(null=False)
    refresh_token = TextField(null=True)
    expires_at = DateTimeField(null=True)  # When the access token expires
    token_type = CharField(max_length=50, null=False)
    scopes = JSONField(null=False)  # The scopes granted
    refresh_token_expires_at = DateTimeField(null=True)

    class Meta:
        db_table = "integrations"

    @classmethod
    def get_all_for_user(cls, user):
        return cls.select_query().where(cls.user == user)

    @classmethod
    def get_by_uuid_for_user(cls, uuid, user):
        return cls.select_query().where(cls.uuid == uuid, cls.user == user).limit(1)

    @classmethod
    def delete_by_uuid_for_user(cls, uuid, user):
        return cls.soft_delete().where(cls.uuid == uuid, cls.user == user).execute()

    @classmethod
    def create_integration(
        cls,
        user,
        platform_user_id,
        platform,
        access_token,
        expires_at,
        token_type,
        scopes,
        refresh_token=None,
        refresh_token_expires_at=None,
    ):
        return cls.create(
            user=user,
            platform_user_id=platform_user_id,
            platform=platform,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            token_type=token_type,
            scopes=scopes,
            refresh_token_expires_at=refresh_token_expires_at,
        )

    def get_details(self):
        return {
            "uuid": str(self.uuid),
            "platform": self.platform,
            "status": "active" if self.expires_at > datetime.now() else "inactive",
            "token_type": self.token_type,
            "created_at": self.created_at.isoformat(),
        }
