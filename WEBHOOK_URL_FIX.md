# Fixing "URL Not Valid" Error in Meta Webhook Configuration

## The Problem

When trying to enter your webhook URL in Meta's WhatsApp Configuration, you see:
- ❌ "URL not valid"
- ❌ "The URL couldn't be validated"
- ❌ "Invalid callback URL"

## Why This Happens

Meta validates webhook URLs by sending a test request. The URL can fail validation for several reasons:

### Common Causes

1. ❌ **Using localhost or local IP addresses**
   - `http://localhost:8000/api/webhook` - Won't work!
   - `http://127.0.0.1:8000/api/webhook` - Won't work!
   - `http://192.168.1.100:8000/api/webhook` - Won't work!

2. ❌ **Not using HTTPS (for production)**
   - `http://myapp.com/api/webhook` - Won't work in production!
   - Meta requires HTTPS for security

3. ❌ **Server not running or not accessible**
   - Server is down
   - Firewall blocking Meta's verification request
   - URL is wrong

4. ❌ **Wrong endpoint path**
   - Missing `/api/webhook`
   - Extra trailing slash
   - Typo in the path

5. ❌ **Verify token mismatch**
   - Token in Meta doesn't match token in `.env`
   - Case sensitivity issue

## Step-by-Step Solution

### Step 1: Make Your Server Publicly Accessible

**Problem**: Meta cannot reach `localhost`

**Solution A: Use ngrok (for testing/development)**

```bash
# 1. Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# 2. Start your backend server
cd backend
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000

# 3. In a new terminal, start ngrok
ngrok http 8000

# You'll see output like:
# Forwarding  https://abc123xyz.ngrok.io -> http://localhost:8000
```

**Solution B: Deploy to cloud (for production)**

Deploy your app to:
- Heroku
- AWS (EC2, Elastic Beanstalk, ECS)
- Google Cloud Platform
- Azure
- DigitalOcean
- Railway
- Render

Make sure you have HTTPS enabled (most platforms provide this automatically).

### Step 2: Get Your Exact Webhook URL

Your webhook URL format should be:

```
https://your-domain.com/api/webhook
```

**Examples:**

✅ **Correct URLs:**
```
https://abc123.ngrok.io/api/webhook
https://myapp.herokuapp.com/api/webhook
https://api.mycompany.com/api/webhook
https://bharat-biz.example.com/api/webhook
```

❌ **Incorrect URLs:**
```
http://localhost:8000/api/webhook              # localhost not accessible
https://myapp.com/webhook                      # missing /api/ prefix
https://myapp.com/api/webhook/                 # trailing slash
https://myapp.com/                             # missing /api/webhook
http://myapp.com/api/webhook                   # using http not https
```

### Step 3: Test Your Webhook URL BEFORE Entering in Meta

We've created a diagnostic tool to test your webhook before Meta validation:

```bash
cd backend

# Test your webhook
python test_webhook.py <your-url> <your-verify-token>

# Example with ngrok:
python test_webhook.py https://abc123.ngrok.io/api/webhook bharat_biz_verify_2026_secure

# Example with deployed app:
python test_webhook.py https://myapp.com/api/webhook bharat_biz_verify_2026_secure
```

**The tool will test:**
1. ✅ URL format is correct
2. ✅ URL is accessible
3. ✅ Webhook responds to verification requests
4. ✅ Verify token works correctly

**If all tests pass**, your webhook is ready for Meta!

### Step 4: Verify Your Environment Variables

Make sure your `.env` file has the correct verify token:

```bash
# Check your .env file
cat backend/.env | grep WHATSAPP_VERIFY_TOKEN

# It should output something like:
# WHATSAPP_VERIFY_TOKEN=bharat_biz_verify_2026_secure
```

**Important**: 
- The verify token must match exactly (case-sensitive)
- No spaces before or after the `=`
- No quotes around the value

### Step 5: Restart Your Server

After any changes to `.env`:

```bash
# Stop the server (Ctrl+C)
# Then start it again:
cd backend
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Enter URL in Meta Dashboard

Now go to Meta Dashboard:

1. Navigate to: **Your App → WhatsApp → Configuration**
2. Find the **Webhook** section
3. Click **"Edit"** or **"Configure Webhooks"**

**Enter exactly:**

| Field | Value |
|-------|-------|
| **Callback URL** | `https://your-domain.com/api/webhook` |
| **Verify Token** | Same as `WHATSAPP_VERIFY_TOKEN` in your `.env` |

**Critical Points:**
- ✅ Include `https://` at the start
- ✅ Include `/api/webhook` at the end
- ✅ NO trailing slash
- ✅ Verify token must match EXACTLY (case-sensitive)
- ✅ Copy-paste to avoid typos

4. Click **"Verify and Save"**

### Step 7: Check Server Logs

Watch your server logs while Meta verifies:

```bash
# You should see:
INFO:     GET /api/webhook?hub.mode=subscribe&...
INFO:     Webhook verification: mode=subscribe, token=...
INFO:     Webhook verified successfully!
```

If you see `Webhook verification failed`, check:
- The verify token in Meta matches `.env`
- Server is running
- No typos in the URL

## Common Errors and Solutions

### Error: "The URL couldn't be validated. Please verify the URL."

**Cause**: Meta cannot reach your server

**Solutions**:
1. **Check if server is running**: 
   ```bash
   curl http://localhost:8000/api/health
   ```
   Should return a response. If not, start your server.

2. **Use ngrok if testing locally**:
   ```bash
   ngrok http 8000
   # Use the https URL it provides
   ```

3. **Check firewall settings**: Make sure port 8000 (or your port) is open

4. **Test the URL yourself**:
   ```bash
   curl "https://your-url.com/api/webhook?hub.mode=subscribe&hub.verify_token=your_token&hub.challenge=test"
   # Should return: test
   ```

### Error: "Please enter a valid URL"

**Cause**: URL format is wrong

**Check**:
- ✅ Starts with `https://` (not `http://`)
- ✅ Has a valid domain (not localhost)
- ✅ Includes `/api/webhook`
- ✅ No spaces
- ✅ No typos

### Error: Verification keeps failing

**Cause**: Verify token mismatch

**Solution**:
1. Check your `.env` file:
   ```bash
   cat backend/.env | grep WHATSAPP_VERIFY_TOKEN
   ```

2. Copy the exact value (without `WHATSAPP_VERIFY_TOKEN=`)

3. Paste it in Meta Dashboard (verify token field)

4. Make sure there are no extra spaces or quotes

5. **Restart your server** after any `.env` changes

### Error: "Connection timeout"

**Cause**: Server is too slow to respond

**Solutions**:
1. Check server performance
2. Check if server is under heavy load
3. Optimize your webhook endpoint
4. Use faster hosting if deployed

## Quick Diagnostic Checklist

Before entering URL in Meta, verify:

- [ ] Server is running (`curl http://localhost:8000/api/health`)
- [ ] Using public URL (not localhost)
- [ ] Using HTTPS (for production, or ngrok for testing)
- [ ] URL ends with `/api/webhook`
- [ ] No trailing slash
- [ ] Verify token in `.env` is set
- [ ] Server restarted after `.env` changes
- [ ] Ran `python test_webhook.py <url> <token>` successfully

## Real-World Example

Let's walk through a complete example:

**Your Setup:**
- Backend running locally on port 8000
- Want to test WhatsApp integration

**Step 1: Start your server**
```bash
cd /home/runner/work/Bharat-Biz-Agent/Bharat-Biz-Agent/backend
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

**Step 2: Start ngrok**
```bash
ngrok http 8000
```

Output:
```
Forwarding  https://a1b2c3d4.ngrok.io -> http://localhost:8000
```

**Step 3: Your webhook URL is:**
```
https://a1b2c3d4.ngrok.io/api/webhook
```

**Step 4: Test it**
```bash
cd backend
python test_webhook.py https://a1b2c3d4.ngrok.io/api/webhook bharat_biz_verify_2026_secure
```

If all tests pass ✅, proceed to Meta.

**Step 5: Enter in Meta Dashboard**
- Callback URL: `https://a1b2c3d4.ngrok.io/api/webhook`
- Verify Token: `bharat_biz_verify_2026_secure`

**Step 6: Click "Verify and Save"**

✅ Should work!

## Still Not Working?

### Enable Debug Logging

Edit `backend/server.py` temporarily:

```python
# Add at line 69 (in verify_webhook function):
logger.info(f"Received verification - mode={mode}, token={token}, challenge={challenge}")
logger.info(f"Expected token: {settings.whatsapp_verify_token}")
logger.info(f"Token match: {token == settings.whatsapp_verify_token}")
```

Restart server and try again. Check logs for detailed info.

### Test Manually

```bash
# Replace with your actual URL and token
curl "https://your-url.com/api/webhook?hub.mode=subscribe&hub.verify_token=your_token&hub.challenge=test123"

# Should return exactly: test123
```

### Check HTTPS Certificate

If using your own domain:

```bash
curl -v https://your-url.com/api/webhook
```

Look for SSL certificate errors. Meta requires valid SSL certificates.

## Summary

The "URL not valid" error typically means:
1. 🚫 Using localhost (use ngrok or deploy to cloud)
2. 🚫 Not using HTTPS (use ngrok for dev, proper SSL for production)
3. 🚫 Server not accessible (check firewall, ensure server is running)
4. 🚫 Wrong URL format (must be `https://domain.com/api/webhook`)
5. 🚫 Verify token mismatch (must match `.env` exactly)

**Solution**: Use the diagnostic tool first!
```bash
python backend/test_webhook.py <your-url> <your-token>
```

If the tool says "All tests passed ✅", then Meta should accept your URL!

## Need More Help?

See also:
- [WEBHOOK_QUICK_REF.md](WEBHOOK_QUICK_REF.md) - Quick webhook reference
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - General troubleshooting
- [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) - Complete setup guide
