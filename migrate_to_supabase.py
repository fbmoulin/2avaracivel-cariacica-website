#!/usr/bin/env python3
"""
Supabase Migration Script for 2ª Vara Cível de Cariacica
Migrates existing data from current database to Supabase
"""
import os
import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Contact, ProcessConsultation, ChatMessage, AssessorMeeting
from database import db, configure_database
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SupabaseMigration:
    def __init__(self):
        self.app = None
        self.old_data = {}
        self.migration_stats = {
            'contacts': 0,
            'consultations': 0,
            'chat_messages': 0,
            'assessor_meetings': 0,
            'errors': 0
        }

    def test_supabase_connection(self):
        """Test connection to Supabase database"""
        logger.info("Testing Supabase database connection...")
        
        try:
            # Create app with new Supabase config
            self.app = create_app()
            
            with self.app.app_context():
                # Test basic connection
                result = db.session.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                logger.info(f"Connected to PostgreSQL: {version}")
                
                # Test if we can create tables
                db.create_all()
                logger.info("Database tables created successfully")
                
                return True
                
        except Exception as e:
            logger.error(f"Supabase connection failed: {e}")
            return False

    def backup_existing_data(self):
        """Backup existing data from current database (if any)"""
        logger.info("Backing up existing data...")
        
        try:
            # Only backup if there's existing data to preserve
            with self.app.app_context():
                # Count existing records
                contact_count = Contact.query.count()
                consultation_count = ProcessConsultation.query.count()
                chat_count = ChatMessage.query.count()
                meeting_count = AssessorMeeting.query.count()
                
                logger.info(f"Found existing data:")
                logger.info(f"  - Contacts: {contact_count}")
                logger.info(f"  - Process Consultations: {consultation_count}")
                logger.info(f"  - Chat Messages: {chat_count}")
                logger.info(f"  - Assessor Meetings: {meeting_count}")
                
                if contact_count + consultation_count + chat_count + meeting_count == 0:
                    logger.info("No existing data found - fresh start with Supabase")
                    return True
                
                # Backup data if exists
                self.old_data['contacts'] = [contact.to_dict() for contact in Contact.query.all()]
                self.old_data['consultations'] = [cons.to_dict() for cons in ProcessConsultation.query.all()]
                self.old_data['chat_messages'] = [msg.to_dict() for msg in ChatMessage.query.all()]
                self.old_data['meetings'] = [meeting.to_dict() for meeting in AssessorMeeting.query.all()]
                
                logger.info("Data backup completed successfully")
                return True
                
        except Exception as e:
            logger.warning(f"Could not backup existing data: {e}")
            logger.info("Proceeding with fresh migration to Supabase")
            return True

    def migrate_data_to_supabase(self):
        """Migrate backed up data to Supabase"""
        if not self.old_data:
            logger.info("No data to migrate - starting fresh with Supabase")
            return True
            
        logger.info("Migrating data to Supabase...")
        
        try:
            with self.app.app_context():
                # Clear existing data in Supabase (fresh start)
                db.session.execute(text("TRUNCATE TABLE contact CASCADE;"))
                db.session.execute(text("TRUNCATE TABLE process_consultation CASCADE;"))
                db.session.execute(text("TRUNCATE TABLE chat_message CASCADE;"))
                db.session.execute(text("TRUNCATE TABLE assessor_meeting CASCADE;"))
                db.session.commit()
                
                # Migrate contacts
                for contact_data in self.old_data.get('contacts', []):
                    contact = Contact(
                        name=contact_data['name'],
                        email=contact_data['email'],
                        phone=contact_data.get('phone'),
                        subject=contact_data['subject'],
                        message=contact_data['message']
                    )
                    db.session.add(contact)
                    self.migration_stats['contacts'] += 1
                
                # Migrate process consultations
                for cons_data in self.old_data.get('consultations', []):
                    consultation = ProcessConsultation(
                        process_number=cons_data['process_number'],
                        requester_name=cons_data['requester_name'],
                        requester_cpf=cons_data['requester_cpf']
                    )
                    db.session.add(consultation)
                    self.migration_stats['consultations'] += 1
                
                # Migrate chat messages
                for msg_data in self.old_data.get('chat_messages', []):
                    message = ChatMessage(
                        user_message=msg_data['user_message'],
                        bot_response=msg_data['bot_response'],
                        session_id=msg_data.get('session_id')
                    )
                    db.session.add(message)
                    self.migration_stats['chat_messages'] += 1
                
                # Migrate assessor meetings
                for meeting_data in self.old_data.get('meetings', []):
                    meeting = AssessorMeeting(
                        full_name=meeting_data['full_name'],
                        document=meeting_data['document'],
                        email=meeting_data['email'],
                        phone=meeting_data['phone'],
                        meeting_type=meeting_data['meeting_type'],
                        meeting_subject=meeting_data['meeting_subject'],
                        preferred_date=datetime.strptime(meeting_data['preferred_date'], '%Y-%m-%d').date(),
                        preferred_time=meeting_data['preferred_time'],
                        process_number=meeting_data.get('process_number'),
                        status=meeting_data.get('status', 'pending')
                    )
                    db.session.add(meeting)
                    self.migration_stats['assessor_meetings'] += 1
                
                # Commit all changes
                db.session.commit()
                logger.info("Data migration completed successfully")
                return True
                
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            db.session.rollback()
            self.migration_stats['errors'] += 1
            return False

    def verify_migration(self):
        """Verify that migration was successful"""
        logger.info("Verifying migration...")
        
        try:
            with self.app.app_context():
                contact_count = Contact.query.count()
                consultation_count = ProcessConsultation.query.count()
                chat_count = ChatMessage.query.count()
                meeting_count = AssessorMeeting.query.count()
                
                logger.info("Migration verification:")
                logger.info(f"  - Contacts migrated: {contact_count}")
                logger.info(f"  - Process consultations migrated: {consultation_count}")
                logger.info(f"  - Chat messages migrated: {chat_count}")
                logger.info(f"  - Assessor meetings migrated: {meeting_count}")
                
                # Test basic operations
                test_contact = Contact(
                    name="Migration Test",
                    email="test@migration.com",
                    subject="Test Subject",
                    message="Test migration message"
                )
                db.session.add(test_contact)
                db.session.commit()
                
                # Remove test record
                db.session.delete(test_contact)
                db.session.commit()
                
                logger.info("Database operations test: PASSED")
                return True
                
        except Exception as e:
            logger.error(f"Migration verification failed: {e}")
            return False

    def run_migration(self):
        """Run complete migration process"""
        logger.info("="*60)
        logger.info("Starting Supabase Migration")
        logger.info("="*60)
        
        try:
            # Step 1: Test Supabase connection
            if not self.test_supabase_connection():
                logger.error("Migration aborted - could not connect to Supabase")
                return False
            
            # Step 2: Backup existing data
            if not self.backup_existing_data():
                logger.error("Migration aborted - could not backup existing data")
                return False
            
            # Step 3: Migrate data to Supabase
            if not self.migrate_data_to_supabase():
                logger.error("Migration aborted - data migration failed")
                return False
            
            # Step 4: Verify migration
            if not self.verify_migration():
                logger.error("Migration completed but verification failed")
                return False
            
            # Success
            logger.info("="*60)
            logger.info("MIGRATION COMPLETED SUCCESSFULLY")
            logger.info("="*60)
            logger.info("Migration Statistics:")
            for key, value in self.migration_stats.items():
                logger.info(f"  - {key.replace('_', ' ').title()}: {value}")
            
            logger.info("\nYour application is now using Supabase database!")
            logger.info("You can safely delete any old database files if they exist.")
            
            return True
            
        except Exception as e:
            logger.error(f"Migration failed with error: {e}")
            return False

def main():
    """Main migration function"""
    print("🔄 Supabase Migration Tool")
    print("This will migrate your court application to use Supabase database")
    
    # Check if DATABASE_URL is configured
    if not os.environ.get('DATABASE_URL'):
        print("❌ DATABASE_URL environment variable not found")
        print("Please configure your Supabase DATABASE_URL first")
        sys.exit(1)
    
    database_url = os.environ.get('DATABASE_URL')
    if 'supabase' not in database_url.lower():
        response = input("⚠️  DATABASE_URL doesn't appear to be from Supabase. Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Migration cancelled")
            sys.exit(0)
    
    # Run migration
    migration = SupabaseMigration()
    success = migration.run_migration()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("Your application is now using Supabase database.")
    else:
        print("\n❌ Migration failed!")
        print("Check migration.log for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()