# Quick Start Guide - Bharat Biz-Agent

Get your Bharat Biz-Agent up and running in under 30 minutes!

## What You'll Need

- [ ] Meta/Facebook Business Account
- [ ] Phone number (not on regular WhatsApp)
- [ ] MongoDB (local or Atlas)
- [ ] Sarvam AI API key ([Get one here](https://www.sarvam.ai/))
- [ ] Server with HTTPS (or ngrok for testing)

## 5-Step Quick Start

### Step 1: Get WhatsApp Credentials (15 minutes)

1. **Create Meta App**:
   - Go to [Meta for Developers](https://developers.facebook.com/)
   - Create Business App
   - Add WhatsApp product

2. **Collect These Values** (write them down):
   ```
   Phone Number ID:          __________________
   Business Account ID:      __________________
   Temporary Access Token:   __________________ (expires in 24h)
   ```

3. **Generate Permanent Token**:
   - Meta Business Manager → System Users
   - Create system user → Generate token
   - Permissions: `whatsapp_business_messaging`, `whatsapp_business_management`
   - **Save this token securely!**

📖 **Detailed instructions**: [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md)

### Step 2: Configure Environment (3 minutes)

```bash
# 1. Clone/navigate to repository
cd Bharat-Biz-Agent/backend

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Fill in these critical values**:
```bash
WHATSAPP_ACCESS_TOKEN=your_permanent_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id_here
WHATSAPP_VERIFY_TOKEN=create_a_random_string_20_chars

MONGO_URL=mongodb://localhost:27017
SARVAM_API_KEY=your_sarvam_key_here

BUSINESS_NAME=Your Business Name
BUSINESS_PHONE=+919876543210
```

### Step 3: Start Backend (5 minutes)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000

# ✅ You should see:
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify**: Open http://localhost:8000/api/health
```json
{
  "status": "healthy",
  "whatsapp": "configured",  // ← Should say "configured"
  "sarvam": "configured"
}
```

### Step 4: Configure Webhook (5 minutes)

**Option A: Development (ngrok)**
```bash
# In a new terminal:
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Your webhook URL is: https://abc123.ngrok.io/api/webhook
```

**Option B: Production**
```bash
# Deploy to your server
# Your webhook URL is: https://yourdomain.com/api/webhook
```

**⚡ IMPORTANT: Test Your Webhook First!**

Before entering the URL in Meta, test it:
```bash
cd backend
python test_webhook.py https://your-url.com/api/webhook your_verify_token

# Example with ngrok:
python test_webhook.py https://abc123.ngrok.io/api/webhook bharat_biz_verify_2026_secure

# If all tests pass ✅, proceed to Meta!
```

💡 **Having "URL not valid" errors?** See [WEBHOOK_URL_FIX.md](WEBHOOK_URL_FIX.md)

**Configure in Meta**:
1. Meta App Dashboard → WhatsApp → Configuration
2. Click "Configure Webhooks"
3. Enter:
   - **Callback URL**: `https://your-url.com/api/webhook`
   - **Verify Token**: Same as in your `.env` file
4. Click "Verify and Save"
5. Subscribe to fields: `messages` ✅ and `message_status` ✅

**Check logs** - should see:
```
Webhook verified successfully!
```

📖 **Detailed instructions**: [WEBHOOK_QUICK_REF.md](WEBHOOK_QUICK_REF.md)

### Step 5: Test It! (2 minutes)

**Test 1: Send Message**
```bash
curl -X POST http://localhost:8000/api/test/send-message \
  -H "Content-Type: application/json" \
  -d '{
    "to_number": "+919876543210",
    "message": "Hello from Bharat Biz Agent! 🎉"
  }'
```

✅ **Success**: You receive WhatsApp message

**Test 2: Receive Message**
1. Send WhatsApp message to your business number
2. Check server logs - should see message processing
3. System should respond automatically

**Test 3: Try Hinglish Command**
Send on WhatsApp: `"stock check karo"`

✅ **Success**: System responds with inventory info

## You're Live! 🚀

Your WhatsApp business assistant is now operational!

## Next Steps

### Start Frontend (Optional)

```bash
cd frontend
npm install
npm start

# Dashboard available at: http://localhost:3000
```

### Add Your Business Data

**Via Web Dashboard** (http://localhost:3000):
- Add customers
- Add inventory items
- Configure business details

**Via API**:
```bash
# Add customer
curl -X POST http://localhost:8000/api/customers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ramesh Kumar",
    "phone": "+919876543210"
  }'

# Add inventory
curl -X POST http://localhost:8000/api/inventory \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Red Silk Fabric",
    "fabric_type": "silk",
    "color": "red",
    "quantity": 100,
    "rate_per_unit": 450
  }'
```

### Try These Commands on WhatsApp

**Hindi/Hinglish commands**:
```
"Ramesh ko 5000 ka bill banao"         # Create invoice
"red silk ka stock batao"              # Check inventory  
"Ramesh ka udhaar kitna hai"           # Check customer credit
"Ramesh ne 2000 rupay diye"            # Record payment
"low stock items dikhao"               # View low stock
```

**Voice commands**:
- Send voice notes in Hindi/Hinglish
- System transcribes and processes automatically

## Common Issues & Quick Fixes

### ❌ "Webhook verification failed"
- **Fix**: Ensure `WHATSAPP_VERIFY_TOKEN` in `.env` matches Meta Dashboard exactly

### ❌ "401 Unauthorized" when sending messages
- **Fix**: Use permanent token, not temporary one

### ❌ Not receiving messages
- **Fix**: Check webhook is subscribed to "messages" field

### ❌ "whatsapp": "not_configured"
- **Fix**: Check `.env` file has actual values (not placeholders), restart server

📖 **Full troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Documentation Reference

- 📘 [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) - Complete WhatsApp setup guide
- 📙 [WEBHOOK_QUICK_REF.md](WEBHOOK_QUICK_REF.md) - Webhook configuration reference
- 📗 [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) - Step-by-step checklist
- 📕 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Troubleshooting guide
- 📖 [README.md](README.md) - Full project documentation
- 📄 [memory/PRD.md](memory/PRD.md) - Product requirements & features

## Feature Highlights

### 🗣️ Voice-First
- Send voice messages in Hindi/Hinglish
- Automatic speech-to-text via Sarvam AI
- Natural language understanding

### 📄 GST-Compliant Invoices
- Auto-generate invoices
- PDF export
- WhatsApp delivery
- Track payment status

### 💰 Udhaar (Credit) Management
- Track customer credit
- Payment reminders
- Credit limit management
- Human-in-the-loop approval for large credits

### 📦 Inventory Management
- Track textile variants (Fabric × Color × Width)
- Low stock alerts
- Automatic reorder notifications
- Bulk order parsing

### 🔔 Proactive Alerts
- Daily business summary (8 AM IST)
- Low stock alerts (9 AM IST)
- Overdue payment reminders (10 AM IST)
- Weekly credit summary (Monday 9 AM IST)

### 🔒 Security
- DM pairing verification
- PII data masking
- Comprehensive audit logging
- Secure credential management

### 📊 Web Dashboard
- Real-time business metrics
- Customer management
- Inventory tracking
- Invoice generation
- Conversation history

## API Endpoints

**Documentation**: http://localhost:8000/docs

Key endpoints:
- `GET  /api/health` - Health check
- `GET  /api/webhook` - Webhook verification
- `POST /api/webhook` - Receive messages
- `GET  /api/dashboard/stats` - Business stats
- `POST /api/customers` - Create customer
- `POST /api/inventory` - Add inventory item
- `GET  /api/invoices` - List invoices
- `POST /api/test/send-message` - Send test message

## Support & Help

**Getting stuck?**

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) first
2. Review server logs for errors
3. Verify all credentials are correct
4. Ensure server is publicly accessible (HTTPS)
5. Check Meta Developer Console for webhook status

**Need detailed setup help?**
- Follow [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) step-by-step
- Use [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) to track progress

**Meta Resources**:
- [WhatsApp Cloud API Docs](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Meta Developer Community](https://developers.facebook.com/community/)

## Success Checklist

- [x] WhatsApp credentials obtained
- [x] Environment configured (`.env` file)
- [x] Backend server running
- [x] MongoDB connected
- [x] Webhook verified
- [x] Can send WhatsApp messages
- [x] Can receive WhatsApp messages
- [x] System responds to commands
- [x] Frontend dashboard accessible (optional)

## What's Next?

1. **Customize** business information in `.env`
2. **Import** your customer and inventory data
3. **Configure** alert schedules (if needed)
4. **Train** your team on WhatsApp commands
5. **Monitor** quality rating and message limits
6. **Scale** as your business grows

---

**Congratulations!** 🎉 You now have a fully functional AI-powered WhatsApp business assistant!

Start sending commands on WhatsApp and watch your business operations get smarter!

---

## Quick Commands Cheat Sheet

```bash
# Start backend
cd backend && source venv/bin/activate
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Start frontend  
cd frontend && npm start

# Start MongoDB (local)
mongod --dbpath /path/to/data

# Test send message
curl -X POST http://localhost:8000/api/test/send-message \
  -H "Content-Type: application/json" \
  -d '{"to_number": "+91XXXXXXXXXX", "message": "Test"}'

# Check health
curl http://localhost:8000/api/health

# View API docs
open http://localhost:8000/docs
```

**Need help?** Check the documentation files listed above! 📚
