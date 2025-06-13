#!/usr/bin/env python3
"""
Development setup automation script for 2ª Vara Cível de Cariacica
Configures development environment, installs pre-commit hooks, and validates setup
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description=""):
    """Run shell command and handle errors"""
    print(f"Running: {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {description}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {description}")
        print(f"Error: {e.stderr}")
        return None


def setup_pre_commit():
    """Install and configure pre-commit hooks"""
    print("\n🔧 Setting up pre-commit hooks...")
    
    # Install pre-commit hooks
    run_command("poetry run pre-commit install", "Installing pre-commit hooks")
    
    # Run pre-commit on all files to ensure setup works
    run_command("poetry run pre-commit run --all-files", "Running pre-commit on all files")


def validate_environment():
    """Validate development environment setup"""
    print("\n🔍 Validating environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 11:
        print(f"✅ Python {python_version.major}.{python_version.minor} detected")
    else:
        print(f"❌ Python 3.11+ required, found {python_version.major}.{python_version.minor}")
        return False
    
    # Check Poetry installation
    poetry_check = run_command("poetry --version", "Checking Poetry installation")
    if poetry_check:
        print("✅ Poetry is installed")
    else:
        print("❌ Poetry not found")
        return False
    
    # Check if virtual environment is activated
    venv_check = run_command("poetry env info", "Checking virtual environment")
    if venv_check:
        print("✅ Virtual environment configured")
    else:
        print("❌ Virtual environment not configured")
        return False
    
    return True


def install_dependencies():
    """Install project dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Install main dependencies
    run_command("poetry install", "Installing main dependencies")
    
    # Install development dependencies
    run_command("poetry install --with dev,test,monitoring", "Installing development dependencies")


def setup_database():
    """Setup development database"""
    print("\n🗄️ Setting up development database...")
    
    # Check if DATABASE_URL is set
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("⚠️  DATABASE_URL not set - using SQLite for development")
        os.environ['DATABASE_URL'] = 'sqlite:///dev_court.db'
    
    # Initialize database tables
    run_command("poetry run python -c 'from app import create_app; from database import db; app = create_app(); app.app_context().push(); db.create_all()'", 
                "Creating database tables")


def run_tests():
    """Run test suite to validate setup"""
    print("\n🧪 Running test suite...")
    
    # Run unit tests
    run_command("poetry run pytest tests/unit/ -v", "Running unit tests")
    
    # Run integration tests
    run_command("poetry run pytest tests/integration/ -v", "Running integration tests")


def main():
    """Main setup function"""
    print("🏛️ 2ª Vara Cível de Cariacica - Development Setup")
    print("=" * 50)
    
    # Validate environment
    if not validate_environment():
        print("\n❌ Environment validation failed")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Setup pre-commit hooks
    setup_pre_commit()
    
    # Setup database
    setup_database()
    
    # Run tests
    run_tests()
    
    print("\n🎉 Development environment setup complete!")
    print("\nNext steps:")
    print("1. Set your environment variables in .env file")
    print("2. Configure your OpenAI API key for chatbot functionality")
    print("3. Run 'poetry run court-dev' to start development server")
    print("4. Run 'poetry run pytest' to run the test suite")


if __name__ == "__main__":
    main()