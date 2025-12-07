# Superset configuration
import os

SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "postgresql://content_admin:ContentMaker2024!Secure@postgres:5432/content_maker"
)

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}

# Security
SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY", "your-super-secret-key-change-in-production")

# CORS
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "resources": {"*": {"origins": "*"}},
}

