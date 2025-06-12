"""
Email service for 2ª Vara Cível de Cariacica
Handles automated daily reports and notifications
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import func
from models import Contact, ChatMessage, ProcessConsultation, HearingSchedule, NewsItem, db


class EmailService:
    """Service for handling email notifications and reports"""
    
    def __init__(self):
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.email_user = os.environ.get('EMAIL_USER')
        self.email_password = os.environ.get('EMAIL_PASSWORD')
        self.from_email = os.environ.get('FROM_EMAIL', 'noreply@varacivel.cariacica.tjes.jus.br')
        # Multiple admin emails for daily reports
        self.admin_emails = [
            'fbmoulin@tjes.jus.br',
            'alraimundo@tjes.jus.br', 
            'rtnobrega@tjes.jus.br'
        ]
        self.admin_email = self.admin_emails[0]  # Primary email for compatibility
        
    def send_email(self, to_email: str, subject: str, body: str, 
                   attachments: Optional[List[str]] = None, is_html: bool = True) -> bool:
        """Send email with optional attachments"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'html' if is_html else 'plain', 'utf-8'))
            
            # Add attachments if any
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            if self.email_user and self.email_password:
                server.login(self.email_user, self.email_password)
            
            server.send_message(msg)
            server.quit()
            
            logging.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def generate_daily_report(self, date: datetime = None) -> Dict:
        """Generate comprehensive daily activity report"""
        if not date:
            date = datetime.now().date()
        
        # Get previous day's data
        start_date = datetime.combine(date, datetime.min.time())
        end_date = start_date + timedelta(days=1)
        
        try:
            # Contact form submissions
            contacts = Contact.query.filter(
                Contact.created_at >= start_date,
                Contact.created_at < end_date
            ).all()
            
            # Chatbot interactions
            chat_messages = ChatMessage.query.filter(
                ChatMessage.created_at >= start_date,
                ChatMessage.created_at < end_date
            ).all()
            
            # Process consultations
            consultations = ProcessConsultation.query.filter(
                ProcessConsultation.consulted_at >= start_date,
                ProcessConsultation.consulted_at < end_date
            ).all()
            
            # Hearing schedules
            hearings = HearingSchedule.query.filter(
                HearingSchedule.created_at >= start_date,
                HearingSchedule.created_at < end_date
            ).all()
            
            # Website statistics
            stats = self.get_website_statistics(start_date, end_date)
            
            report_data = {
                'date': date.strftime('%d/%m/%Y'),
                'contacts': {
                    'total': len(contacts),
                    'details': [
                        {
                            'name': c.name,
                            'email': c.email,
                            'subject': c.subject,
                            'time': c.created_at.strftime('%H:%M')
                        } for c in contacts
                    ]
                },
                'chatbot': {
                    'total_interactions': len(chat_messages),
                    'unique_sessions': len(set(msg.session_id for msg in chat_messages if msg.session_id)),
                    'common_topics': self.analyze_chat_topics(chat_messages)
                },
                'consultations': {
                    'total': len(consultations),
                    'processes': [c.process_number for c in consultations]
                },
                'hearings': {
                    'total_scheduled': len(hearings),
                    'by_type': self.group_hearings_by_type(hearings),
                    'by_mode': self.group_hearings_by_mode(hearings)
                },
                'statistics': stats
            }
            
            return report_data
            
        except Exception as e:
            logging.error(f"Error generating daily report: {e}")
            return {}
    
    def get_website_statistics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get website usage statistics"""
        try:
            total_contacts = Contact.query.filter(
                Contact.created_at >= start_date,
                Contact.created_at < end_date
            ).count()
            
            total_consultations = ProcessConsultation.query.filter(
                ProcessConsultation.consulted_at >= start_date,
                ProcessConsultation.consulted_at < end_date
            ).count()
            
            total_hearings = HearingSchedule.query.filter(
                HearingSchedule.created_at >= start_date,
                HearingSchedule.created_at < end_date
            ).count()
            
            total_chat_interactions = ChatMessage.query.filter(
                ChatMessage.created_at >= start_date,
                ChatMessage.created_at < end_date
            ).count()
            
            return {
                'total_interactions': total_contacts + total_consultations + total_hearings + total_chat_interactions,
                'contact_forms': total_contacts,
                'process_consultations': total_consultations,
                'hearing_schedules': total_hearings,
                'chatbot_interactions': total_chat_interactions
            }
            
        except Exception as e:
            logging.error(f"Error getting website statistics: {e}")
            return {}
    
    def analyze_chat_topics(self, chat_messages: List[ChatMessage]) -> List[Dict]:
        """Analyze common topics in chat messages"""
        topics = {}
        
        for msg in chat_messages:
            # Simple keyword analysis
            message_lower = msg.user_message.lower()
            
            if any(word in message_lower for word in ['processo', 'andamento', 'consulta']):
                topics['Consultas de Processo'] = topics.get('Consultas de Processo', 0) + 1
            elif any(word in message_lower for word in ['audiência', 'agendamento', 'horário']):
                topics['Agendamento de Audiências'] = topics.get('Agendamento de Audiências', 0) + 1
            elif any(word in message_lower for word in ['contato', 'telefone', 'endereço']):
                topics['Informações de Contato'] = topics.get('Informações de Contato', 0) + 1
            elif any(word in message_lower for word in ['documento', 'certidão', 'comprovante']):
                topics['Documentos e Certidões'] = topics.get('Documentos e Certidões', 0) + 1
            else:
                topics['Outros'] = topics.get('Outros', 0) + 1
        
        return [{'topic': k, 'count': v} for k, v in sorted(topics.items(), key=lambda x: x[1], reverse=True)]
    
    def group_hearings_by_type(self, hearings: List[HearingSchedule]) -> Dict:
        """Group hearings by type"""
        types = {}
        for hearing in hearings:
            types[hearing.hearing_type] = types.get(hearing.hearing_type, 0) + 1
        return types
    
    def group_hearings_by_mode(self, hearings: List[HearingSchedule]) -> Dict:
        """Group hearings by mode"""
        modes = {}
        for hearing in hearings:
            modes[hearing.hearing_mode] = modes.get(hearing.hearing_mode, 0) + 1
        return modes
    
    def format_daily_report_html(self, report_data: Dict) -> str:
        """Format daily report as HTML email"""
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório Diário - 2ª Vara Cível de Cariacica</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .header {{
                    background: linear-gradient(135deg, #1e40af, #3b82f6);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .section {{
                    background: white;
                    padding: 25px;
                    margin-bottom: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .section h3 {{
                    color: #1e40af;
                    border-bottom: 2px solid #e5e7eb;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                .stat-card {{
                    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    border-left: 4px solid #3b82f6;
                }}
                .stat-number {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #1e40af;
                }}
                .stat-label {{
                    color: #64748b;
                    font-size: 0.9em;
                    margin-top: 5px;
                }}
                .contact-item {{
                    background: #f8fafc;
                    padding: 15px;
                    margin-bottom: 10px;
                    border-radius: 5px;
                    border-left: 3px solid #10b981;
                }}
                .topic-item {{
                    display: flex;
                    justify-content: space-between;
                    padding: 10px;
                    background: #f1f5f9;
                    margin-bottom: 5px;
                    border-radius: 4px;
                }}
                .footer {{
                    text-align: center;
                    color: #64748b;
                    font-size: 0.9em;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                }}
                .no-data {{
                    text-align: center;
                    color: #6b7280;
                    font-style: italic;
                    padding: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Relatório Diário</h1>
                <h2>2ª Vara Cível de Cariacica</h2>
                <p>Data: {report_data.get('date', 'N/A')}</p>
            </div>
            
            <div class="section">
                <h3>📈 Resumo de Atividades</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{report_data.get('statistics', {}).get('total_interactions', 0)}</div>
                        <div class="stat-label">Total de Interações</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{report_data.get('contacts', {}).get('total', 0)}</div>
                        <div class="stat-label">Formulários de Contato</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{report_data.get('consultations', {}).get('total', 0)}</div>
                        <div class="stat-label">Consultas de Processo</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{report_data.get('hearings', {}).get('total_scheduled', 0)}</div>
                        <div class="stat-label">Audiências Agendadas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{report_data.get('chatbot', {}).get('total_interactions', 0)}</div>
                        <div class="stat-label">Interações Chatbot</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{report_data.get('chatbot', {}).get('unique_sessions', 0)}</div>
                        <div class="stat-label">Sessões Únicas</div>
                    </div>
                </div>
            </div>
        """
        
        # Contact forms section
        if report_data.get('contacts', {}).get('total', 0) > 0:
            html += """
            <div class="section">
                <h3>📝 Formulários de Contato</h3>
            """
            for contact in report_data['contacts']['details']:
                html += f"""
                <div class="contact-item">
                    <strong>{contact['name']}</strong> ({contact['time']})<br>
                    <strong>Email:</strong> {contact['email']}<br>
                    <strong>Assunto:</strong> {contact['subject']}
                </div>
                """
            html += "</div>"
        
        # Chatbot topics section
        if report_data.get('chatbot', {}).get('common_topics'):
            html += """
            <div class="section">
                <h3>🤖 Tópicos Mais Consultados no Chatbot</h3>
            """
            for topic in report_data['chatbot']['common_topics']:
                html += f"""
                <div class="topic-item">
                    <span>{topic['topic']}</span>
                    <span><strong>{topic['count']}</strong></span>
                </div>
                """
            html += "</div>"
        
        # Process consultations section
        if report_data.get('consultations', {}).get('total', 0) > 0:
            html += """
            <div class="section">
                <h3>🔍 Consultas de Processo</h3>
                <p><strong>Processos consultados:</strong></p>
                <ul>
            """
            for process in report_data['consultations']['processes']:
                html += f"<li>{process}</li>"
            html += "</ul></div>"
        
        # Hearings section
        if report_data.get('hearings', {}).get('total_scheduled', 0) > 0:
            html += """
            <div class="section">
                <h3>📅 Audiências Agendadas</h3>
            """
            
            if report_data['hearings'].get('by_type'):
                html += "<p><strong>Por tipo:</strong></p><ul>"
                for hearing_type, count in report_data['hearings']['by_type'].items():
                    html += f"<li>{hearing_type}: {count}</li>"
                html += "</ul>"
            
            if report_data['hearings'].get('by_mode'):
                html += "<p><strong>Por modalidade:</strong></p><ul>"
                for mode, count in report_data['hearings']['by_mode'].items():
                    html += f"<li>{mode}: {count}</li>"
                html += "</ul>"
            
            html += "</div>"
        
        # No activity message
        if report_data.get('statistics', {}).get('total_interactions', 0) == 0:
            html += """
            <div class="section">
                <div class="no-data">
                    Nenhuma atividade registrada no período.
                </div>
            </div>
            """
        
        # Add recipients information
        recipients_list = ', '.join(self.admin_emails)
        
        html += f"""
            <div class="footer">
                <p>Este relatório é gerado automaticamente pelo sistema da 2ª Vara Cível de Cariacica.</p>
                <p><strong>Horários de envio:</strong> 12:00 e 17:00 (Segunda a Sexta-feira)</p>
                <p><strong>Destinatários:</strong> {recipients_list}</p>
                <p>Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_daily_report(self, date: datetime = None) -> bool:
        """Send daily report to all admin emails"""
        try:
            if not date:
                date = datetime.now().date() - timedelta(days=1)  # Previous day
            
            report_data = self.generate_daily_report(date)
            
            if not report_data:
                logging.error("Failed to generate daily report data")
                return False
            
            # Determine report time period for subject
            current_time = datetime.now().time()
            if current_time.hour < 14:  # Morning report (12:00)
                period = "Manhã"
            else:  # Afternoon report (17:00)
                period = "Tarde"
            
            subject = f"Relatório Diário ({period}) - 2ª Vara Cível de Cariacica - {report_data['date']}"
            html_body = self.format_daily_report_html(report_data)
            
            # Send to all admin emails
            all_success = True
            for admin_email in self.admin_emails:
                success = self.send_email(
                    to_email=admin_email,
                    subject=subject,
                    body=html_body,
                    is_html=True
                )
                
                if success:
                    logging.info(f"Daily report sent successfully to {admin_email}")
                else:
                    logging.error(f"Failed to send daily report to {admin_email}")
                    all_success = False
            
            return all_success
            
        except Exception as e:
            logging.error(f"Error sending daily report: {e}")
            return False
    
    def send_hearing_confirmation(self, hearing: HearingSchedule) -> bool:
        """Send hearing confirmation email"""
        try:
            subject = f"Confirmação de Agendamento - Processo {hearing.process_number}"
            
            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #1e40af; color: white; padding: 20px; text-align: center;">
                    <h2>Agendamento Confirmado</h2>
                    <p>2ª Vara Cível de Cariacica</p>
                </div>
                
                <div style="padding: 20px;">
                    <h3>Detalhes da Audiência</h3>
                    <p><strong>Processo:</strong> {hearing.process_number}</p>
                    <p><strong>Data:</strong> {hearing.scheduled_date.strftime('%d/%m/%Y')}</p>
                    <p><strong>Horário:</strong> {hearing.scheduled_date.strftime('%H:%M')}</p>
                    <p><strong>Tipo:</strong> {hearing.hearing_type}</p>
                    <p><strong>Modalidade:</strong> {hearing.hearing_mode}</p>
                    <p><strong>Advogado:</strong> {hearing.lawyer_name}</p>
                    <p><strong>Cliente:</strong> {hearing.client_name}</p>
                    
                    {f'<div style="background: #e0f2fe; padding: 15px; margin: 20px 0; border-radius: 5px;"><h4>Informações da Reunião Virtual</h4><p><strong>Link:</strong> {hearing.meeting_link}</p><p><strong>ID:</strong> {hearing.meeting_id}</p><p><strong>Senha:</strong> {hearing.meeting_password}</p></div>' if hearing.hearing_mode in ['virtual', 'hybrid'] and hearing.meeting_link else ''}
                    
                    <div style="background: #f8fafc; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <h4>Instruções Importantes</h4>
                        <ul>
                            <li>Chegue com 15 minutos de antecedência</li>
                            <li>Leve todos os documentos relacionados ao processo</li>
                            <li>Para reagendamentos, entre em contato com antecedência mínima de 24 horas</li>
                        </ul>
                    </div>
                </div>
                
                <div style="background: #f1f5f9; padding: 15px; text-align: center; color: #64748b;">
                    <p>Este é um e-mail automático. Não responda a este e-mail.</p>
                    <p>2ª Vara Cível de Cariacica - (27) 3246-8200</p>
                </div>
            </div>
            """
            
            return self.send_email(
                to_email=hearing.lawyer_email,
                subject=subject,
                body=html_body,
                is_html=True
            )
            
        except Exception as e:
            logging.error(f"Error sending hearing confirmation: {e}")
            return False


# Initialize email service
email_service = EmailService()