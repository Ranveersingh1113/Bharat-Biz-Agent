# Bharat Biz-Agent - Product Requirements Document

## Overview
AI-powered WhatsApp-native business assistant for Indian SMBs in textile retail sector. Supports Hinglish (Hindi + English) voice and text commands.

## Original Problem Statement
Build a voice-first, WhatsApp-native AI co-pilot for textile retailers (Neurathon 2026) with:
- Invoice generation (GST-compliant)
- Udhaar (credit) management with HITL approval
- Textile inventory with variant tracking
- UPI fraud detection awareness
- Full WhatsApp Cloud API integration
- Proactive alerts via cron scheduler
- DM pairing security

## Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React.js with Tailwind CSS
- **Database**: MongoDB
- **NLP**: Sarvam AI (Sarvam-M for Hinglish understanding)
- **STT**: Sarvam Saarika v2.5 for voice transcription
- **Messaging**: WhatsApp Cloud API
- **Scheduler**: APScheduler for proactive alerts

### Key Components
1. **Agent Orchestrator**: Routes intents to appropriate handlers
2. **Sarvam Service**: Hinglish NLP and speech-to-text
3. **WhatsApp Service**: Message sending/receiving, media handling
4. **Invoice Service**: GST-compliant invoice generation with PDF
5. **Inventory Service**: Textile variant tracking (Color × Fabric × Width)
6. **Udhaar Service**: Credit management with HITL safety
7. **Bulk Order Service**: Multi-variant order parsing
8. **Scheduler Service**: Proactive daily/weekly alerts
9. **Security Service**: DM pairing, PII masking, audit logging

## User Personas
1. **Ramesh Kapoor** (Shop Owner) - Voice-first, Hinglish speaker
2. **Priya Sharma** (Shop Assistant) - Tech-savvy, prefers text
3. **Suresh Gupta** (Bulk Buyer) - Complex multi-variant orders

## Implementation Status (Feb 4, 2026)

### P0 Features ✅ COMPLETED
- [x] Voice-to-invoice generation (Saarika STT integrated)
- [x] Hinglish text command processing (Sarvam-M)
- [x] Customer management with credit tracking
- [x] Textile inventory with variants (Color × Fabric × Width)
- [x] Udhaar (credit) management with HITL approval
- [x] WhatsApp webhook integration
- [x] Web dashboard for business metrics

### P1 Features ✅ COMPLETED
- [x] PDF Invoice generation (HTML fallback if WeasyPrint unavailable)
- [x] Bulk order parsing (multi-variant: "1000m - 400 red silk, 300 blue cotton")
- [x] Low stock alerts
- [x] HITL approval workflow
- [x] Payment recording
- [x] Invoice status tracking
- [x] Proactive scheduler (daily summary, low stock, overdue reminders, weekly report)

### P2 Features ✅ COMPLETED
- [x] DM Pairing security (6-digit code verification)
- [x] PII Masking (phone, email, GST, Aadhaar, PAN)
- [x] Audit logging with PII-safe records
- [x] Full web dashboard

### Remaining / Future
- [ ] UPI screenshot OCR verification (currently warns only)
- [ ] WhatsApp document sharing for PDF invoices
- [ ] Multi-store support
- [ ] Supplier management
- [ ] GST filing integration

## API Endpoints

### Core APIs
- `/api/health` - Health check
- `/api/dashboard/stats` - Dashboard metrics
- `/api/customers` - Customer CRUD
- `/api/inventory` - Inventory management
- `/api/invoices` - Invoice management with PDF generation
- `/api/udhaar/*` - Credit management
- `/api/hitl/*` - HITL approvals
- `/api/webhook` - WhatsApp webhook

### New APIs
- `/api/test/parse-bulk-order` - Test bulk order parsing
- `/api/scheduler/status` - View scheduled jobs
- `/api/scheduler/trigger/{type}` - Manually trigger alerts
- `/api/security/pairing/*` - Device pairing
- `/api/audit/logs` - Audit trail

## Configuration

### WhatsApp Webhook Setup
```
Callback URL: https://file-analyzer-91.preview.emergentagent.com/api/webhook
Verify Token: bharat_biz_verify_2026_secure
```

### Scheduled Jobs (IST)
- Daily Summary: 8:00 AM
- Low Stock Alerts: 9:00 AM
- Overdue Reminders: 10:00 AM
- Weekly Credit Summary: Monday 9:00 AM

## Test Commands (Hinglish)
```
Invoice: "Ramesh ko 5000 ka bill bhejo"
Stock: "red silk ka stock check karo"
Udhaar: "Suresh ka udhaar batao"
Payment: "Suresh ne GPay se 10000 bheja"
Bulk Order: "1000 meter chahiye - 400 red silk, 300 blue cotton, 300 green poly"
Low Stock: "low stock items batao"
```

## Next Tasks
1. Configure WhatsApp webhook in Meta Business dashboard
2. Test live WhatsApp message flow with real device
3. Add voice response using Sarvam TTS
4. Implement UPI screenshot OCR verification
