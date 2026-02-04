# Bharat Biz-Agent - Product Requirements Document

## Overview
AI-powered WhatsApp-native business assistant for Indian SMBs in textile retail sector. Supports Hinglish (Hindi + English) voice and text commands.

## Original Problem Statement
Build a voice-first, WhatsApp-native AI co-pilot for textile retailers with:
- Invoice generation (GST-compliant)
- Udhaar (credit) management with HITL approval
- Textile inventory with variant tracking
- UPI fraud detection awareness
- Full WhatsApp Cloud API integration

## Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React.js with Tailwind CSS
- **Database**: MongoDB
- **NLP**: Sarvam AI (Sarvam-M for Hinglish understanding)
- **STT**: Sarvam Saarika v2.5 for voice transcription
- **Messaging**: WhatsApp Cloud API

### Key Components
1. **Agent Orchestrator**: Routes intents to appropriate handlers
2. **Sarvam Service**: Hinglish NLP and speech-to-text
3. **WhatsApp Service**: Message sending/receiving, media handling
4. **Invoice Service**: GST-compliant invoice generation
5. **Inventory Service**: Textile variant tracking
6. **Udhaar Service**: Credit management with HITL safety

## User Personas
1. **Ramesh Kapoor** (Shop Owner) - Voice-first, Hinglish speaker
2. **Priya Sharma** (Shop Assistant) - Tech-savvy, prefers text
3. **Suresh Gupta** (Bulk Buyer) - Complex multi-variant orders

## Core Requirements (Implemented)

### P0 Features ✅
- [x] Voice-to-invoice generation (<5 seconds)
- [x] Hinglish text command processing
- [x] Customer management with credit tracking
- [x] Textile inventory with variants (Color × Fabric × Width)
- [x] Udhaar (credit) management
- [x] WhatsApp webhook integration
- [x] Web dashboard for business metrics

### P1 Features ✅
- [x] Low stock alerts
- [x] HITL approval workflow
- [x] Payment recording
- [x] Invoice status tracking

## What's Been Implemented (Feb 4, 2026)

### Backend APIs
- `/api/health` - Health check
- `/api/dashboard/stats` - Dashboard metrics
- `/api/customers` - Customer CRUD
- `/api/inventory` - Inventory management
- `/api/invoices` - Invoice management
- `/api/udhaar/*` - Credit management
- `/api/hitl/*` - HITL approvals
- `/api/webhook` - WhatsApp webhook
- `/api/test/*` - Agent testing endpoints

### Frontend Pages
- Dashboard with stats cards
- Customers list
- Inventory with variant filters
- Invoices list
- Udhaar management
- HITL Approvals
- Agent test chat interface

### Integrations
- Sarvam AI (Sarvam-M + Saarika v2.5)
- WhatsApp Cloud API
- MongoDB

## Configuration

### WhatsApp Webhook Setup
```
Callback URL: https://file-analyzer-91.preview.emergentagent.com/api/webhook
Verify Token: bharat_biz_verify_2026_secure
```

### Environment Variables
- `SARVAM_API_KEY` - Sarvam AI API key
- `WHATSAPP_ACCESS_TOKEN` - WhatsApp Cloud API token
- `WHATSAPP_PHONE_NUMBER_ID` - WhatsApp phone number ID
- `MONGO_URL` - MongoDB connection string

## Backlog / Future Features

### P0 Remaining
- [ ] PDF invoice generation and WhatsApp document sharing
- [ ] Actual UPI screenshot fraud detection (OCR-based)

### P1
- [ ] Bulk order processing with multi-variant parsing
- [ ] Automatic payment reminders via WhatsApp
- [ ] Customer credit history export

### P2
- [ ] Multi-store support
- [ ] Supplier management
- [ ] GST filing integration
- [ ] Analytics dashboard

## Next Tasks
1. Set up WhatsApp webhook in Meta Business dashboard
2. Test live WhatsApp message flow
3. Implement PDF invoice generation
4. Add payment screenshot OCR verification
