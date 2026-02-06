# Bharat Biz-Agent

AI-powered WhatsApp-native business assistant for Indian SMBs in textile retail sector. Supports Hinglish (Hindi + English) voice and text commands.

## Features

- 🎤 Voice-to-invoice generation (Hinglish support)
- 📱 WhatsApp Cloud API integration
- 💰 Udhaar (credit) management with HITL approval
- 📦 Textile inventory management with variants
- 📄 GST-compliant invoice generation (PDF)
- 🔔 Proactive alerts via scheduler
- 🔐 DM pairing security
- 📊 Web dashboard for business metrics

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React.js with Tailwind CSS
- **Database**: MongoDB
- **NLP**: Sarvam AI (Sarvam-M for Hinglish)
- **STT**: Sarvam Saarika v2.5
- **Messaging**: WhatsApp Cloud API

## Deployment to Vercel

### Prerequisites

1. A [Vercel](https://vercel.com) account
2. [Vercel CLI](https://vercel.com/docs/cli) installed: `npm i -g vercel`
3. MongoDB database (MongoDB Atlas recommended)
4. WhatsApp Business API credentials
5. Sarvam AI API key

### Step 1: Install Vercel CLI

```bash
npm i -g vercel
```

### Step 2: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your environment variables in `.env`:
   - `MONGO_URL` - Your MongoDB connection string (from MongoDB Atlas)
   - `WHATSAPP_VERIFY_TOKEN` - Use `bharat_biz_verify_2026_secure` (must match Meta configuration)
   - `WHATSAPP_ACCESS_TOKEN` - Your Meta WhatsApp access token
   - `WHATSAPP_PHONE_NUMBER_ID` - Your WhatsApp phone number ID
   - `WHATSAPP_BUSINESS_ACCOUNT_ID` - Your WhatsApp business account ID
   - `SARVAM_API_KEY` - Your Sarvam API key
   - Business details (name, address, phone, GST number, etc.)

### Step 3: Deploy to Vercel

```bash
cd /path/to/Bharat-Biz-Agent
vercel
```

Follow the prompts:
- Set up and deploy: **Yes**
- Which scope: Select your account
- Link to existing project: **No** (for first deploy)
- Project name: `bharat-biz-agent` (or your choice)
- Directory: `./` (press Enter)
- Override settings: **No**

### Step 4: Set Environment Variables on Vercel

After deployment, set environment variables in Vercel Dashboard:

1. Go to your project on [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on **Settings** → **Environment Variables**
3. Add all variables from your `.env` file:
   - `MONGO_URL`
   - `DB_NAME`
   - `SARVAM_API_KEY`
   - `WHATSAPP_ACCESS_TOKEN`
   - `WHATSAPP_PHONE_NUMBER_ID`
   - `WHATSAPP_BUSINESS_ACCOUNT_ID`
   - `WHATSAPP_VERIFY_TOKEN` (must be `bharat_biz_verify_2026_secure`)
   - `WHATSAPP_API_VERSION`
   - `BUSINESS_NAME`
   - `BUSINESS_ADDRESS`
   - `BUSINESS_PHONE`
   - `GST_NUMBER`
   - `BUSINESS_STATE_CODE`

4. Redeploy: `vercel --prod`

### Step 5: Configure Meta WhatsApp Webhook

After deployment, you'll get a Vercel URL like: `https://bharat-biz-agent.vercel.app`

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Select your app → WhatsApp → Configuration
3. Set webhook:
   - **Callback URL**: `https://your-project.vercel.app/api/webhook`
   - **Verify Token**: `bharat_biz_verify_2026_secure` (must match `WHATSAPP_VERIFY_TOKEN`)
4. Subscribe to webhook fields:
   - `messages`
   - `message_status`

### Step 6: Verify Deployment

Check if your app is running:

```bash
curl https://your-project.vercel.app/api/health
```

You should see:
```json
{
  "status": "healthy",
  "database": "connected",
  "whatsapp": "configured",
  "sarvam": "configured"
}
```

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB (local or Atlas)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env
# Fill in .env with your credentials
uvicorn server:app --reload
```

Backend will run on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:3000`

## API Documentation

Once deployed, visit `https://your-project.vercel.app/docs` for interactive API documentation.

### Key Endpoints

- `GET /api/health` - Health check
- `GET /api/webhook` - WhatsApp webhook verification
- `POST /api/webhook` - WhatsApp webhook receiver
- `GET /api/dashboard/stats` - Dashboard metrics
- `GET /api/customers` - Customer management
- `GET /api/inventory` - Inventory management
- `GET /api/invoices` - Invoice management

## Testing

Run backend tests:

```bash
python backend_test.py
```

## Troubleshooting

### Webhook Verification Fails

1. Ensure `WHATSAPP_VERIFY_TOKEN` in Vercel exactly matches the token in Meta configuration
2. Check Vercel logs: `vercel logs`
3. Verify the callback URL is correct: `https://your-project.vercel.app/api/webhook`

### Database Connection Issues

1. Ensure MongoDB Atlas allows connections from all IPs (0.0.0.0/0) for Vercel
2. Check `MONGO_URL` is correct in Vercel environment variables
3. Verify database name in `DB_NAME` variable

### Environment Variables Not Working

1. After adding/changing environment variables in Vercel, always redeploy
2. Use `vercel --prod` to deploy to production
3. Check environment variables are set in both **Production** and **Preview** environments

## Support

For issues or questions, please check the [PRD documentation](memory/PRD.md) or create an issue.

## License

MIT
