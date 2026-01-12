from peewee import ForeignKeyField
from playhouse.postgres_ext import CharField, TextField

from data_adapter.db import BaseModel
from data_adapter.user import User


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
    user = ForeignKeyField(User, backref="personas")
    name = CharField()
    tone = CharField()
    style = CharField()
    instructions = TextField()
    personal_details = TextField()

    class Meta:
        db_table = "personas"

    @classmethod
    def create_persona(cls, user: User, name, tone, style, instructions, role, content_categories, personal_details):
        persona = cls.create(
            user=user,
            name=name,
            tone=tone,
            style=style,
            instructions=instructions,
            role=role,
            content_categories=content_categories,
            personal_details=personal_details,
        )
        return persona.refresh()

    @classmethod
    def get_by_name(cls, name):
        return cls.select_query().where(cls.name == name).limit(1)

    @classmethod
    def get_by_name_and_user(cls, name, user):
        """Get persona by name and user. Returns Persona instance or None."""
        try:
            return cls.select_query().where(cls.name == name, cls.user == user).get()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_all(cls, page=1, page_size=10):
        return cls.select_query().order_by(cls.updated_at.desc()).limit(page_size).offset((page - 1) * page_size)

    @classmethod
    def get_all_count(cls):
        return cls.select_query().count()

    @classmethod
    def get_by_uuid(cls, uuid):
        """Get persona by UUID. Returns Persona instance or None."""
        try:
            return cls.select().where(cls.uuid == uuid).get()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_all_for_user(cls, user, page=1, page_size=10):
        """Get paginated personas for a specific user"""
        return cls.select_query().where(cls.user == user).order_by(cls.updated_at.desc()).limit(page_size).offset((page - 1) * page_size)

    @classmethod
    def get_all_for_user_count(cls, user):
        """Get total count of personas for a specific user"""
        return cls.select_query().where(cls.user == user).count()

    @classmethod
    def delete_by_uuid(cls, persona_uuid):
        """Delete persona by UUID (soft delete)"""
        persona = cls.get_by_uuid(persona_uuid)
        if not persona:
            return False
        persona.is_deleted = True
        persona.save()
        return True

    def get_details(self):
        return {
            "uuid": str(self.uuid),
            "name": self.name,
            "tone": self.tone,
            "style": self.style,
            "instructions": self.instructions,
            "personal_details": self.personal_details,
        }
