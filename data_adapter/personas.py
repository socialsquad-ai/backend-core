from data_adapter.db import BaseModel
from playhouse.postgres_ext import CharField, TextField


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

    class Meta:
        db_table = "personas"

    @classmethod
    def create_persona(cls, name, tone, style, instructions, personal_details):
        persona = cls.create(
            name=name,
            tone=tone,
            style=style,
            instructions=instructions,
            personal_details=personal_details,
        )
        return persona.refresh()

    @classmethod
    def get_by_name(cls, name):
        return cls.select_query().where(cls.name == name).limit(1)

    @classmethod
    def get_all(cls, page=1, page_size=10):
        return (
            cls.select_query()
            .order_by(cls.updated_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )

    @classmethod
    def get_all_count(cls):
        return cls.select_query().count()

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
