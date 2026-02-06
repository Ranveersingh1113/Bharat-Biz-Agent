# WhatsApp Configuration Checklist

Use this checklist to track your progress through the WhatsApp setup process.

## Prerequisites ✓

- [ ] Facebook Business Account created
- [ ] Phone number available (not on regular WhatsApp)
- [ ] Server with HTTPS capability
- [ ] Basic understanding of webhooks

## Phase 1: Meta App Setup

### Step 1: Create Meta Business App
- [ ] Go to [Meta for Developers](https://developers.facebook.com/)
- [ ] Create new app (type: "Business")
- [ ] Name your app
- [ ] Link to Business Account
- [ ] App created successfully ✅

### Step 2: Add WhatsApp Product
- [ ] Add WhatsApp product to app
- [ ] Navigate to WhatsApp section
- [ ] Access WhatsApp Getting Started page ✅

### Step 3: Configure Business Account
- [ ] Select or create WhatsApp Business Account
- [ ] Business Account linked ✅

### Step 4: Add Phone Number
- [ ] Choose: Test number OR Own number
- [ ] If test number: Note the number
- [ ] If own number: Verify with code
- [ ] Phone number active ✅

## Phase 2: Collect Credentials

### Required Credentials Checklist
Copy these from Meta Dashboard to your notes:

- [ ] **Phone Number ID**: `___________________________________`
- [ ] **Business Account ID**: `___________________________________`
- [ ] **Temporary Access Token**: `___________________________________`
- [ ] Test number (if using): `___________________________________`

### Generate Permanent Access Token
- [ ] Go to Meta Business Manager
- [ ] Navigate to System Users
- [ ] Create new system user
- [ ] Assign app with full control
- [ ] Generate token with permissions:
  - [ ] whatsapp_business_messaging
  - [ ] whatsapp_business_management
- [ ] **Permanent Access Token**: `___________________________________`
- [ ] Token saved securely ✅

## Phase 3: Local Setup

### Backend Environment Configuration
- [ ] Navigate to `backend/` directory
- [ ] Copy `.env.example` to `.env`
- [ ] Fill in `.env` with collected credentials:

```bash
# WhatsApp Configuration
WHATSAPP_ACCESS_TOKEN=         # ← Paste permanent token here
WHATSAPP_PHONE_NUMBER_ID=      # ← Paste phone number ID here
WHATSAPP_BUSINESS_ACCOUNT_ID=  # ← Paste business account ID here
WHATSAPP_VERIFY_TOKEN=         # ← Create a random string (20+ chars)
WHATSAPP_API_VERSION=v18.0     # ← Keep default
```

- [ ] Set other required variables:
  - [ ] MONGO_URL
  - [ ] SARVAM_API_KEY
  - [ ] BUSINESS_NAME
  - [ ] BUSINESS_PHONE
- [ ] `.env` file complete ✅

### Install Dependencies
- [ ] Create Python virtual environment
- [ ] Activate virtual environment
- [ ] Run `pip install -r requirements.txt`
- [ ] All dependencies installed ✅

### Start Backend Server
- [ ] Run: `python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000`
- [ ] Server running without errors
- [ ] Visit `http://localhost:8000/api/health`
- [ ] Health check returns OK ✅

## Phase 4: Make Server Public

Choose one option:

### Option A: Tunneling (Development)
- [ ] Install ngrok: `brew install ngrok`
- [ ] Run: `ngrok http 8000`
- [ ] Note HTTPS URL: `___________________________________`
- [ ] Keep ngrok running ✅

### Option B: Cloud Deployment (Production)
- [ ] Deploy to cloud platform (AWS/GCP/Heroku/etc.)
- [ ] Configure HTTPS/SSL certificate
- [ ] Note public URL: `___________________________________`
- [ ] Server accessible via HTTPS ✅

## Phase 5: Webhook Configuration

### Configure in Meta Dashboard
- [ ] Go to Meta App > WhatsApp > Configuration
- [ ] Click "Configure Webhooks"
- [ ] Enter Callback URL: `https://your-url.com/api/webhook`
- [ ] Enter Verify Token (same as in .env)
- [ ] Click "Verify and Save"
- [ ] Check logs for: "Webhook verified successfully!"
- [ ] Verification successful ✅

### Subscribe to Webhook Fields
- [ ] Subscribe to "messages"
- [ ] Subscribe to "message_status"
- [ ] Subscriptions active ✅

## Phase 6: Testing

### Test 1: Send Message (API → WhatsApp)
- [ ] Use test endpoint or curl:
```bash
curl -X POST http://localhost:8000/api/test/send-message \
  -H "Content-Type: application/json" \
  -d '{"to_number": "+919876543210", "message": "Test"}'
```
- [ ] Message sent successfully
- [ ] Message received on WhatsApp ✅

### Test 2: Receive Message (WhatsApp → API)
- [ ] For test number: Add recipient number in Meta Dashboard
- [ ] Send WhatsApp message to your business number
- [ ] Check server logs for incoming webhook
- [ ] System responds automatically ✅

### Test 3: End-to-End Flow
- [ ] Send: "red silk ka stock check karo"
- [ ] System processes message
- [ ] System responds with stock info
- [ ] Full flow working ✅

## Phase 7: Production Readiness

### Security Review
- [ ] `.env` file in `.gitignore`
- [ ] No credentials in code
- [ ] HTTPS enabled
- [ ] Verify token is strong (20+ characters)
- [ ] Access token stored securely
- [ ] Security measures in place ✅

### Business Verification (if required)
- [ ] Submit business verification documents
- [ ] Wait for Meta approval
- [ ] Business verified ✅

### Message Tier Status
- [ ] Check current tier limit
- [ ] Monitor quality rating
- [ ] Plan for tier upgrades
- [ ] Tier management understood ✅

### Monitoring Setup
- [ ] Set up application logging
- [ ] Monitor webhook requests
- [ ] Set up error alerts
- [ ] Monitoring configured ✅

## Phase 8: Frontend & Additional Services

### Frontend Setup
- [ ] Navigate to `frontend/` directory
- [ ] Run `npm install`
- [ ] Run `npm start`
- [ ] Dashboard accessible at `http://localhost:3000` ✅

### Database Setup
- [ ] MongoDB installed/configured
- [ ] Database connection tested
- [ ] Sample data seeded
- [ ] Database operational ✅

### AI Services
- [ ] Sarvam AI account created
- [ ] API key obtained
- [ ] API key in `.env`
- [ ] Test STT/NLP functionality ✅

## Final Verification

### Complete System Test
- [ ] Send voice message in Hinglish
- [ ] System transcribes correctly
- [ ] System understands intent
- [ ] System executes action
- [ ] Response received on WhatsApp
- [ ] Dashboard shows activity
- [ ] **System fully operational** ✅

## Common Issues Checklist

If something doesn't work, check:

- [ ] Is backend server running?
- [ ] Is server publicly accessible via HTTPS?
- [ ] Does verify token match exactly in .env and Meta?
- [ ] Is access token the permanent one (not expired temp token)?
- [ ] Are webhook subscriptions active?
- [ ] For test numbers: Is recipient in approved list?
- [ ] Are there any errors in server logs?
- [ ] Is MongoDB connected?
- [ ] Is Sarvam API key valid?

## Support Resources

- [ ] Bookmark: [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) - Complete guide
- [ ] Bookmark: [WEBHOOK_QUICK_REF.md](WEBHOOK_QUICK_REF.md) - Quick reference
- [ ] Bookmark: [Meta WhatsApp Docs](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [ ] Bookmark: API docs at `/docs`

## Completion

- [ ] All checklist items completed
- [ ] System tested and working
- [ ] Documentation reviewed
- [ ] Ready for production use

**Setup Date**: _______________  
**Completed By**: _______________  
**Notes**: _____________________

---

## Next Steps After Setup

1. Customize business information in `.env`
2. Add your actual inventory items
3. Add your customer data
4. Configure scheduled alerts timing
5. Train your team on WhatsApp commands
6. Monitor initial usage and quality rating
7. Plan for scaling (message tier upgrades)

## Quick Commands Reference

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
  -d '{"to_number": "+91XXXXXXXXXX", "message": "Test message"}'

# View logs
tail -f backend/logs/app.log  # if logging to file
```

Congratulations on completing the WhatsApp setup! 🎉
