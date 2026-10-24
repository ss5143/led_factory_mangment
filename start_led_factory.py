
import os
import sys
import time
import threading
import webbrowser


# =========================================================
# DJANGO SETTINGS
# =========================================================

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "led_factory.settings"
)


# =========================================================
# DJANGO INITIALIZE
# =========================================================

import django

django.setup()

from django.conf import settings

print("====================================")
print("LED Factory Starting...")
print("DATABASE:", settings.DATABASES["default"]["NAME"])
print("STATIC ROOT:", settings.STATIC_ROOT)
print("MEDIA ROOT:", settings.MEDIA_ROOT)
print("====================================")


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_database():

    from django.core.management import call_command
    from django.contrib.auth import get_user_model

    print("Checking database...")

    # -----------------------------------------
    # Create/update database tables
    # Existing data is NOT deleted.
    # -----------------------------------------

    call_command(
        "migrate",
        interactive=False,
        verbosity=0,
    )

    # -----------------------------------------
    # Create writable folders
    # -----------------------------------------

    os.makedirs(
        settings.STATIC_ROOT,
        exist_ok=True
    )

    os.makedirs(
        settings.MEDIA_ROOT,
        exist_ok=True
    )

    # -----------------------------------------
    # Collect static files
    # Do NOT clear existing files.
    # -----------------------------------------

    call_command(
        "collectstatic",
        interactive=False,
        clear=False,
        verbosity=0,
    )

    # -----------------------------------------
    # Default admin
    # -----------------------------------------

    User = get_user_model()

    username = "admin"
    password = "Admin@1234"

    user, created = User.objects.get_or_create(
        username=username
    )

    if created:

        user.set_password(password)

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True

        user.save()

        print("====================================")
        print("Default admin created")
        print("Username: admin")
        print("Password: Admin@1234")
        print("====================================")

    else:

        print("Admin already exists.")

    print("Database ready.")


# =========================================================
# START DJANGO SERVER
# =========================================================

def start_server():

    from django.core.management import call_command

    call_command(
        "runserver",
        "127.0.0.1:8001",
        "--noreload",
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    try:

        initialize_database()

        server_thread = threading.Thread(
            target=start_server,
            daemon=True,
        )

        server_thread.start()

        # Give Django time to start
        time.sleep(3)

        # Open browser automatically
        webbrowser.open(
            "http://127.0.0.1:8001/"
        )

        # Keep EXE running
        while True:

            time.sleep(1)

    except Exception as e:

        print("====================================")
        print("LED Factory startup error:")
        print(e)
        print("====================================")

        input("Press Enter to close...")
