# CLAUDE.md - AI Assistant Guide for SSSIP

## Project Overview

**SSSIP (Self-Service Software Installation Portal)** is a Flask-based web application that allows users to self-install approved software on their devices via JumpCloud integration.

### Core Functionality
- OIDC authentication via JumpCloud SSO
- Retrieve user's registered devices from JumpCloud
- Display whitelisted software applications filtered by device OS
- Initiate software installations on selected devices via JumpCloud API

## Project Structure

```
jcsssipflasklightsail/
├── app.py              # Main Flask application with all routes and API logic
├── index.html          # Single-page frontend (HTML/CSS/JS)
├── Dockerfile          # Container configuration for AWS Lightsail
├── requirements.txt    # Python dependencies
├── README.md           # User documentation
├── logo.png/jpg        # Application logos
└── .env                # Environment variables (not in repo)
```

## Technology Stack

- **Backend**: Flask (Python 3.10)
- **Authentication**: Flask-OIDC with JumpCloud SSO
- **External API**: JumpCloud API v2
- **Frontend**: Vanilla JavaScript with inline CSS
- **Deployment**: Docker on AWS Lightsail (Gunicorn on port 5002)

## Key Files

### app.py (Main Application)
- **Lines 58-78**: `CustomOpenIDConnect` class - custom OIDC configuration loader
- **Lines 105-109**: `/` route - serves index.html for authenticated users
- **Lines 111-130**: `/api/apps` - returns whitelisted apps filtered by OS
- **Lines 139-152**: `/api/devices` - returns user's devices sorted by last contact
- **Lines 154-192**: `get_user_devices()` - fetches device details from JumpCloud
- **Lines 194-205**: `/api/install` - initiates software installation
- **Lines 207-244**: Authentication routes (`/login`, `/logout`, `/oidc-callback`)

### index.html (Frontend)
- Single-page application with device selector and app list
- Uses fetch API to communicate with backend endpoints
- Loading overlay and notification system for user feedback

## Environment Variables

The application requires these environment variables (typically in `.env` file):

```bash
# OIDC Configuration (JumpCloud SSO)
OIDC_CLIENT_ID=<client-id>
OIDC_CLIENT_SECRET=<client-secret>
OIDC_AUTH_URI=<auth-uri>
OIDC_TOKEN_URI=<token-uri>
OIDC_ISSUER=<issuer>
OIDC_USERINFO_URI=<userinfo-uri>
OIDC_REDIRECT_URIS=<comma-separated-uris>
OIDC_OPENID_REALM=<realm>
OIDC_COOKIE_SECURE=True  # Set to False for local development

# Application
SECRET_KEY=<flask-secret-key>

# JumpCloud API
JUMP_CLOUD_API_KEY=<api-key>
JUMPCLOUD_BASE_URL=https://console.jumpcloud.com/api/v2/

# App Whitelist
WHITELISTED_APPS_URL=<url-to-whitelist-json>
```

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (development mode)
python app.py

# Run with Flask CLI
FLASK_APP=app.py FLASK_ENV=development flask run

# Build Docker image
docker build -t sssip .

# Run Docker container
docker run -p 5002:5002 --env-file .env sssip
```

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | Yes | Serves main index.html |
| `/login` | GET | No | Initiates OIDC login flow |
| `/logout` | GET | No | Logs out user |
| `/oidc-callback` | GET/POST | No | OIDC callback handler |
| `/profile` | GET | Yes | Shows user profile info |
| `/api/user-info` | GET | Yes | Returns user info as JSON |
| `/api/devices` | GET | Yes | Returns user's devices |
| `/api/apps` | GET | Yes | Returns apps (optional `?os=` filter) |
| `/api/install` | POST | Yes | Initiates app installation |

## Code Conventions

### Python (app.py)
- Uses `python-dotenv` for environment variable loading
- Logging configured at DEBUG level
- OIDC routes decorated with `@oidc.require_login`
- API endpoints return JSON via `jsonify()`
- Error handling returns empty arrays/error status codes

### JavaScript (index.html)
- Async/await pattern for all API calls
- Functions prefixed descriptively: `load*`, `show*`, `close*`, `install*`
- DOM manipulation via vanilla JS (createElement, appendChild)
- Event handling via inline `onclick` and `addEventListener`

### Error Handling
- Backend: Logs errors and returns empty responses or status codes
- Frontend: try/catch blocks with console.error and user notifications

## Whitelisted Apps Configuration

The application fetches whitelisted apps from `WHITELISTED_APPS_URL`. Expected JSON format:

```json
{
  "whitelisted_apps": [
    {
      "id": "jumpcloud-app-id",
      "compatible_os": ["Mac OS X", "Windows"]
    }
  ]
}
```

## Deployment Notes

### AWS Lightsail
1. Build and push Docker image to registry
2. Create Lightsail container service
3. Configure environment variables in Lightsail console
4. Deploy container with port 5002 exposed

### Docker Configuration
- Base image: `python:3.10-slim`
- Runs via Gunicorn on port 5002
- Uses `ProxyFix` middleware for reverse proxy headers

## Common Tasks for AI Assistants

### Adding a new API endpoint
1. Add route in `app.py` with `@app.route()` decorator
2. Add `@oidc.require_login` if authentication required
3. Return JSON via `jsonify()`

### Modifying frontend
1. Edit `index.html` directly (single-file SPA)
2. JavaScript at bottom of file within `<script>` tags
3. CSS in `<style>` section in `<head>`

### Adding new environment variables
1. Add `os.getenv()` call in `app.py`
2. Document in `.env.example` (if exists) and this file
3. Update README.md setup instructions

## Security Considerations

- All API endpoints require OIDC authentication
- JumpCloud API key stored in environment variables
- `OIDC_COOKIE_SECURE` should be `True` in production
- Never commit `.env` files or secrets to repository
