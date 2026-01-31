from datetime import datetime, timezone

from peewee import ForeignKeyField
from playhouse.postgres_ext import CharField, DateTimeField, JSONField, TextField

from data_adapter.db import BaseModel
from data_adapter.user import User


class Integration(BaseModel):
    user = ForeignKeyField(User, backref="integrations")
    platform_user_id = CharField(max_length=50, null=False)  # e.g., 'instagram_user_id', 'youtube_channel_id'
    platform = CharField(max_length=50, null=False)  # e.g., 'instagram', 'youtube'
    access_token = TextField(null=False)
    refresh_token = TextField(null=True)
    expires_at = DateTimeField(null=True)  # When the access token expires
    token_type = CharField(max_length=50, null=False)
    scopes = JSONField(null=False)  # The scopes granted
    refresh_token_expires_at = DateTimeField(null=True)
    platform_username = CharField(max_length=255, null=True)

    class Meta:
        db_table = "integrations"
        indexes = ((("platform_user_id", "platform"), True),)

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
    def get_by_platform_user_id(cls, platform_user_id: str, platform: str):
        """Get integration by platform user ID and platform type."""
        return cls.select_query().where(cls.platform_user_id == platform_user_id, cls.platform == platform).first()

    @classmethod
    def get_by_user_id_and_platform(cls, user_id: str, platform: str):
        """Get integration by user ID and platform type."""
        return cls.select_query().join(User).where(User.id == user_id, cls.platform == platform).first()

    @classmethod
    def create_or_update_integration(
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
        platform_username=None,
    ):
        # We use select() instead of select_query() to include potentially soft-deleted integrations
        integration = cls.select().where(cls.platform_user_id == platform_user_id, cls.platform == platform).first()
        if integration:
            integration.user = user
            integration.access_token = access_token
            integration.expires_at = expires_at
            integration.token_type = token_type
            integration.scopes = scopes
            integration.refresh_token = refresh_token
            integration.refresh_token_expires_at = refresh_token_expires_at
            integration.platform_username = platform_username
            integration.is_deleted = False
            integration.save()
            return integration

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
            platform_username=platform_username,
        )

    def get_details(self):
        now = datetime.now(timezone.utc)
        expires_at = self.expires_at

        # Make expires_at aware if it isn't, assuming UTC
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        is_active = True
        if expires_at:
             is_active = expires_at > now

        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "user_id": self.user.id,
            "platform": self.platform,
            "platform_user_id": self.platform_user_id,
            "platform_username": self.platform_username,
            "status": "active" if is_active else "inactive",
            "is_active": is_active,
            "token_type": self.token_type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else self.created_at.isoformat(),
        }
