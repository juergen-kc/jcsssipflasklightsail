# Run with: python app.py
from flask import Flask, jsonify, request, send_from_directory, redirect, url_for, session
from flask_oidc import OpenIDConnect
from datetime import datetime
import requests
import os
import json
import logging
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables from .env file
load_dotenv()

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

# Instantiate the Flask app
app = Flask(__name__, static_url_path='')

# Apply ProxyFix middleware to handle reverse proxy headers correctly
app.wsgi_app = ProxyFix(app.wsgi_app)

# Set up OIDC configuration
app.config.update({
    'OIDC_CLIENT_ID': os.getenv('OIDC_CLIENT_ID'),
    'OIDC_CLIENT_SECRET': os.getenv('OIDC_CLIENT_SECRET'),
    'OIDC_AUTH_URI': os.getenv('OIDC_AUTH_URI'),
    'OIDC_TOKEN_URI': os.getenv('OIDC_TOKEN_URI'),
    'OIDC_ISSUER': os.getenv('OIDC_ISSUER'),
    'OIDC_USERINFO_URI': os.getenv('OIDC_USERINFO_URI'),
    'OIDC_REDIRECT_URIS': os.getenv('OIDC_REDIRECT_URIS', '').split(','),
    'SECRET_KEY': os.getenv('SECRET_KEY'), 
    'OIDC_COOKIE_SECURE': os.getenv('OIDC_COOKIE_SECURE', 'True').lower() == 'true',
    'OIDC_OPENID_REALM': os.getenv('OIDC_OPENID_REALM'),  
})

# Log OIDC-related environment variables to console - Remove this in production
# print("OIDC Configuration:")
# print(f"OIDC_CLIENT_ID: {os.getenv('OIDC_CLIENT_ID')}")
# print(f"OIDC_CLIENT_SECRET: {os.getenv('OIDC_CLIENT_SECRET')}")
# print(f"OIDC_AUTH_URI: {os.getenv('OIDC_AUTH_URI')}")
# print(f"OIDC_TOKEN_URI: {os.getenv('OIDC_TOKEN_URI')}")
# print(f"OIDC_ISSUER: {os.getenv('OIDC_ISSUER')}")
# print(f"OIDC_USERINFO_URI: {os.getenv('OIDC_USERINFO_URI')}")
# print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")
# print(f"OIDC_COOKIE_SECURE: {os.getenv('OIDC_COOKIE_SECURE', 'True').lower() == 'true'}")
# print(f"OIDC_OPENID_REALM: {os.getenv('OIDC_OPENID_REALM')}")
# print(f"REDIRECT_URIS (expected list): {os.getenv('OIDC_REDIRECT_URIS', '').split(',')}")

# Set up OIDC configuration
app.config['redirect_uris'] = os.getenv('OIDC_REDIRECT_URIS', '').split(',')

# Set up OIDC client authentication method
app.config['client_auth_methods'] = ['client_secret_post']  

# Set up OIDC cookie settings
class CustomOpenIDConnect(OpenIDConnect):
    def load_secrets(self, app):
        oidc_config = {
            'web': {
                'client_id': app.config.get('OIDC_CLIENT_ID'),
                'client_secret': app.config.get('OIDC_CLIENT_SECRET'),
                'auth_uri': app.config.get('OIDC_AUTH_URI'),
                'token_uri': app.config.get('OIDC_TOKEN_URI'),
                'issuer': app.config.get('OIDC_ISSUER'),
                'userinfo_uri': app.config.get('OIDC_USERINFO_URI'),
                'redirect_uris': os.getenv('OIDC_REDIRECT_URIS', '').split(','),
                'client_auth_methods': ['client_secret_post']  
            }
        }

        # Check if any values are None or empty strings and raise an error if so
        for key, value in oidc_config['web'].items():
            if not value:
                raise ValueError(f"Missing OIDC configuration for {key}")

        return oidc_config

# Instantiate the OIDC client
oidc = CustomOpenIDConnect(app)

# Set up JumpCloud API key
JUMP_CLOUD_API_KEY = os.getenv('JUMP_CLOUD_API_KEY')

# Base URL for JumpCloud API v2
JUMPCLOUD_BASE_URL = os.getenv('JUMPCLOUD_BASE_URL', 'https://console.jumpcloud.com/api/v2/')

# Load the whitelist from a URL specified in the environment variable
WHITELISTED_APPS_URL = os.getenv('WHITELISTED_APPS_URL')
try:
    response = requests.get(WHITELISTED_APPS_URL)
    if response.status_code == 200:
        whitelisted_apps = response.json()["whitelisted_apps"]
    else:
        logging.error(f"Failed to load whitelisted apps from {WHITELISTED_APPS_URL}")
        whitelisted_apps = []
except Exception as e:
    logging.error(f"Error loading whitelisted apps: {e}")
    whitelisted_apps = []

# Create a mapping of app IDs to compatible OSes
whitelisted_apps_dict = {app['id']: app['compatible_os'] for app in whitelisted_apps}

@app.route('/')
def index():
    if not oidc.user_loggedin:
        return redirect(url_for('login'))
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/api/apps', methods=['GET'])
@oidc.require_login
def apps():
    os_filter = request.args.get('os', '').lower()  # Convert the query parameter to lowercase
    headers = {'x-api-key': JUMP_CLOUD_API_KEY}
    params = {'limit': 100}
    response = requests.get(f"{JUMPCLOUD_BASE_URL}softwareapps", headers=headers, params=params)
    if response.status_code != 200:
        print("Error with API call:", response.status_code, response.text)
        return jsonify([])  # Return an empty list in case of API call failure

    all_apps = response.json()
    # Filter apps based on the OS, ensuring the app ID exists in the whitelist dictionary
    # and comparing OS in a case-insensitive manner
    filtered_apps = [
        app for app in all_apps 
        if app['id'] in whitelisted_apps_dict and os_filter in (os.lower() for os in whitelisted_apps_dict[app['id']])
    ]

    return jsonify(filtered_apps)

def parse_last_contact(last_contact_str):
    # Handle the 'Never' case or any other special cases you have
    if last_contact_str == 'Never':
        return datetime.min
    # Parse the lastContact string into a datetime object with the correct format
    return datetime.strptime(last_contact_str, '%Y-%m-%dT%H:%M:%S.%fZ')

@app.route('/api/devices', methods=['GET'])
@oidc.require_login
def devices():
    user_info = session['oidc_auth_profile']
    user_id = user_info.get('sub')
    devices = get_user_devices(user_id)

    # Sort devices by the parsed 'lastContact' time and include inactive devices
    sorted_devices = sorted(
        devices,
        key=lambda d: parse_last_contact(d['lastContact']),
        reverse=True
    )
    return jsonify(sorted_devices)

def get_user_devices(user_id):
    # Fetch the devices for the user from JumpCloud
    url = JUMPCLOUD_BASE_URL + f'users/{user_id}/systems'
    headers = {'x-api-key': JUMP_CLOUD_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Unable to fetch devices for user {user_id} from JumpCloud. Status code: {response.status_code}, Response: {response.text}")
        return []

    # Parsing the device IDs from the response
    device_ids = [device['id'] for device in response.json()]
    devices_details = []
    for device_id in device_ids:
        # Fetch the details for each device
        url = f'https://console.jumpcloud.com/api/systems/{device_id}'
        device_response = requests.get(url, headers=headers)
        if device_response.status_code != 200:
            print(f"Error: Unable to fetch details for device {device_id} from JumpCloud. Status code: {device_response.status_code}, Response: {device_response.text}")
            continue
        device_data = device_response.json()
        devices_details.append({
            'id': device_id, 
            'name': device_data.get('displayName', 'Unknown'), 
            'os': device_data.get('os', 'Unknown'),
            'osVersion': device_data.get('osVersionDetail', {}).get('osName', 'N/A'),
            'arch': device_data.get('arch', 'Unknown'),
            'hostname': device_data.get('hostname', 'Unknown'),
            'lastContact': device_data.get('lastContact', 'Never'),  
            'active': device_data.get('active', False),
            'model': device_data.get('model', 'Unknown'),
            'manufacturer': device_data.get('manufacturer', 'Unknown'),
            'serialNumber': device_data.get('serialNumber', 'Unknown'),
            'biosVersion': device_data.get('biosVersion', 'Unknown'),
            'biosReleaseDate': device_data.get('biosReleaseDate', 'Unknown'),
            'systemUptime': device_data.get('systemUptime', 'Unknown'),
            'lastUser': device_data.get('lastUser', 'Unknown')
            # ... add other fields as necessary ...
        })
    return devices_details

@app.route('/api/install', methods=['POST'])
@oidc.require_login
def install():
    data = request.json
    app_id = data['appId']
    device_id = data['deviceId']
    url = f"{JUMPCLOUD_BASE_URL}softwareapps/{app_id}/associations"
    headers = {'x-api-key': JUMP_CLOUD_API_KEY, 'Content-Type': 'application/json'}
    payload = {'op': 'add', 'type': 'system', 'id': device_id}
    response = requests.post(url, headers=headers, json=payload)
    status = 'Initiated' if response.status_code == 200 else 'Failed or already installed'
    return jsonify({'status': status})

@app.route('/login')
def login():
    # Initiate OIDC login flow by redirecting user to auth server:
    try:
        print("Initiating OIDC login flow...")
        response = oidc.redirect_to_auth_server()
        print("Redirecting to:", response.headers.get("Location"))
        return response
    except Exception as e:
        app.logger.error(f"Error initiating OIDIC login: {e}")
        return jsonify({'error': 'Login initiation failed'}), 500
        
@app.route('/logout', methods=['GET'])
def logout():
    oidc.logout()
    return redirect(url_for('index'))

@app.route('/oidc-callback', methods=['GET', 'POST'])
def oidc_callback():
    # Log the request details for debugging
    app.logger.info(f"Full request URL: {request.url}")
    app.logger.info(f"Request args: {request.args}")

    # Check if there is an error in the callback
    if 'error' in request.args:
        app.logger.error(f"Error in OIDC callback: {request.args.get('error_description')}")
        return jsonify({'error': request.args.get('error_description')}), 400

    # Process the OIDC callback
    try:
        # Process the callback and store the user info in the session
        if oidc.user_loggedin:
            return redirect(url_for('profile'))
        else:
            return redirect(oidc.authenticate_or_redirect())
    except Exception as e:
        app.logger.error(f"Error processing OIDC callback: {e}")
        return jsonify({'error': 'OIDC callback processing failed'}), 500

@app.route('/profile')
@oidc.require_login
def profile():
    user_info = session['oidc_auth_profile']
    user_id = user_info.get('sub')
    name = user_info.get('name')
    email = user_info.get('email')
    return f'User ID: {user_id}, Name: {name}, Email: {email}'

@app.route('/api/user-info', methods=['GET'])
@oidc.require_login
def user_info():
    user_info = session['oidc_auth_profile']
    app.logger.debug(f"User info: {user_info}")  # Log user info for debugging
    return jsonify(user_info)

if __name__ == '__main__':
    app.run(debug=True)
