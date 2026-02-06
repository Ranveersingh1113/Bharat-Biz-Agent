# Vercel Deployment Guide for Bharat Biz-Agent

This guide provides step-by-step instructions for deploying the Bharat Biz-Agent to Vercel.

## Overview

The Bharat Biz-Agent is now configured for deployment to Vercel, which provides:
- ✅ Permanent HTTPS URL (not temporary like preview environments)
- ✅ Always online (24/7 availability for Meta webhook verification)
- ✅ Free tier available
- ✅ Easy GitHub integration with auto-deployment
- ✅ Environment variable management

## Files Added for Vercel Deployment

1. **`vercel.json`** - Vercel configuration file
2. **`api/index.py`** - Serverless function entry point for FastAPI
3. **`requirements.txt`** - Python dependencies (copied from backend/)
4. **`.env.example`** - Environment variable template
5. **`.vercelignore`** - Files to exclude from deployment

## Pre-Deployment Checklist

### 1. MongoDB Atlas Setup

1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster (free M0 tier is sufficient for testing)
3. Create a database user with read/write permissions
4. **IMPORTANT**: Configure Network Access:
   - Go to **Network Access** → **Add IP Address**
   - Choose **Allow Access from Anywhere** (0.0.0.0/0)
   - This is required for Vercel serverless functions
5. Get your connection string:
   - Go to **Database** → **Connect** → **Connect your application**
   - Copy the connection string (format: `mongodb+srv://username:password@cluster.mongodb.net/`)
   - Replace `<password>` with your database user password

### 2. WhatsApp Business API Setup

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create or select your app
3. Add WhatsApp product to your app
4. Get the following credentials:
   - **Access Token**: From WhatsApp → API Setup
   - **Phone Number ID**: From WhatsApp → API Setup
   - **Business Account ID**: From WhatsApp → API Setup
5. **IMPORTANT**: Note that you'll configure the webhook URL AFTER deploying to Vercel

### 3. Sarvam AI Setup

1. Sign up at [Sarvam.ai](https://www.sarvam.ai/)
2. Get your API key from the dashboard

## Deployment Steps

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

### Step 3: Deploy to Vercel

```bash
cd /path/to/Bharat-Biz-Agent
vercel
```

Follow the prompts:
- **Set up and deploy**: Yes
- **Which scope**: Select your account
- **Link to existing project**: No (for first deployment)
- **Project name**: `bharat-biz-agent` (or your choice)
- **In which directory is your code located?**: `./` (press Enter)
- **Want to override settings?**: No

Vercel will deploy and give you a URL like: `https://bharat-biz-agent-xxxxx.vercel.app`

### Step 4: Configure Environment Variables

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add the following variables (for **Production**, **Preview**, and **Development**):

#### Required Environment Variables

| Variable Name | Example Value | Description |
|--------------|---------------|-------------|
| `MONGO_URL` | `mongodb+srv://user:pass@cluster.mongodb.net/` | MongoDB connection string from Atlas |
| `DB_NAME` | `bharat_biz_agent` | Database name |
| `SARVAM_API_KEY` | `your_sarvam_api_key` | Sarvam AI API key |
| `WHATSAPP_ACCESS_TOKEN` | `your_meta_token` | Meta WhatsApp access token |
| `WHATSAPP_PHONE_NUMBER_ID` | `123456789` | WhatsApp phone number ID |
| `WHATSAPP_BUSINESS_ACCOUNT_ID` | `987654321` | WhatsApp business account ID |
| `WHATSAPP_VERIFY_TOKEN` | `bharat_biz_verify_2026_secure` | ⚠️ **MUST BE EXACTLY THIS** |
| `WHATSAPP_API_VERSION` | `v18.0` | WhatsApp API version |
| `BUSINESS_NAME` | `Kapoor Textiles` | Your business name |
| `BUSINESS_ADDRESS` | `123 Main St, Delhi` | Your business address |
| `BUSINESS_PHONE` | `+919876543210` | Your business phone |
| `GST_NUMBER` | `07XXXXX1234X1Z5` | Your GST number |
| `BUSINESS_STATE_CODE` | `07` | Your state code (07 for Delhi) |
| `CORS_ORIGINS` | `*` | CORS allowed origins (optional) |

⚠️ **CRITICAL**: The `WHATSAPP_VERIFY_TOKEN` MUST be exactly `bharat_biz_verify_2026_secure` - this is hardcoded in the codebase.

### Step 5: Redeploy with Environment Variables

After adding environment variables, redeploy to production:

```bash
vercel --prod
```

### Step 6: Verify Deployment

Test your deployment:

```bash
curl https://your-project.vercel.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-06T...",
  "database": "connected",
  "whatsapp": "configured",
  "sarvam": "configured"
}
```

### Step 7: Configure Meta Webhook

Now that your app is deployed, configure the webhook in Meta:

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Select your app → **WhatsApp** → **Configuration**
3. In the **Webhook** section, click **Edit**
4. Set the following:
   - **Callback URL**: `https://your-project.vercel.app/api/webhook`
   - **Verify Token**: `bharat_biz_verify_2026_secure`
5. Click **Verify and Save**
6. Subscribe to webhook fields:
   - ✅ `messages`
   - ✅ `message_status`

If verification is successful, you'll see a green checkmark! 🎉

## Troubleshooting

### Webhook Verification Fails

**Symptom**: Meta shows "The callback URL or verify token couldn't be validated"

**Solutions**:
1. Double-check that `WHATSAPP_VERIFY_TOKEN` in Vercel is EXACTLY: `bharat_biz_verify_2026_secure`
2. Ensure the callback URL is correct: `https://your-project.vercel.app/api/webhook` (no trailing slash)
3. Check Vercel deployment logs: `vercel logs`
4. Verify the app is running: `curl https://your-project.vercel.app/api/health`
5. Check that environment variables are set for **Production** environment

### Database Connection Errors

**Symptom**: App starts but can't connect to MongoDB

**Solutions**:
1. Verify MongoDB Atlas Network Access allows 0.0.0.0/0
2. Check `MONGO_URL` has correct username and password
3. Ensure connection string format is correct: `mongodb+srv://...`
4. Test connection string locally first
5. Check Vercel function logs for specific error messages

### Environment Variables Not Working

**Symptom**: App doesn't read environment variables

**Solutions**:
1. After adding/changing environment variables, ALWAYS redeploy: `vercel --prod`
2. Ensure variables are set for the correct environment (Production/Preview/Development)
3. Check variable names match exactly (case-sensitive)
4. View deployment logs to see if variables are being loaded

### Import Errors / Module Not Found

**Symptom**: Deployment fails with "ModuleNotFoundError"

**Solutions**:
1. Check that `requirements.txt` is in the root directory
2. Verify all dependencies are listed in `requirements.txt`
3. Check Vercel build logs for specific missing modules
4. Some packages might not work on Vercel serverless - check compatibility

### Function Timeout

**Symptom**: Requests timeout after 10 seconds

**Solutions**:
1. Vercel free tier has 10-second timeout for serverless functions
2. Optimize database queries and API calls
3. Consider upgrading Vercel plan for longer timeouts
4. Implement async processing for long-running tasks

## Post-Deployment

### Monitor Your Deployment

1. **Vercel Dashboard**: Monitor deployments, view logs, check analytics
2. **Function Logs**: `vercel logs` to see real-time logs
3. **Health Check**: Regularly check `/api/health` endpoint

### Continuous Deployment

Vercel automatically deploys when you push to GitHub:
- **Push to main branch**: Deploys to production
- **Push to other branches**: Creates preview deployments
- **Pull requests**: Creates preview deployments with unique URLs

### Update Environment Variables

To update environment variables:
1. Go to Vercel Dashboard → Settings → Environment Variables
2. Update the value
3. Redeploy: `vercel --prod`

## Testing the Full Flow

1. **Test Health Endpoint**:
   ```bash
   curl https://your-project.vercel.app/api/health
   ```

2. **Test Webhook Verification** (simulate Meta's verification):
   ```bash
   curl "https://your-project.vercel.app/api/webhook?hub.mode=subscribe&hub.verify_token=bharat_biz_verify_2026_secure&hub.challenge=test123"
   ```
   Expected: Returns `test123`

3. **Send a WhatsApp Message**: Send a message to your WhatsApp Business number and verify it's processed

## Important Notes

- ⚠️ The verify token `bharat_biz_verify_2026_secure` is hardcoded in the application
- ⚠️ Never commit `.env` files to Git (they're already in `.gitignore`)
- ✅ Use `.env.example` as a template for local development
- ✅ MongoDB Atlas free tier is sufficient for testing and small production deployments
- ✅ Vercel free tier is sufficient for most use cases

## Support

- **Vercel Documentation**: https://vercel.com/docs
- **FastAPI on Vercel**: https://vercel.com/docs/frameworks/fastapi
- **MongoDB Atlas**: https://www.mongodb.com/docs/atlas/
- **WhatsApp Business API**: https://developers.facebook.com/docs/whatsapp

## Summary

Your deployment should now be:
- ✅ Running on Vercel with a permanent HTTPS URL
- ✅ Connected to MongoDB Atlas
- ✅ Configured with Meta WhatsApp webhook
- ✅ Ready to receive and process WhatsApp messages 24/7

For any issues, check the Troubleshooting section above or review the Vercel deployment logs.
