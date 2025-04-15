import datetime

from peewee import Model, AutoField, UUIDField, DateTimeField, BooleanField
from playhouse.pool import PooledPostgresqlExtDatabase

from config.env import (
    SSQ_DB_HOST,
    SSQ_DB_NAME,
    SSQ_DB_PASSWORD,
    SSQ_DB_PORT,
    SSQ_DB_USER,
    DEBUG,
    APP_ENVIRONMENT,
    TESTING,
)
from logger.logging import LoggerUtil

# Connect to ssq database
ssq_db = PooledPostgresqlExtDatabase(
    SSQ_DB_NAME,
    user=SSQ_DB_USER,
    password=SSQ_DB_PASSWORD,
    host=SSQ_DB_HOST,
    port=SSQ_DB_PORT,
    autorollback=True,
    max_connections=50,
    # Number of seconds to wait for a connection(DB query) when pool is full
    timeout=5,
    stale_timeout=300,  # Number of seconds to allow connections to be used
    thread_safe=not TESTING,
)

if DEBUG:
    # Print all queries in debug mode.
    import logging

    peewee_logger = logging.getLogger("peewee")
    peewee_logger.addHandler(logging.StreamHandler())
    peewee_logger.setLevel(logging.DEBUG)


class BaseModel(Model):
    id = AutoField()
    uuid = UUIDField()
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField()
    is_deleted = BooleanField(default=False)

    class Meta:
        database = ssq_db

    @classmethod
    def get_by_pk(cls, pk):
        return cls.select_query().where(cls.id == pk).limit(1)

    @classmethod
    def get_by_uuid(cls, uuid):
        return cls.select_query().where(cls.uuid == uuid).limit(1)

    def save(self, *args, **kwargs):
        if not kwargs.pop("skip_updated_at", False):
            self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)

    def refresh(self):
        # Always use as a return value
        # instance = instance.refresh()
        return type(self).get(self._pk_expr())

    @classmethod
    def select_query(cls, columns=None):
        if columns is None:
            columns = []
        return cls.select(*columns).where(cls.is_deleted == False)  # noqa

    @classmethod
    def update_query(cls, update_dict, skip_updated_at=False):
        if not skip_updated_at:
            update_dict[cls.updated_at] = datetime.datetime.now()
        return cls.update(update_dict)

    @classmethod
    def soft_delete(cls):
        return cls.update(
            {cls.is_deleted: True, cls.updated_at: datetime.datetime.now()}
        )


def get_db_status():
    LoggerUtil.create_info_log(
        "GET_DB_STATUS:: host: {}, user: {}, port: {}, db: {}, app_env: {}".format(
            SSQ_DB_HOST,
            SSQ_DB_USER,
            SSQ_DB_PORT,
            SSQ_DB_NAME,
            APP_ENVIRONMENT,
        ),
    )
    error = False
    try:
        cursor = ssq_db.execute_sql("select 'ok'")
        res = cursor.fetchone()[0]
        LoggerUtil.create_info_log("DB:: Successfully connected")
    except Exception as e:
        LoggerUtil.create_error_log("DB:: Not able to connect with e: {}".format(e))
        res = str(e)
        error = True
    return res, error
