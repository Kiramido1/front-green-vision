#!/usr/bin/env python
"""
Quick setup script for Green Vision Django Backend
"""
import os
import sys
import subprocess


def run_command(command, description):
    """Run a shell command and print status"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(e.stderr)
        return False


def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         GREEN VISION - DJANGO BACKEND SETUP              ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  WARNING: Virtual environment is not activated!")
        print("Please activate your virtual environment first:")
        print("  Windows: venv\\Scripts\\activate")
        print("  Linux/Mac: source venv/bin/activate")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("\n❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Make migrations
    if not run_command("python manage.py makemigrations", "Creating migrations"):
        print("\n⚠️  Warning: Migration creation had issues")
    
    # Run migrations
    if not run_command("python manage.py migrate", "Running migrations"):
        print("\n❌ Setup failed at database migration")
        sys.exit(1)
    
    # Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        print("\n⚠️  Warning: Static file collection had issues")
    
    print(f"\n{'='*60}")
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}")
    print("\n📝 Next Steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Run the server: python manage.py runserver")
    print("3. Visit: http://127.0.0.1:8000/")
    print("4. Admin panel: http://127.0.0.1:8000/admin/")
    print("\n✨ Happy coding!")


if __name__ == "__main__":
    main()
