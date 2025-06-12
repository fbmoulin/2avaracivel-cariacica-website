"""
Scheduler service for automated tasks
Handles daily email reports and other scheduled operations
"""

import os
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List
import schedule
from services.email_service import email_service


class SchedulerService:
    """Service for managing scheduled tasks"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.jobs = []
        
    def start(self):
        """Start the scheduler service"""
        if self.running:
            return
        
        self.running = True
        self.setup_jobs()
        
        # Start scheduler in a separate thread
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        logging.info("Scheduler service started successfully")
    
    def stop(self):
        """Stop the scheduler service"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logging.info("Scheduler service stopped")
    
    def setup_jobs(self):
        """Setup all scheduled jobs"""
        # Daily reports - Monday to Friday at 12:00 and 17:00
        schedule.every().monday.at("12:00").do(self.send_daily_report)
        schedule.every().tuesday.at("12:00").do(self.send_daily_report)
        schedule.every().wednesday.at("12:00").do(self.send_daily_report)
        schedule.every().thursday.at("12:00").do(self.send_daily_report)
        schedule.every().friday.at("12:00").do(self.send_daily_report)
        
        schedule.every().monday.at("17:00").do(self.send_daily_report)
        schedule.every().tuesday.at("17:00").do(self.send_daily_report)
        schedule.every().wednesday.at("17:00").do(self.send_daily_report)
        schedule.every().thursday.at("17:00").do(self.send_daily_report)
        schedule.every().friday.at("17:00").do(self.send_daily_report)
        
        # Weekly summary on Fridays at 18:00
        schedule.every().friday.at("18:00").do(self.send_weekly_summary)
        
        # Monthly report on the 1st of each month at 09:00
        schedule.every().day.at("09:00").do(self.check_monthly_report)
        
        # Cleanup old data every Sunday at 02:00
        schedule.every().sunday.at("02:00").do(self.cleanup_old_data)
        
        logging.info("Scheduled jobs configured: Daily reports at 12:00 and 17:00 (Mon-Fri)")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logging.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
    
    def send_daily_report(self):
        """Send daily report via email"""
        try:
            logging.info("Starting daily report generation...")
            
            # Send report for previous day
            yesterday = datetime.now().date() - timedelta(days=1)
            success = email_service.send_daily_report(yesterday)
            
            if success:
                logging.info(f"Daily report sent successfully for {yesterday}")
            else:
                logging.error(f"Failed to send daily report for {yesterday}")
                
        except Exception as e:
            logging.error(f"Error sending daily report: {e}")
    
    def send_weekly_summary(self):
        """Send weekly summary report"""
        try:
            logging.info("Generating weekly summary...")
            
            # Get data for the past week
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            
            weekly_data = self.generate_weekly_summary(start_date, end_date)
            
            if weekly_data:
                html_body = self.format_weekly_summary_html(weekly_data)
                subject = f"Relatório Semanal - 2ª Vara Cível de Cariacica - {start_date.strftime('%d/%m')} a {end_date.strftime('%d/%m/%Y')}"
                
                # Send to all admin emails
                all_success = True
                for admin_email in email_service.admin_emails:
                    success = email_service.send_email(
                        to_email=admin_email,
                        subject=subject,
                        body=html_body,
                        is_html=True
                    )
                    if success:
                        logging.info(f"Weekly summary sent successfully to {admin_email}")
                    else:
                        logging.error(f"Failed to send weekly summary to {admin_email}")
                        all_success = False
            
        except Exception as e:
            logging.error(f"Error sending weekly summary: {e}")
    
    def check_monthly_report(self):
        """Check if monthly report should be sent (1st of month)"""
        if datetime.now().day == 1:
            self.send_monthly_report()
    
    def send_monthly_report(self):
        """Send monthly report"""
        try:
            logging.info("Generating monthly report...")
            
            # Get data for previous month
            today = datetime.now().date()
            first_day_current_month = today.replace(day=1)
            last_day_previous_month = first_day_current_month - timedelta(days=1)
            first_day_previous_month = last_day_previous_month.replace(day=1)
            
            monthly_data = self.generate_monthly_summary(first_day_previous_month, last_day_previous_month)
            
            if monthly_data:
                html_body = self.format_monthly_summary_html(monthly_data)
                subject = f"Relatório Mensal - 2ª Vara Cível de Cariacica - {first_day_previous_month.strftime('%m/%Y')}"
                
                success = email_service.send_email(
                    to_email=email_service.admin_email,
                    subject=subject,
                    body=html_body,
                    is_html=True
                )
                
                if success:
                    logging.info("Monthly report sent successfully")
                else:
                    logging.error("Failed to send monthly report")
            
        except Exception as e:
            logging.error(f"Error sending monthly report: {e}")
    
    def cleanup_old_data(self):
        """Clean up old data from the database"""
        try:
            from models import ChatMessage, ProcessConsultation, db
            
            # Delete chat messages older than 90 days
            cutoff_date = datetime.now() - timedelta(days=90)
            
            old_messages = ChatMessage.query.filter(ChatMessage.created_at < cutoff_date).all()
            for message in old_messages:
                db.session.delete(message)
            
            # Delete process consultations older than 180 days
            cutoff_date = datetime.now() - timedelta(days=180)
            old_consultations = ProcessConsultation.query.filter(ProcessConsultation.consulted_at < cutoff_date).all()
            for consultation in old_consultations:
                db.session.delete(consultation)
            
            db.session.commit()
            
            logging.info(f"Cleaned up {len(old_messages)} old chat messages and {len(old_consultations)} old consultations")
            
        except Exception as e:
            logging.error(f"Error cleaning up old data: {e}")
    
    def generate_weekly_summary(self, start_date, end_date) -> Dict:
        """Generate weekly summary data"""
        try:
            from models import Contact, ChatMessage, ProcessConsultation, HearingSchedule
            
            # Aggregate data for the week
            weekly_stats = {}
            current_date = start_date
            
            while current_date <= end_date:
                daily_data = email_service.generate_daily_report(current_date)
                day_name = current_date.strftime('%A')
                weekly_stats[day_name] = daily_data.get('statistics', {})
                current_date += timedelta(days=1)
            
            # Calculate totals
            total_interactions = sum(day.get('total_interactions', 0) for day in weekly_stats.values())
            total_contacts = sum(day.get('contact_forms', 0) for day in weekly_stats.values())
            total_consultations = sum(day.get('process_consultations', 0) for day in weekly_stats.values())
            total_hearings = sum(day.get('hearing_schedules', 0) for day in weekly_stats.values())
            total_chat = sum(day.get('chatbot_interactions', 0) for day in weekly_stats.values())
            
            return {
                'period': f"{start_date.strftime('%d/%m')} a {end_date.strftime('%d/%m/%Y')}",
                'daily_stats': weekly_stats,
                'totals': {
                    'interactions': total_interactions,
                    'contacts': total_contacts,
                    'consultations': total_consultations,
                    'hearings': total_hearings,
                    'chatbot': total_chat
                }
            }
            
        except Exception as e:
            logging.error(f"Error generating weekly summary: {e}")
            return {}
    
    def generate_monthly_summary(self, start_date, end_date) -> Dict:
        """Generate monthly summary data"""
        try:
            from models import Contact, ChatMessage, ProcessConsultation, HearingSchedule
            
            # Similar to weekly but for monthly period
            total_stats = email_service.get_website_statistics(
                datetime.combine(start_date, datetime.min.time()),
                datetime.combine(end_date, datetime.max.time())
            )
            
            # Get top consulting days, most active hours, etc.
            return {
                'period': f"{start_date.strftime('%m/%Y')}",
                'totals': total_stats,
                'month_name': start_date.strftime('%B %Y')
            }
            
        except Exception as e:
            logging.error(f"Error generating monthly summary: {e}")
            return {}
    
    def format_weekly_summary_html(self, data: Dict) -> str:
        """Format weekly summary as HTML"""
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Relatório Semanal - 2ª Vara Cível de Cariacica</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1e40af; color: white; padding: 20px; text-align: center; border-radius: 8px; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
                .stat-card {{ background: #f0f9ff; padding: 15px; border-radius: 8px; text-align: center; }}
                .stat-number {{ font-size: 1.5em; font-weight: bold; color: #1e40af; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Relatório Semanal</h1>
                <h2>2ª Vara Cível de Cariacica</h2>
                <p>Período: {data.get('period', 'N/A')}</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{data.get('totals', {}).get('interactions', 0)}</div>
                    <div>Total Interações</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{data.get('totals', {}).get('contacts', 0)}</div>
                    <div>Contatos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{data.get('totals', {}).get('consultations', 0)}</div>
                    <div>Consultas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{data.get('totals', {}).get('hearings', 0)}</div>
                    <div>Audiências</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{data.get('totals', {}).get('chatbot', 0)}</div>
                    <div>Chatbot</div>
                </div>
            </div>
            
            <p style="text-align: center; color: #64748b; margin-top: 30px;">
                Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}
            </p>
        </body>
        </html>
        """
        return html
    
    def format_monthly_summary_html(self, data: Dict) -> str:
        """Format monthly summary as HTML"""
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Relatório Mensal - 2ª Vara Cível de Cariacica</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1e40af; color: white; padding: 20px; text-align: center; border-radius: 8px; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
                .stat-card {{ background: #f0f9ff; padding: 15px; border-radius: 8px; text-align: center; }}
                .stat-number {{ font-size: 2em; font-weight: bold; color: #1e40af; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📈 Relatório Mensal</h1>
                <h2>2ª Vara Cível de Cariacica</h2>
                <p>{data.get('month_name', 'N/A')}</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{data.get('totals', {}).get('total_interactions', 0)}</div>
                    <div>Total Interações</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{data.get('totals', {}).get('contact_forms', 0)}</div>
                    <div>Formulários Contato</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{data.get('totals', {}).get('process_consultations', 0)}</div>
                    <div>Consultas Processo</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{data.get('totals', {}).get('hearing_schedules', 0)}</div>
                    <div>Audiências Agendadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{data.get('totals', {}).get('chatbot_interactions', 0)}</div>
                    <div>Interações Chatbot</div>
                </div>
            </div>
            
            <p style="text-align: center; color: #64748b; margin-top: 30px;">
                Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}
            </p>
        </body>
        </html>
        """
        return html
    
    def send_test_report(self):
        """Send a test report immediately for verification"""
        try:
            logging.info("Sending test report...")
            return email_service.send_daily_report()
        except Exception as e:
            logging.error(f"Error sending test report: {e}")
            return False


# Initialize scheduler service
scheduler_service = SchedulerService()