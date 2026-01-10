# Webhook Handling System

This document describes the webhook handling system for processing incoming social media comments.

## Architecture

The webhook handling system consists of the following components:

1. **Webhook Controller** (`controller/webhook_controller.py`):
   - Receives incoming webhook requests
   - Validates the request
   - Enqueues the task for asynchronous processing

2. **Webhook Management** (`usecases/webhook_management.py`):
   - Contains the core business logic for processing webhooks
   - Handles comment validation, content checking, and reply generation
   - Manages webhook logging and retries

3. **Broker** (`server/broker.py`):
   - Configures the TaskIQ broker for asynchronous task processing
   - Uses PostgreSQL as the message broker

4. **Webhook Logs** (`data_adapter/webhook_logs.py`):
   - Stores webhook events for auditing and idempotency
   - Tracks processing status and retry attempts

## Setup

1. **Environment Variables**
   Ensure the following environment variables are set in your `.env` file:
   ```
   # Database
   SSQ_DB_USER=your_db_user
   SSQ_DB_PASSWORD=your_db_password
   SSQ_DB_HOST=localhost
   SSQ_DB_PORT=5432
   SSQ_DB_NAME=your_db_name
   
   # TaskIQ
   TASKIQ_WORKERS=4
   ```

2. **Database Tables**
   The following database tables are required:
   - `users`
   - `integrations`
   - `persona_templates`
   - `personas`
   - `posts`
   - `webhook_logs`

## Running Tests

To test the webhook handling flow, run:

```bash
python -m tests.test_webhook_flow
```

## Webhook Payload Format

Example webhook payload for Instagram comments:

```json
{
  "entry": [{
    "changes": [{
      "value": {
        "post_id": "post_123",
        "item": "comment",
        "comment_id": "comment_123",
        "sender_id": "user_123",
        "sender_name": "Test User",
        "message": "This is a test comment",
        "created_time": 1625097600
      }
    }]
  }],
  "object": "instagram",
  "user_id": "user_123",
  "persona_id": "persona_123"
}
```

## Error Handling and Retries

The system implements the following retry strategy:

1. **Exponential Backoff**: Retries with increasing delays between attempts
2. **Max Retries**: Configurable maximum number of retry attempts
3. **Permanent Failures**: Webhooks that repeatedly fail are marked as failed

## Monitoring

Monitor the following for system health:

1. **Logs**: Check application logs for errors and warnings
2. **Webhook Logs**: Monitor the `webhook_logs` table for failed webhooks
3. **Task Queue**: Monitor the task queue for backlogs or failures

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify database credentials
   - Check if the database server is running
   - Ensure the database user has proper permissions

2. **Webhook Processing Failures**
   - Check the `error_message` in the `webhook_logs` table
   - Verify that the webhook payload matches the expected format
   - Check if the associated user, integration, and persona exist

3. **Task Queue Issues**
   - Ensure the TaskIQ worker processes are running
   - Check for deadlocks or long-running tasks
   - Monitor the task queue for backlogs

## Security Considerations

1. **Authentication**: Ensure all webhook endpoints are secured
2. **Input Validation**: Validate all incoming webhook data
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Sensitive Data**: Avoid logging sensitive information
5. **HTTPS**: Always use HTTPS for webhook endpoints
