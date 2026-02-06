# Visual Guide: Configuring Webhook in Meta Dashboard

This guide shows you EXACTLY where to enter your webhook URL in Meta's interface.

## Step-by-Step Visual Instructions

### Step 1: Navigate to Webhook Configuration

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click on **"My Apps"**
3. Select your app
4. In the left sidebar, find **"WhatsApp"** 
5. Click **"Configuration"** under WhatsApp

You should now see the WhatsApp Configuration page.

### Step 2: Locate the Webhook Section

On the Configuration page, scroll down to find the **"Webhook"** section.

It will look like this:

```
┌─────────────────────────────────────────────────────────────┐
│ Webhook                                                      │
│                                                              │
│ ○ Not configured       OR      ✓ Configured                │
│                                                              │
│ [Edit] button                                                │
└─────────────────────────────────────────────────────────────┘
```

Click the **[Edit]** button (or **[Configure Webhooks]** if not configured yet).

### Step 3: The Webhook Configuration Form

A modal/popup will appear with these fields:

```
┌──────────────────────────────────────────────────────────────┐
│  Edit Callback URL                                     [×]   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Callback URL *                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ https://                                                 ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  Verify token *                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                                                          ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│                    [Cancel]  [Verify and Save]               │
└──────────────────────────────────────────────────────────────┘
```

### Step 4: Fill in the Form EXACTLY

#### Callback URL Field:
Enter your complete webhook URL **EXACTLY** as shown:

✅ **Correct format:**
```
https://your-domain.com/api/webhook
```

**Examples:**
- With ngrok: `https://abc123xyz.ngrok.io/api/webhook`
- With Heroku: `https://myapp.herokuapp.com/api/webhook`
- Custom domain: `https://api.mycompany.com/api/webhook`

❌ **Common mistakes:**
- `http://localhost:8000/api/webhook` ← Not public!
- `https://myapp.com/webhook` ← Missing /api/ prefix
- `https://myapp.com/api/webhook/` ← Has trailing slash
- `myapp.com/api/webhook` ← Missing https://

#### Verify Token Field:
Enter the **exact** verify token from your `.env` file:

```bash
# Check your .env file first:
cat backend/.env | grep WHATSAPP_VERIFY_TOKEN

# Copy the value after the = sign
# Example: bharat_biz_verify_2026_secure
```

**Important:**
- ⚠️ Case-sensitive! `ABC` ≠ `abc`
- ⚠️ No spaces before or after
- ⚠️ Must match `.env` EXACTLY

### Step 5: Click "Verify and Save"

When you click **[Verify and Save]**, Meta will:

1. Send a GET request to your URL:
   ```
   GET https://your-url.com/api/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=RANDOM_STRING
   ```

2. Your server should respond with the `hub.challenge` value

3. If successful, you'll see: ✅ **"Webhook configured successfully"**

4. If failed, you'll see: ❌ **"URL couldn't be validated"**

### Step 6: Subscribe to Webhook Fields

After successful verification, you'll see a list of webhook fields:

```
┌──────────────────────────────────────────────────────────────┐
│ Webhook fields                                                │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ ☐ messages              Subscribe to receive incoming        │
│                        messages                               │
│                                          [Subscribe]          │
│                                                               │
│ ☐ messaging_postbacks   Subscribe to receive postbacks       │
│                                          [Subscribe]          │
│                                                               │
│ ☐ message_status        Subscribe to receive message         │
│                        status updates                         │
│                                          [Subscribe]          │
└──────────────────────────────────────────────────────────────┘
```

**REQUIRED: Subscribe to these fields:**

1. **messages** ✅ 
   - Click **[Subscribe]** next to "messages"
   - This allows you to receive incoming WhatsApp messages

2. **message_status** ✅
   - Click **[Subscribe]** next to "message_status"  
   - This allows you to track message delivery (sent/delivered/read)

### Step 7: Verify Configuration

After subscribing, the Webhook section should show:

```
┌─────────────────────────────────────────────────────────────┐
│ Webhook                                                      │
│                                                              │
│ ✓ Configured                                                │
│                                                              │
│ Callback URL: https://your-url.com/api/webhook             │
│                                                              │
│ Subscribed fields:                                           │
│ • messages                                                   │
│ • message_status                                            │
│                                                              │
│ [Edit]                                                       │
└─────────────────────────────────────────────────────────────┘
```

✅ Configuration complete!

## What to Do If Verification Fails

### Error: "The URL couldn't be validated"

**Before trying again:**

1. **Test your webhook first:**
   ```bash
   cd backend
   python test_webhook.py https://your-url.com/api/webhook your_token
   ```

2. **Check server logs:**
   ```bash
   # You should see:
   INFO: Webhook verification: mode=subscribe, token=...
   ```

3. **Common fixes:**
   - Make sure server is running
   - Use ngrok if testing locally
   - Check verify token matches .env
   - Ensure URL has no trailing slash
   - Restart server after .env changes

**Then try again in Meta.**

### Error: "Please enter a valid URL"

**This means the URL format is wrong.**

Check:
- ✅ Starts with `https://`
- ✅ Has valid domain (not localhost)
- ✅ Ends with `/api/webhook`
- ✅ No spaces or typos

## Real Example Walkthrough

Let's say you're using ngrok for testing:

**1. Start your server:**
```bash
cd backend
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

**2. Start ngrok:**
```bash
ngrok http 8000
# Output: Forwarding https://abc123.ngrok.io -> http://localhost:8000
```

**3. Your webhook URL is:**
```
https://abc123.ngrok.io/api/webhook
```

**4. Test it:**
```bash
python test_webhook.py https://abc123.ngrok.io/api/webhook bharat_biz_verify_2026_secure
```

If tests pass ✅, proceed to Meta.

**5. In Meta Dashboard:**
- Callback URL: `https://abc123.ngrok.io/api/webhook`
- Verify Token: `bharat_biz_verify_2026_secure`
- Click: Verify and Save

**6. Watch your server logs:**
```
INFO: GET /api/webhook?hub.mode=subscribe&...
INFO: Webhook verification: mode=subscribe
INFO: Webhook verified successfully!
```

**7. In Meta, subscribe to:**
- messages ✅
- message_status ✅

**Done!** 🎉

## Troubleshooting Checklist

Before entering URL in Meta:

- [ ] Server is running
- [ ] Using public URL (ngrok or deployed)
- [ ] URL tested with `test_webhook.py` ✅
- [ ] Verify token copied from `.env`
- [ ] URL has no trailing slash
- [ ] URL includes `/api/webhook` at the end
- [ ] Server logs show webhook endpoint is ready

## Need More Help?

- **URL being rejected?** → See [WEBHOOK_URL_FIX.md](WEBHOOK_URL_FIX.md)
- **General issues?** → See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Complete setup?** → See [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md)

---

**Remember:** The diagnostic tool is your friend!

```bash
python backend/test_webhook.py <url> <token>
```

If it passes all tests, Meta will accept your URL! ✅
