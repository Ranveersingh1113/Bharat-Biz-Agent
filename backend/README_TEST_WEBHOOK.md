# Webhook Diagnostic Tool

## Quick Usage

Test your webhook URL before configuring it in Meta Dashboard:

```bash
python test_webhook.py <webhook-url> <verify-token>
```

## Examples

### With ngrok:
```bash
python test_webhook.py https://abc123.ngrok.io/api/webhook bharat_biz_verify_2026_secure
```

### With deployed app:
```bash
python test_webhook.py https://myapp.com/api/webhook bharat_biz_verify_2026_secure
```

## What It Tests

1. ✅ **URL Format** - Checks HTTPS, hostname, path format
2. ✅ **URL Accessibility** - Tests if URL is reachable
3. ✅ **Webhook Verification** - Simulates Meta's verification request
4. ✅ **Security** - Tests incorrect token rejection

## Common Issues Detected

- ❌ Using localhost (Meta can't reach it)
- ❌ Using HTTP instead of HTTPS
- ❌ Private IP addresses
- ❌ Server not running
- ❌ Wrong verify token
- ❌ Missing /api/webhook path

## If All Tests Pass

You'll get exact instructions for entering the URL in Meta Dashboard:

```
📋 Copy these exact values into Meta Dashboard:

Callback URL:  https://your-url.com/api/webhook
Verify Token:  your_verify_token

⚠️  IMPORTANT:
1. The Callback URL must be EXACTLY as shown above
2. Include https:// at the beginning
3. Include /api/webhook at the end
4. No trailing slash
5. Verify Token is case-sensitive - copy exactly
```

## Troubleshooting

If tests fail, the tool will tell you exactly what's wrong and how to fix it.

See also: [WEBHOOK_URL_FIX.md](../WEBHOOK_URL_FIX.md) for detailed troubleshooting.
