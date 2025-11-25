SECRET_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

INSTALLED_APPS = ("django.contrib.auth", "django.contrib.contenttypes", "tests")

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTHENTICATION_BACKENDS = ["django_auth_ldap.backend.LDAPBackend"]

# Use python-ldap for tests since slapdtest requires it
AUTH_LDAP_BACKEND = "django_auth_ldap.adapters.python_ldap"
