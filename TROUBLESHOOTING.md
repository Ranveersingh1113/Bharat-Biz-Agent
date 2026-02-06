# WhatsApp Troubleshooting Guide

This guide provides step-by-step troubleshooting for common WhatsApp configuration issues.

## Quick Diagnostic Tool

Run this diagnostic before troubleshooting:

```bash
# Check if server is running
curl http://localhost:8000/api/health

# Expected response:
# {
#   "status": "healthy",
#   "whatsapp": "configured" or "not_configured",
#   ...
# }
```

---

## Problem Tree

### 🔴 Issue 1: Cannot Verify Webhook

**Symptom**: Meta shows "Verification Failed" when configuring webhook

#### Diagnostic Steps:

**Step 1**: Is your server running?
```bash
curl http://localhost:8000/api/health
```
- ✅ **200 OK** → Go to Step 2
- ❌ **Connection refused** → Start your server:
  ```bash
  cd backend
  python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
  ```

**Step 2**: Is your server publicly accessible?
```bash
curl https://your-public-url.com/api/health
```
- ✅ **200 OK** → Go to Step 3
- ❌ **Connection timeout/refused** → Solutions:
  - **Development**: Use ngrok to expose local server
    ```bash
    ngrok http 8000
    # Use the HTTPS URL provided
    ```
  - **Production**: Check firewall, security groups, or load balancer settings

**Step 3**: Test webhook verification manually
```bash
curl "https://your-url.com/api/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=test123"
```
- ✅ **Returns "test123"** → Go to Step 4
- ❌ **403 Forbidden** → Verify token mismatch! Check:
  ```bash
  # In backend/.env
  WHATSAPP_VERIFY_TOKEN=your_token_here
  
  # Must match exactly what you enter in Meta Dashboard
  # Case-sensitive!
  ```

**Step 4**: Check server logs
```bash
# Watch logs while configuring in Meta
tail -f logs.txt  # or check console output
```
- Look for: `"Webhook verification: mode=subscribe, token=..."`
- Should see: `"Webhook verified successfully!"`
- If see: `"Webhook verification failed..."` → Token mismatch

**Solution Checklist**:
- [ ] Server is running
- [ ] Server is publicly accessible via HTTPS
- [ ] Webhook URL is correct: `https://your-url.com/api/webhook`
- [ ] Verify token matches exactly in .env and Meta Dashboard
- [ ] No typos in verify token (case-sensitive)
- [ ] Server responds to manual test
- [ ] No firewall blocking Meta's IP ranges

---

### 🔴 Issue 2: Cannot Send Messages (401 Unauthorized)

**Symptom**: Getting 401 error when trying to send WhatsApp messages

#### Diagnostic Steps:

**Step 1**: Test with the API
```bash
curl -X POST http://localhost:8000/api/test/send-message \
  -H "Content-Type: application/json" \
  -d '{"to_number": "+919876543210", "message": "Test"}'
```

**Step 2**: Check the error response
- **401 Unauthorized** → Access token issue
- **400 Bad Request** → Message format issue (see Issue 4)
- **403 Forbidden** → Phone number or permissions issue

**Step 3**: Verify access token in .env
```bash
cat backend/.env | grep WHATSAPP_ACCESS_TOKEN
```

Common token issues:
- ❌ **Using temporary token** (expires in 24 hours)
  - Solution: Generate permanent token (see WHATSAPP_SETUP.md Section 6)
- ❌ **Token expired**
  - Solution: Generate new permanent token
- ❌ **Wrong token** (copy-paste error)
  - Solution: Re-copy from Meta Business Manager
- ❌ **Token without proper permissions**
  - Solution: Regenerate with `whatsapp_business_messaging` permission

**Step 4**: Test token directly with Meta API
```bash
curl -X POST "https://graph.facebook.com/v18.0/YOUR_PHONE_NUMBER_ID/messages" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "+919876543210",
    "type": "text",
    "text": {"body": "Test"}
  }'
```

**Solution Checklist**:
- [ ] Using permanent access token (not temporary)
- [ ] Token copied correctly (no extra spaces)
- [ ] Token has required permissions
- [ ] Token not expired
- [ ] WHATSAPP_PHONE_NUMBER_ID is correct
- [ ] Server restarted after changing .env

---

### 🔴 Issue 3: Not Receiving Messages

**Symptom**: Can send messages but not receiving incoming WhatsApp messages

#### Diagnostic Steps:

**Step 1**: Is webhook verified?
- Check Meta Dashboard → WhatsApp → Configuration → Webhooks
- Should show ✅ verified

**Step 2**: Are webhook fields subscribed?
- In Webhook configuration, check:
  - [ ] `messages` - Subscribed
  - [ ] `message_status` - Subscribed

**Step 3**: Send test message and check logs
```bash
# In one terminal, watch logs:
tail -f logs.txt  # or console output

# Send WhatsApp message to your business number
# Look for in logs:
"Webhook received: {...}"
"Processing message from +91XXXXXXXXXX: type=text"
```

**Scenario A**: No webhook request in logs
- Webhook not reaching your server
- Solutions:
  1. Verify webhook URL is correct in Meta
  2. Check server is publicly accessible
  3. Verify HTTPS is working
  4. Check firewall isn't blocking Meta's IPs

**Scenario B**: Webhook received but error in processing
- Check error in logs
- Common issues:
  - MongoDB connection error
  - Sarvam API key missing/invalid
  - Python dependencies missing

**Step 4**: Check phone number restrictions
- **If using test number**: Is sender in approved test recipient list?
  - Meta Dashboard → WhatsApp → API Setup → Test Recipients
  - Add recipient numbers before testing
- **If using production number**: Is number opt-in compliant?

**Solution Checklist**:
- [ ] Webhook verified successfully
- [ ] Subscribed to "messages" field
- [ ] Server accessible and running
- [ ] Test phone number in approved list (if using test number)
- [ ] No errors in server logs
- [ ] MongoDB connected
- [ ] All services initialized

---

### 🔴 Issue 4: Getting 400 Bad Request

**Symptom**: Messages failing with 400 error

#### Common Causes:

**Cause 1: Invalid Phone Number Format**
```bash
# ❌ Wrong formats:
9876543210           # Missing country code
919876543210         # Missing +
+91 9876543210       # Has space
+91-9876543210       # Has dash

# ✅ Correct format:
+919876543210        # E.164 format: + country code + number
```

**Cause 2: Message Too Long**
- Text messages: 4096 characters max
- Button titles: 20 characters max
- Interactive messages: Check character limits

**Cause 3: Invalid Message Structure**
Check your JSON payload matches WhatsApp API requirements

**Solution**: Always use E.164 format for phone numbers

---

### 🔴 Issue 5: Server Responds "whatsapp": "not_configured"

**Symptom**: Health check shows WhatsApp not configured

#### Fix:

**Step 1**: Check .env file exists
```bash
ls -la backend/.env
```
- If missing: `cp backend/.env.example backend/.env`

**Step 2**: Verify required variables are set
```bash
cat backend/.env | grep WHATSAPP
```

Must have:
```bash
WHATSAPP_ACCESS_TOKEN=actual_token_not_placeholder
WHATSAPP_PHONE_NUMBER_ID=actual_id_not_placeholder
WHATSAPP_BUSINESS_ACCOUNT_ID=actual_id_not_placeholder
WHATSAPP_VERIFY_TOKEN=your_verify_token
```

**Step 3**: Restart server after changing .env
```bash
# Stop server (Ctrl+C)
# Start again
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

---

### 🔴 Issue 6: Messages Sent But Not Delivered

**Symptom**: Message sent successfully (status 200) but not delivered to WhatsApp

#### Diagnostic Steps:

**Step 1**: Check message status in logs
- Look for status updates in webhook logs
- Possible statuses: `sent`, `delivered`, `read`, `failed`

**Step 2**: Check recipient number
- **For test numbers**: Must be in approved recipient list
- **For production**: Number must be valid and opted-in

**Step 3**: Check message rate limits
- New numbers have limited messaging tier
- Check Meta Dashboard for tier status
- Quality rating affects delivery

**Step 4**: Verify message format
- Some message types require specific formatting
- Interactive messages have strict requirements

---

### 🔴 Issue 7: "Phone Number Already Registered" Error

**Symptom**: Can't add phone number - already registered with WhatsApp

#### Solutions:

**Option A**: Use a different phone number
- The number cannot be on regular WhatsApp
- Get a new number for WhatsApp Business API

**Option B**: Delete WhatsApp account on that number
1. Open WhatsApp on the phone with that number
2. Go to Settings → Account → Delete My Account
3. Wait 24-48 hours
4. Try adding to Business API again

**Option C**: Use Meta's test number (Recommended for dev)
- Meta provides test numbers for development
- No need to use your own number during testing

---

### 🔴 Issue 8: Rate Limit Exceeded

**Symptom**: Error 429 or messages being throttled

#### Understanding Rate Limits:

WhatsApp uses tiered messaging limits:
- **Tier 1**: 1,000 unique customers in 24 hours
- **Tier 2**: 10,000 unique customers in 24 hours
- **Tier 3**: 100,000 unique customers in 24 hours
- **Tier 4**: Unlimited

#### Solutions:

1. **Check current tier**: Meta Dashboard → WhatsApp → Insights
2. **Improve quality rating**: 
   - Respond to messages promptly
   - Don't send spam
   - Provide opt-out options
3. **Tier automatically upgrades** based on:
   - Message volume
   - Quality rating
   - Time
4. **Request tier upgrade** if needed (contact Meta support)

---

### 🔴 Issue 9: Webhook Working But App Not Responding

**Symptom**: Receiving webhooks but no response to user

#### Diagnostic Steps:

**Step 1**: Check agent orchestrator
```bash
# Look in logs for:
"Processing message from..."
"Intent classified as..."
```

**Step 2**: Check MongoDB connection
```bash
# In logs, look for:
"MongoDB connected" or database errors
```

**Step 3**: Check Sarvam AI integration
```bash
# Verify API key is set:
cat backend/.env | grep SARVAM_API_KEY

# Check logs for Sarvam API errors
```

**Step 4**: Test individual components
```bash
# Test intent classification
curl -X POST http://localhost:8000/api/test/classify-intent \
  -H "Content-Type: application/json" \
  -d '{"text": "stock check karo"}'
```

---

## Environment Variables Checklist

Verify all required variables are set:

```bash
# Required for WhatsApp
✅ WHATSAPP_ACCESS_TOKEN (permanent, not temporary)
✅ WHATSAPP_PHONE_NUMBER_ID
✅ WHATSAPP_BUSINESS_ACCOUNT_ID
✅ WHATSAPP_VERIFY_TOKEN
✅ WHATSAPP_API_VERSION (default: v18.0)

# Required for Database
✅ MONGO_URL
✅ DB_NAME

# Required for AI
✅ SARVAM_API_KEY

# Required for Business
✅ BUSINESS_NAME
✅ BUSINESS_PHONE
```

---

## Debug Mode

Enable detailed logging for troubleshooting:

**Step 1**: Set log level to DEBUG
```python
# In server.py, change:
logging.basicConfig(level=logging.DEBUG)
```

**Step 2**: Restart server and monitor logs
```bash
python -m uvicorn server:app --reload --log-level debug
```

**Step 3**: Look for detailed request/response logs

---

## Getting Help

If you're still stuck:

1. **Check Documentation**:
   - [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) - Complete setup guide
   - [WEBHOOK_QUICK_REF.md](WEBHOOK_QUICK_REF.md) - Webhook reference
   - [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) - Step-by-step checklist

2. **Review Logs**:
   - Server console output
   - Meta Developers Console (App Dashboard → Webhooks)
   - Browser network tab (for frontend issues)

3. **Test Individual Components**:
   - WhatsApp API directly with curl
   - Database connection separately
   - AI services separately

4. **Meta Resources**:
   - [Meta Developer Community](https://developers.facebook.com/community/)
   - [WhatsApp Business API Docs](https://developers.facebook.com/docs/whatsapp/)
   - Meta Business Support

5. **Common Issue Patterns**:
   - Most issues are credentials (token, IDs)
   - Second most: network/accessibility
   - Third most: configuration mismatches

---

## Prevention Checklist

Avoid common issues:

- [ ] Use permanent access tokens (not temporary)
- [ ] Keep tokens secure (never commit .env)
- [ ] Use HTTPS for webhooks (required by Meta)
- [ ] Test in development before production
- [ ] Monitor quality rating regularly
- [ ] Keep API version updated
- [ ] Document your configuration
- [ ] Backup your .env template
- [ ] Test after any changes
- [ ] Monitor logs regularly

---

## Quick Command Reference

```bash
# Check if server is accessible
curl http://localhost:8000/api/health

# Test webhook verification
curl "http://localhost:8000/api/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=test"

# Send test message
curl -X POST http://localhost:8000/api/test/send-message \
  -H "Content-Type: application/json" \
  -d '{"to_number": "+91XXXXXXXXXX", "message": "Test"}'

# Check environment variables
cat backend/.env | grep WHATSAPP

# Restart server
# Ctrl+C then:
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

---

**Remember**: Most WhatsApp configuration issues are due to:
1. ❌ Using temporary tokens (24h expiry)
2. ❌ Token/verify token mismatches
3. ❌ Server not publicly accessible via HTTPS
4. ❌ Webhook not subscribed to correct fields
5. ❌ Phone numbers not in E.164 format

Double-check these first! 🔍
