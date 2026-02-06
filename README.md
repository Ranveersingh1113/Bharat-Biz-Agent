# Bharat Biz-Agent

AI-powered WhatsApp-native business assistant for Indian SMBs in the textile retail sector. Supports Hinglish (Hindi + English) voice and text commands.

> 📚 **New to setup?** Check the [Documentation Index (DOCS_INDEX.md)](DOCS_INDEX.md) for a guide to all available documentation, or jump straight to the [Quick Start Guide (QUICKSTART.md)](QUICKSTART.md) for a 30-minute setup!

## Features

- 📱 **WhatsApp-Native**: Full WhatsApp Cloud API integration for messaging
- 🗣️ **Voice-First**: Hinglish voice command support via Sarvam AI
- 📄 **GST-Compliant Invoices**: Automatic invoice generation with PDF export
- 💰 **Udhaar Management**: Credit tracking with Human-in-the-Loop approval
- 📦 **Inventory Management**: Textile variant tracking (Color × Fabric × Width)
- 🔔 **Proactive Alerts**: Scheduled daily summaries, low stock alerts, overdue reminders
- 🔒 **Security**: DM pairing, PII masking, comprehensive audit logging
- 📊 **Web Dashboard**: Real-time business metrics and management

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 16+ and npm
- MongoDB (local or Atlas)
- Meta WhatsApp Business API account
- Sarvam AI API key

### 1. WhatsApp Configuration (IMPORTANT)

⚠️ **You must configure WhatsApp Business API first!**

Follow the comprehensive guide: **[WHATSAPP_SETUP.md](WHATSAPP_SETUP.md)**

This guide covers:
- Creating a Meta Business App
- Setting up WhatsApp Business Account
- Getting access tokens and credentials
- Configuring webhooks
- Testing your setup

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials (see WHATSAPP_SETUP.md for details)

# Start the server
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000`

### 4. MongoDB Setup

**Option A: Local MongoDB**
```bash
# Install MongoDB and start the service
mongod --dbpath /path/to/data
```

**Option B: MongoDB Atlas (Recommended)**
1. Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Get your connection string
3. Update `MONGO_URL` in `.env`

## Configuration

### Environment Variables

All configuration is done via environment variables. See:
- `backend/.env.example` - Template with all available options
- `WHATSAPP_SETUP.md` - Detailed guide for WhatsApp credentials

Key variables:
```bash
# WhatsApp
WHATSAPP_ACCESS_TOKEN=         # Your permanent access token
WHATSAPP_PHONE_NUMBER_ID=      # Your phone number ID
WHATSAPP_VERIFY_TOKEN=         # Your webhook verify token

# Database
MONGO_URL=                     # MongoDB connection string

# AI Services
SARVAM_API_KEY=               # Sarvam AI API key

# Business Details
BUSINESS_NAME=                 # Your business name
GST_NUMBER=                   # Your GST number (optional)
```

## Usage

### Via WhatsApp

Send messages to your WhatsApp Business number:

**Hindi/Hinglish Commands:**
```
"Ramesh ko 5000 ka bill bhejo"       # Create invoice
"red silk ka stock check karo"       # Check inventory
"Suresh ka udhaar batao"            # Check customer credit
"Suresh ne GPay se 10000 bheja"     # Record payment
"low stock items batao"             # Get low stock alerts
```

**Voice Commands:**
- Send voice notes in Hindi/Hinglish
- The system will transcribe and process them automatically

### Via Web Dashboard

Access the dashboard at `http://localhost:3000` to:
- View business metrics and statistics
- Manage customers and inventory
- Generate and view invoices
- Track credit (udhaar) and payments
- Approve HITL requests
- View conversation history

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Key endpoints:
- `/api/webhook` - WhatsApp webhook (GET for verification, POST for messages)
- `/api/customers` - Customer management
- `/api/inventory` - Inventory management
- `/api/invoices` - Invoice generation and retrieval
- `/api/dashboard/stats` - Business statistics

## Testing

### Test WhatsApp Integration

```bash
# Send a test message
curl -X POST http://localhost:8000/api/test/send-message \
  -H "Content-Type: application/json" \
  -d '{"to_number": "+919876543210", "message": "Test message"}'

# Test text processing
curl -X POST http://localhost:8000/api/test/process-text \
  -H "Content-Type: application/json" \
  -d '{"text": "Ramesh ka udhaar batao", "phone": "+919876543210"}'
```

### Run Backend Tests

```bash
cd backend
python -m pytest backend_test.py -v
```

## Architecture

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React.js with Tailwind CSS
- **Database**: MongoDB
- **NLP**: Sarvam AI (Hinglish understanding & Speech-to-Text)
- **Messaging**: WhatsApp Cloud API
- **Scheduler**: APScheduler for proactive alerts

## Project Structure

```
Bharat-Biz-Agent/
├── backend/
│   ├── agents/              # AI agent orchestration
│   ├── services/            # Business logic services
│   ├── config.py           # Configuration management
│   ├── models.py           # Data models
│   ├── server.py           # FastAPI server
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template
├── frontend/
│   ├── src/                # React components
│   ├── public/             # Static assets
│   └── package.json        # Node dependencies
├── memory/
│   └── PRD.md             # Product requirements
├── WHATSAPP_SETUP.md      # WhatsApp setup guide
└── README.md              # This file
```

## Troubleshooting

### WhatsApp Issues

If you're having trouble with WhatsApp configuration:
1. Read [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) carefully
2. Check the "Common Issues and Troubleshooting" section
3. Verify your webhook is accessible and HTTPS
4. Ensure access tokens are correct and not expired

### Common Errors

**"Webhook verification failed"**
- Check that `WHATSAPP_VERIFY_TOKEN` in `.env` matches Meta configuration
- Ensure server is running and accessible
- Verify webhook URL is correct and HTTPS

**"401 Unauthorized" when sending messages**
- Verify `WHATSAPP_ACCESS_TOKEN` is correct
- Use permanent token, not temporary
- Check token permissions in Meta Business Manager

**Messages not being received**
- Verify webhook is subscribed to `messages` field
- Check if phone number is in test recipient list (for test numbers)
- Review server logs for webhook requests

## Security

- Never commit `.env` file
- Use environment variables for production
- Rotate access tokens regularly
- Keep Sarvam AI key secure
- Review audit logs regularly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions:
- Check the [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) guide
- Review API documentation at `/docs`
- Check application logs for errors
- See [PRD.md](memory/PRD.md) for detailed feature documentation

## Acknowledgments

- Built for Neurathon 2026
- Powered by Sarvam AI for Hinglish support
- Uses Meta WhatsApp Business Cloud API
