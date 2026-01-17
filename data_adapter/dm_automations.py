from peewee import BooleanField, CharField, ForeignKeyField, TextField

from data_adapter.db import BaseModel
from data_adapter.integration import Integration


class DmAutomationRule(BaseModel):
    integration = ForeignKeyField(Integration, backref="dm_automation_rules")
    post_id = CharField(max_length=255, null=True)
    trigger_type = CharField(max_length=50)
    match_type = CharField(max_length=50, null=True)
    trigger_text = TextField()
    dm_response = TextField()
    comment_reply = TextField(null=True)
    is_active = BooleanField(default=True)

    class Meta:
        db_table = "dm_automation_rules"

    @classmethod
    def get_by_integration_and_trigger(cls, integration_id: int, trigger_type: str):
        return cls.select_query().where(
            cls.integration == integration_id,
            cls.trigger_type == trigger_type,
            cls.is_active == True,
        )

    @classmethod
    def get_by_post_id(cls, post_id: str):
        return cls.select_query().where(
            cls.post_id == post_id,
            cls.trigger_type == "comment",
            cls.is_active == True,
        )

    def get_details(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "integration_id": self.integration.id,
            "post_id": self.post_id,
            "trigger_type": self.trigger_type,
            "match_type": self.match_type,
            "trigger_text": self.trigger_text,
            "dm_response": self.dm_response,
            "comment_reply": self.comment_reply,
            "is_active": self.is_active,
        }
