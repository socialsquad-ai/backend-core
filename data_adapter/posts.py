from data_adapter.db import BaseModel
from playhouse.postgres_ext import CharField, TimeField, BooleanField, TextField
from peewee import ForeignKeyField
from data_adapter.integration import Integration


class Post(BaseModel):
    post_id = CharField(max_length=255, unique=True)
    integration = ForeignKeyField(Integration, backref="posts")
    ignore_instructions = TextField(default="")
    engagement_enabled = BooleanField(default=False)
    # Defaulting engagement period to 12:00 PM - 2:00 PM
    engagement_start_hours = TimeField(default="12:00")
    engagement_end_hours = TimeField(default="14:00")

    class Meta:
        db_table = "posts"

    @classmethod
    def get_by_post_id(cls, post_id):
        return cls.select_query().where(cls.post_id == post_id).limit(1)

    @classmethod
    def get_by_integration(cls, integration):
        return cls.select_query().where(cls.integration == integration)

    def get_details(self):
        return {
            "post_id": self.post_id,
            "integration": self.integration.get_details(),
            "ignore_instructions": self.ignore_instructions,
            "engagement_enabled": self.engagement_enabled,
            "engagement_start_hours": self.engagement_start_hours,
            "engagement_end_hours": self.engagement_end_hours,
        }
