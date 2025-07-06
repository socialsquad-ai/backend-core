from data_adapter.db import BaseModel
from playhouse.postgres_ext import CharField, BooleanField, DateTimeField
from peewee import ForeignKeyField
from data_adapter.account import Account


class User(BaseModel):
    auth0_user_id = CharField(unique=True)  # Auth0 user ID
    name = CharField(null=True)
    email = CharField()
    signup_method = CharField(
        default="email-password"
    )  # email-password, google, facebook, etc.
    email_verified = BooleanField(default=False)
    auth0_created_at = DateTimeField(null=True)  # When user was created in Auth0
    account = ForeignKeyField(Account, backref="users")

    class Meta:
        db_table = "users"

    @classmethod
    def get_by_email(cls, email):
        return cls.select_query().where(cls.email == email).limit(1)

    @classmethod
    def get_by_auth0_user_id(cls, auth0_user_id):
        return cls.select_query().where(cls.auth0_user_id == auth0_user_id).limit(1)

    @classmethod
    def get_or_create_user_from_auth0(
        cls,
        auth0_user_id,
        name,
        email,
        signup_method,
        email_verified,
        auth0_created_at,
        account,
    ):
        """
        Create or update user from Auth0 user data
        user_data should contain: auth0_user_id, name, email, signup_method, email_verified, created_at
        """
        try:
            user = User.create(
                auth0_user_id=auth0_user_id,
                name=name,
                email=email,
                signup_method=signup_method,
                email_verified=email_verified,
                auth0_created_at=auth0_created_at,
                account=account,
            )
        except Exception as e:
            raise e
        return user

    @classmethod
    def get_all_users(cls):
        return cls.select_query().limit(100)

    def get_details(self):
        return {
            "name": self.name,
            "email": self.email,
            "signup_method": self.signup_method,
            "email_verified": self.email_verified,
            "created_at": (
                self.auth0_created_at.isoformat()
                if self.auth0_created_at
                else self.created_at.isoformat()
            ),
            "uuid": str(self.uuid),
        }
