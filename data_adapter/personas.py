from data_adapter.db import BaseModel
from playhouse.postgres_ext import CharField, TextField, ForeignKeyField
from data_adapter.account import Account


class PersonaTemplate(BaseModel):
    name = CharField()
    description = TextField()
    tone = CharField()
    style = CharField()
    instructions = TextField()

    class Meta:
        db_table = "persona_templates"

    @classmethod
    def get_all_templates(cls):
        return cls.select_query().limit(100)

    def get_details(self):
        return {
            "uuid": str(self.uuid),
            "name": self.name,
            "description": self.description,
            "tone": self.tone,
            "style": self.style,
            "instructions": self.instructions,
        }


class Persona(BaseModel):
    name = CharField()
    tone = CharField()
    style = CharField()
    instructions = TextField()
    personal_details = TextField()
    account = ForeignKeyField(Account, backref="personas")

    class Meta:
        db_table = "personas"

    @classmethod
    def create_persona(cls, account, name, tone, style, instructions, personal_details):
        persona = cls.create(
            account=account,
            name=name,
            tone=tone,
            style=style,
            instructions=instructions,
            personal_details=personal_details,
        )
        return persona.refresh()

    @classmethod
    def get_by_name_and_account(cls, name, account):
        return (
            cls.select_query().where(cls.name == name, cls.account == account).limit(1)
        )

    @classmethod
    def get_all_for_account(cls, account, page=1, page_size=10):
        return (
            cls.select_query()
            .where(cls.account == account)
            .order_by(cls.updated_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )

    @classmethod
    def get_all_for_account_count(cls, account):
        return cls.select_query().where(cls.account == account).count()

    @classmethod
    def get_by_uuid(cls, uuid):
        return cls.select().where(cls.uuid == uuid)

    def get_details(self):
        return {
            "uuid": str(self.uuid),
            "name": self.name,
            "tone": self.tone,
            "style": self.style,
            "instructions": self.instructions,
            "personal_details": self.personal_details,
        }
