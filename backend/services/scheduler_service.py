import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

class ProactiveAlertScheduler:
    """Cron scheduler for proactive business alerts"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.db = None
        self.whatsapp_service = None
        self.owner_phone = None
        self._started = False
    
    def configure(self, db, whatsapp_service, owner_phone: str):
        """Configure scheduler with dependencies"""
        self.db = db
        self.whatsapp_service = whatsapp_service
        self.owner_phone = owner_phone
    
    def start(self):
        """Start the scheduler with all jobs"""
        if self._started:
            return
        
        # Daily morning summary at 8 AM IST (2:30 AM UTC)
        self.scheduler.add_job(
            self.send_daily_summary,
            CronTrigger(hour=2, minute=30),
            id='daily_summary',
            name='Daily Business Summary'
        )
        
        # Low stock alerts at 9 AM IST (3:30 AM UTC)
        self.scheduler.add_job(
            self.send_low_stock_alerts,
            CronTrigger(hour=3, minute=30),
            id='low_stock_alerts',
            name='Low Stock Alerts'
        )
        
        # Overdue payment reminders at 10 AM IST (4:30 AM UTC)
        self.scheduler.add_job(
            self.send_overdue_reminders,
            CronTrigger(hour=4, minute=30),
            id='overdue_reminders',
            name='Overdue Payment Reminders'
        )
        
        # Weekly credit summary on Monday 9 AM IST
        self.scheduler.add_job(
            self.send_weekly_credit_summary,
            CronTrigger(day_of_week='mon', hour=3, minute=30),
            id='weekly_credit_summary',
            name='Weekly Credit Summary'
        )
        
        self.scheduler.start()
        self._started = True
        logger.info("Proactive alert scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self._started:
            self.scheduler.shutdown()
            self._started = False
            logger.info("Proactive alert scheduler stopped")
    
    async def send_daily_summary(self):
        """Send daily business summary to owner"""
        if not self.db or not self.whatsapp_service or not self.owner_phone:
            logger.warning("Scheduler not properly configured")
            return
        
        try:
            # Get yesterday's date range
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday = today - timedelta(days=1)
            
            # Get yesterday's stats
            pipeline = [
                {"$match": {"created_at": {"$gte": yesterday.isoformat(), "$lt": today.isoformat()}}},
                {"$group": {
                    "_id": None,
                    "total_sales": {"$sum": "$grand_total"},
                    "invoice_count": {"$sum": 1},
                    "total_credit": {"$sum": "$balance_due"}
                }}
            ]
            
            result = await self.db.invoices.aggregate(pipeline).to_list(1)
            stats = result[0] if result else {"total_sales": 0, "invoice_count": 0, "total_credit": 0}
            
            # Get total pending udhaar
            udhaar_pipeline = [
                {"$group": {"_id": None, "total": {"$sum": "$total_credit"}}}
            ]
            udhaar_result = await self.db.customers.aggregate(udhaar_pipeline).to_list(1)
            total_udhaar = udhaar_result[0]["total"] if udhaar_result else 0
            
            # Get low stock count
            low_stock = await self.db.inventory.count_documents({
                "$expr": {"$lte": ["$quantity", "$reorder_level"]}
            })
            
            message = f"""
🌅 *Good Morning! Daily Summary*
{'=' * 30}

📅 *Yesterday's Performance:*
💰 Sales: ₹{stats.get('total_sales', 0):,.0f}
📄 Invoices: {stats.get('invoice_count', 0)}
💳 Credit Given: ₹{stats.get('total_credit', 0):,.0f}

📊 *Current Status:*
💸 Total Udhaar: ₹{total_udhaar:,.0f}
⚠️ Low Stock Items: {low_stock}

_Have a great day! 🙏_
"""
            
            await self.whatsapp_service.send_text_message(self.owner_phone, message.strip())
            logger.info("Daily summary sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send daily summary: {str(e)}")
    
    async def send_low_stock_alerts(self):
        """Send low stock alerts"""
        if not self.db or not self.whatsapp_service or not self.owner_phone:
            return
        
        try:
            # Find items below reorder level
            low_stock_items = await self.db.inventory.find({
                "$expr": {"$lte": ["$quantity", "$reorder_level"]}
            }, {"_id": 0}).to_list(20)
            
            if not low_stock_items:
                return  # No alerts needed
            
            message = "⚠️ *LOW STOCK ALERT*\n" + "=" * 30 + "\n\n"
            
            for item in low_stock_items:
                status = "🔴" if item['quantity'] <= item['reorder_level'] * 0.5 else "🟡"
                message += f"{status} *{item['name']}*\n"
                message += f"   Stock: {item['quantity']:.0f} {item['unit']}\n"
                message += f"   Reorder at: {item['reorder_level']} {item['unit']}\n\n"
            
            message += "\n_Reply 'reorder [item]' to place order_"
            
            await self.whatsapp_service.send_text_message(self.owner_phone, message.strip())
            logger.info(f"Low stock alert sent for {len(low_stock_items)} items")
            
        except Exception as e:
            logger.error(f"Failed to send low stock alerts: {str(e)}")
    
    async def send_overdue_reminders(self):
        """Send overdue payment reminders"""
        if not self.db or not self.whatsapp_service or not self.owner_phone:
            return
        
        try:
            overdue_date = datetime.now(timezone.utc) - timedelta(days=30)
            
            # Get overdue customers
            pipeline = [
                {
                    "$match": {
                        "payment_status": {"$in": ["pending", "partial"]},
                        "created_at": {"$lt": overdue_date.isoformat()}
                    }
                },
                {
                    "$group": {
                        "_id": "$customer_id",
                        "customer_name": {"$first": "$customer_name"},
                        "total_overdue": {"$sum": "$balance_due"},
                        "oldest_date": {"$min": "$created_at"}
                    }
                },
                {"$sort": {"total_overdue": -1}},
                {"$limit": 5}
            ]
            
            overdue_list = await self.db.invoices.aggregate(pipeline).to_list(5)
            
            if not overdue_list:
                return
            
            message = "🔔 *OVERDUE PAYMENT REMINDER*\n" + "=" * 30 + "\n\n"
            
            total_overdue = 0
            for customer in overdue_list:
                days_old = (datetime.now(timezone.utc) - datetime.fromisoformat(customer['oldest_date'].replace('Z', '+00:00'))).days
                message += f"👤 *{customer['customer_name']}*\n"
                message += f"   Amount: ₹{customer['total_overdue']:,.0f}\n"
                message += f"   Overdue: {days_old} days\n\n"
                total_overdue += customer['total_overdue']
            
            message += f"{'=' * 30}\n"
            message += f"💰 *Total Overdue: ₹{total_overdue:,.0f}*\n\n"
            message += "_Reply 'reminder [name]' to send collection message_"
            
            await self.whatsapp_service.send_text_message(self.owner_phone, message.strip())
            logger.info(f"Overdue reminder sent for {len(overdue_list)} customers")
            
        except Exception as e:
            logger.error(f"Failed to send overdue reminders: {str(e)}")
    
    async def send_weekly_credit_summary(self):
        """Send weekly credit summary on Mondays"""
        if not self.db or not self.whatsapp_service or not self.owner_phone:
            return
        
        try:
            # Get all customers with credit
            customers_with_credit = await self.db.customers.find(
                {"total_credit": {"$gt": 0}},
                {"_id": 0}
            ).sort("total_credit", -1).to_list(100)
            
            if not customers_with_credit:
                message = "🎉 *Weekly Credit Report*\n\n✅ No pending credit! All customers have paid up."
            else:
                total_credit = sum(c['total_credit'] for c in customers_with_credit)
                
                message = "📊 *WEEKLY CREDIT REPORT*\n" + "=" * 30 + "\n\n"
                message += f"💰 *Total Outstanding: ₹{total_credit:,.0f}*\n"
                message += f"👥 Customers: {len(customers_with_credit)}\n\n"
                
                message += "*Top 5 Pending:*\n"
                for idx, customer in enumerate(customers_with_credit[:5], 1):
                    message += f"{idx}. {customer['name']}: ₹{customer['total_credit']:,.0f}\n"
                
                message += f"\n{'=' * 30}\n"
                message += "_Focus on collection this week! 💪_"
            
            await self.whatsapp_service.send_text_message(self.owner_phone, message.strip())
            logger.info("Weekly credit summary sent")
            
        except Exception as e:
            logger.error(f"Failed to send weekly credit summary: {str(e)}")
    
    async def trigger_manual_alert(self, alert_type: str) -> str:
        """Manually trigger an alert (for testing)"""
        if alert_type == "daily":
            await self.send_daily_summary()
            return "Daily summary sent"
        elif alert_type == "low_stock":
            await self.send_low_stock_alerts()
            return "Low stock alerts sent"
        elif alert_type == "overdue":
            await self.send_overdue_reminders()
            return "Overdue reminders sent"
        elif alert_type == "weekly":
            await self.send_weekly_credit_summary()
            return "Weekly summary sent"
        else:
            return f"Unknown alert type: {alert_type}"

alert_scheduler = ProactiveAlertScheduler()
