from datetime import datetime
from data_adapter.db import BaseModel
from playhouse.postgres_ext import (
    TextField,
    JSONField,
    DateTimeField,
    CharField,
    IntegerField,
)
from peewee import ForeignKeyField
from data_adapter.integration import Integration
from data_adapter.posts import Post


class WebhookLog(BaseModel):
    """
    Model to store incoming webhook data for auditing and retry purposes
    """

    webhook_id = CharField(max_length=255, unique=True, index=True)
    integration = ForeignKeyField(Integration, backref="webhook_logs")
    post = ForeignKeyField(Post, backref="webhook_logs", null=True)
    event_type = CharField(max_length=100)  # e.g., 'comment_created', 'comment_updated'
    payload = JSONField()
    status = CharField(
        max_length=50, default="pending"
    )  # pending, processing, completed, failed
    retry_count = IntegerField(default=0)
    last_attempt_at = DateTimeField(null=True)
    error_message = TextField(null=True)
    processed_at = DateTimeField(null=True)

    class Meta:
        db_table = "webhook_logs"
        indexes = (
            (("webhook_id", "event_type"), True),  # Composite unique index
        )

    @classmethod
    def create_webhook_log(
        cls, webhook_id, integration_id, event_type, payload, post_id=None
    ):
        """Create a new webhook log entry"""
        return cls.create(
            webhook_id=webhook_id,
            integration=integration_id,
            post=post_id,
            event_type=event_type,
            payload=payload,
            status="pending",
            retry_count=0,
        )

    def mark_processing(self):
        """Mark the webhook as being processed"""
        self.status = "processing"
        self.retry_count += 1
        self.last_attempt_at = datetime.utcnow()
        self.save()

    def mark_completed(self, result=None):
        """Mark the webhook as successfully processed"""
        self.status = "completed"
        self.processed_at = datetime.utcnow()
        if result:
            self.result = result
        self.save()

    def mark_failed(self, error_message):
        """Mark the webhook as failed with error message"""
        self.status = "failed"
        self.error_message = str(error_message)[:1000]  # Limit error message length
        self.save()

    def can_retry(self, max_retries=3):
        """Check if this webhook can be retried"""
        return self.retry_count < max_retries and self.status != "completed"

    @classmethod
    def get_pending_webhooks(cls, batch_size=10):
        """Get a batch of pending webhooks for processing"""
        return (
            cls.select()
            .where(
                (cls.status == "pending")
                | ((cls.status == "failed") & (cls.retry_count < 3))
            )
            .order_by(cls.created_at)
            .limit(batch_size)
        )
