# WhatsApp Business API Setup Guide for Meta Platform

This guide will help you configure the WhatsApp Business API on the Meta (Facebook) platform for the Bharat-Biz-Agent project.

## Prerequisites

- A Facebook Business Account
- A verified phone number that is not already on WhatsApp
- A Meta Business Manager account
- Access to your server/hosting with HTTPS enabled

## Step-by-Step Setup

### 1. Create a Meta Business App

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click on **"My Apps"** in the top right corner
3. Click **"Create App"**
4. Select **"Business"** as the app type
5. Fill in the following details:
   - **App Name**: Choose a name (e.g., "Bharat Biz Agent")
   - **App Contact Email**: Your business email
   - **Business Account**: Select or create a business account
6. Click **"Create App"**

### 2. Add WhatsApp Product to Your App

1. In your app dashboard, scroll down to **"Add Products to Your App"**
2. Find **"WhatsApp"** and click **"Set Up"**
3. You'll be redirected to the WhatsApp Getting Started page

### 3. Configure WhatsApp Business Account

1. In the WhatsApp section, you'll see **"Start using the API"**
2. Select or create a **WhatsApp Business Account**
3. Click **"Continue"**

### 4. Add a Phone Number

1. You'll be prompted to add a phone number
2. Choose one of these options:
   - **Use the test number provided by Meta** (for development/testing)
   - **Add your own phone number** (for production)

#### Option A: Using Meta's Test Number (Recommended for Initial Testing)

1. Meta provides a temporary test phone number
2. You can send messages to up to 5 pre-verified test recipient numbers
3. This is perfect for initial development and testing

#### Option B: Adding Your Own Phone Number (For Production)

1. Click **"Add Phone Number"**
2. Enter your business phone number (must not be already on WhatsApp)
3. Choose **"Text message"** or **"Voice call"** for verification
4. Enter the verification code you receive
5. Complete the phone number verification

**Important Notes:**
- The phone number cannot be already registered with regular WhatsApp
- You'll need to verify business details for production use
- Some regions may require business verification

### 5. Get Your Access Tokens and IDs

After adding a phone number, you'll need to collect the following credentials:

#### A. Temporary Access Token (For Testing)

1. In the WhatsApp > API Setup section, you'll see a **"Temporary access token"**
2. Copy this token - it's valid for 24 hours
3. This is your `WHATSAPP_ACCESS_TOKEN` (temporary)

#### B. Phone Number ID

1. In the same section, look for **"Phone number ID"**
2. Copy this ID - it's your `WHATSAPP_PHONE_NUMBER_ID`

#### C. WhatsApp Business Account ID

1. Look for **"WhatsApp Business Account ID"** in the settings
2. Copy this ID - it's your `WHATSAPP_BUSINESS_ACCOUNT_ID`

### 6. Generate a Permanent Access Token

The temporary token expires in 24 hours. For production, you need a permanent token:

1. Go to **Business Settings** in Meta Business Manager
2. Navigate to **System Users** under Users
3. Click **"Add"** to create a new system user
4. Give it a name (e.g., "Bharat Biz Agent API")
5. Set the role to **"Admin"**
6. Click **"Create System User"**
7. Click on the newly created system user
8. Click **"Add Assets"**
9. Select **"Apps"** and add your WhatsApp app
10. Toggle **"Full control"** for the app
11. Click **"Generate New Token"**
12. Select your app and choose the following permissions:
    - `whatsapp_business_messaging`
    - `whatsapp_business_management`
13. Copy the generated token - this is your permanent `WHATSAPP_ACCESS_TOKEN`

**Important:** Store this token securely! It won't be shown again.

### 7. Set Up Webhook for Receiving Messages

Webhooks allow your application to receive incoming WhatsApp messages.

#### A. Configure Your Webhook URL

1. In the WhatsApp > Configuration section, find **"Webhook"**
2. Click **"Configure Webhooks"** or **"Edit"**
3. Enter your webhook details:
   - **Callback URL**: `https://your-domain.com/api/webhook`
     - Example: `https://bharatbiz.example.com/api/webhook`
     - Must be HTTPS
     - Must be publicly accessible
   - **Verify Token**: Create a random string (e.g., `bharat_biz_verify_2026_secure`)
     - This is your `WHATSAPP_VERIFY_TOKEN`
4. Click **"Verify and Save"**

**Note:** Meta will send a GET request to your webhook URL to verify it. Make sure your server is running and the endpoint is accessible.

#### B. Subscribe to Webhook Fields

After verifying the webhook, subscribe to the following fields:
- ✅ `messages` - To receive incoming messages
- ✅ `message_status` - To receive message status updates (sent, delivered, read)

Click **"Subscribe"** for each field.

### 8. Configure Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```bash
# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=bharat_biz_agent

# Sarvam AI Configuration
SARVAM_API_KEY=your_sarvam_api_key_here

# WhatsApp Business API Configuration
WHATSAPP_ACCESS_TOKEN=your_permanent_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id_here
WHATSAPP_VERIFY_TOKEN=bharat_biz_verify_2026_secure
WHATSAPP_API_VERSION=v18.0

# Business Configuration
BUSINESS_NAME=Your Business Name
BUSINESS_ADDRESS=Your Business Address
BUSINESS_PHONE=+919876543210
GST_NUMBER=your_gst_number
BUSINESS_STATE_CODE=07

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
```

### 9. Test Your Configuration

#### A. Test Sending a Message

1. Start your backend server:
   ```bash
   cd backend
   python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```

2. Use the test endpoint to send a message:
   ```bash
   curl -X POST http://localhost:8000/api/test/send-message \
     -H "Content-Type: application/json" \
     -d '{
       "to_number": "+919876543210",
       "message": "Hello from Bharat Biz Agent!"
     }'
   ```

#### B. Test Webhook Verification

1. Meta will automatically verify your webhook when you configure it
2. Check your server logs for verification requests
3. You should see: `Webhook verified successfully!`

#### C. Test Receiving Messages

1. If using Meta's test number, add test recipient numbers in the Meta dashboard
2. Send a WhatsApp message from a test number to your WhatsApp Business number
3. Check your server logs - you should see the incoming message
4. The app should respond automatically

### 10. Production Checklist

Before going live, ensure:

- ✅ You have a permanent access token (not the temporary one)
- ✅ Your webhook URL is HTTPS and publicly accessible
- ✅ You've completed business verification (if required in your region)
- ✅ You've reviewed and accepted WhatsApp Business API Terms
- ✅ Your phone number is verified and active
- ✅ You've tested sending and receiving messages
- ✅ Your `.env` file is secured and not committed to git
- ✅ You've set up proper error logging and monitoring

## Common Issues and Troubleshooting

### Issue 1: Webhook Verification Failed

**Symptoms:** Meta shows "Verification Failed" when setting up webhook

**Solutions:**
- Ensure your server is running and accessible
- Verify the webhook URL is correct and HTTPS
- Check that the verify token matches exactly (case-sensitive)
- Check server logs for incoming verification requests
- Ensure the webhook endpoint returns the challenge correctly

### Issue 2: Messages Not Being Received

**Symptoms:** Can't receive WhatsApp messages

**Solutions:**
- Verify webhook is properly configured and subscribed to `messages` field
- Check if the phone number is in the test recipient list (for test numbers)
- Ensure your server is publicly accessible
- Check server logs for incoming webhook requests
- Verify the webhook URL doesn't have firewall restrictions

### Issue 3: Error 401 Unauthorized

**Symptoms:** Can't send messages, getting 401 errors

**Solutions:**
- Verify your access token is correct and not expired
- Ensure you're using a permanent token, not the temporary one
- Check if the token has the required permissions
- Verify the phone number ID is correct

### Issue 4: Error 400 Bad Request

**Symptoms:** Getting 400 errors when sending messages

**Solutions:**
- Ensure phone numbers are in E.164 format (+country code + number)
- Verify message format is correct
- Check if you're within rate limits
- For test numbers, ensure recipient is in the test recipient list

### Issue 5: Phone Number Already Registered

**Symptoms:** Can't add phone number - says it's already registered

**Solutions:**
- The number may be registered with regular WhatsApp
- You need to use a different number or delete the WhatsApp account
- Consider using Meta's test number for development

## Rate Limits and Quotas

### Message Rate Limits

- **Business Tier**: Depends on your phone number's quality rating
- **New Numbers**: Start with limited messaging tier
- **Tier Upgrades**: Automatic based on message volume and quality

### Quality Rating

Maintain high quality to avoid restrictions:
- Respond to customer messages promptly
- Don't spam users
- Provide opt-out options
- Keep message content relevant

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate access tokens** periodically
4. **Implement rate limiting** in your application
5. **Validate webhook signatures** (optional but recommended)
6. **Use HTTPS** for all webhook communications
7. **Monitor API usage** and set up alerts
8. **Keep access tokens secure** - never expose in client-side code

## Additional Resources

- [Meta WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [WhatsApp Business Platform Getting Started](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started)
- [Meta Business Manager](https://business.facebook.com/)
- [WhatsApp API Changelog](https://developers.facebook.com/docs/whatsapp/changelog)

## Support

If you encounter issues:
1. Check the [Meta Developer Community](https://developers.facebook.com/community/)
2. Review [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp/)
3. Contact Meta Support through the Business Manager
4. Check the application logs in `backend/server.py` for detailed error messages

## Next Steps

After successful WhatsApp configuration:
1. Configure Sarvam AI API for Hinglish support
2. Set up MongoDB database
3. Test the complete message flow
4. Configure scheduled alerts
5. Set up the React dashboard

For detailed product features, see [PRD.md](memory/PRD.md)
