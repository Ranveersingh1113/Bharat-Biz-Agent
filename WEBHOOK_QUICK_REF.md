# Quick Reference: WhatsApp Webhook Configuration

This is a condensed reference for quickly configuring your WhatsApp webhook. For the complete setup guide, see [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md).

## Webhook Endpoint

Your server must expose this endpoint:

```
GET  /api/webhook  - For webhook verification
POST /api/webhook  - For receiving messages
```

## Webhook Configuration in Meta Dashboard

1. Go to your Meta App Dashboard
2. Navigate to **WhatsApp > Configuration**
3. Click **"Configure Webhooks"** or **"Edit"**

### Required Settings:

| Field | Value | Example |
|-------|-------|---------|
| **Callback URL** | Your public HTTPS URL + `/api/webhook` | `https://your-domain.com/api/webhook` |
| **Verify Token** | Same as `WHATSAPP_VERIFY_TOKEN` in .env | `bharat_biz_verify_2026_secure` |

### Required Subscriptions:

Subscribe to these webhook fields:
- ✅ **messages** - To receive incoming messages
- ✅ **message_status** - To track message delivery status

## Environment Variable

Make sure this is set in your `backend/.env`:

```bash
WHATSAPP_VERIFY_TOKEN=bharat_biz_verify_2026_secure
```

**Important:** The verify token must match exactly (case-sensitive) between:
- Your `.env` file
- Meta webhook configuration

## Verification Process

When you click "Verify and Save" in Meta Dashboard:

1. Meta sends a GET request to your webhook URL:
   ```
   GET https://your-domain.com/api/webhook?
       hub.mode=subscribe&
       hub.verify_token=YOUR_TOKEN&
       hub.challenge=CHALLENGE_STRING
   ```

2. Your server (server.py line 59-78) validates:
   - `hub.mode` == "subscribe"
   - `hub.verify_token` == `settings.whatsapp_verify_token`

3. If valid, server returns the `hub.challenge` as plain text

4. Meta confirms verification ✅

## Testing Webhook Verification

### Step 1: Start Your Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Make Server Publicly Accessible

Your server must be accessible via HTTPS. Options:

**Option A: Production Deployment**
- Deploy to a cloud platform (AWS, GCP, Azure, Heroku, etc.)
- Ensure HTTPS is enabled

**Option B: Development with Tunneling (ngrok)**
```bash
# Install ngrok
brew install ngrok  # macOS
# Or download from https://ngrok.com/

# Create a tunnel to your local server
ngrok http 8000

# Use the HTTPS URL provided (e.g., https://abc123.ngrok.io)
# Your webhook URL becomes: https://abc123.ngrok.io/api/webhook
```

### Step 3: Manual Verification Test

Test the verification endpoint manually:

```bash
curl "http://localhost:8000/api/webhook?hub.mode=subscribe&hub.verify_token=bharat_biz_verify_2026_secure&hub.challenge=test123"
```

Expected response:
```
test123
```

### Step 4: Configure in Meta

1. Enter your webhook URL in Meta Dashboard
2. Enter the verify token
3. Click "Verify and Save"
4. Check your server logs - should see: `Webhook verified successfully!`

## Message Receiving Test

After webhook verification:

1. Send a WhatsApp message to your business number
2. Check server logs - you should see:
   ```
   Webhook received: {...}
   Processing message from +919876543210: type=text
   ```
3. The system should auto-respond

## Troubleshooting Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| "Verification Failed" | - Check server is running<br>- Verify URL is HTTPS<br>- Check verify token matches exactly |
| Not receiving messages | - Verify webhook subscribed to "messages"<br>- Check phone in test recipient list<br>- Review server logs |
| 403 Forbidden | - Verify token mismatch - check .env file |
| Connection timeout | - Server not publicly accessible<br>- Check firewall/security groups |

## Server Logs to Watch

Key log messages:
```python
# Verification
"Webhook verification: mode=subscribe, token=..."
"Webhook verified successfully!"

# Receiving messages  
"Webhook received: {...}"
"Processing message from +919876543210: type=text"

# Errors
"Webhook verification failed..."
"Webhook error: ..."
```

## Next Steps

After successful webhook configuration:

1. ✅ Webhook verified
2. Test sending messages → **Use `/api/test/send-message` endpoint**
3. Test receiving messages → **Send WhatsApp to your number**
4. Configure other settings → **See WHATSAPP_SETUP.md**

## Webhook Request Format

For reference, incoming webhook POST body structure:

```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "id": "message_id",
          "from": "918765432109",
          "timestamp": "1612345678",
          "type": "text",
          "text": { "body": "Hello" }
        }]
      }
    }]
  }]
}
```

Your server automatically processes this in `server.py` lines 81-112.

## Security Notes

- ✅ Always use HTTPS for webhooks (Meta requirement)
- ✅ Keep verify token secret (minimum 20 characters recommended)
- ✅ Validate webhook signatures in production (optional but recommended)
- ✅ Never log sensitive customer data

---

For complete setup instructions, troubleshooting, and advanced configuration, see [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md).
