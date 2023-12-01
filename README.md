
# Flask OIDC JumpCloud Application

This is a Flask application that uses OpenID Connect (OIDC) for authentication and integrates with the JumpCloud API.

## Features

- OIDC Authentication: Users can log in using their OIDC credentials.
- JumpCloud API Integration: The application can retrieve a user's devices from JumpCloud and install apps on them.
- User Profile: Users will see their Full Name after logging in.

## Setup and Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set the required environment variables:
   ```
   export FLASK_APP=app.py
   export FLASK_ENV=development
   export OIDC_CLIENT_SECRETS=<path-to-client-secrets.json>
   export OIDC_COOKIE_SECURE=False
   export OIDC_CALLBACK_ROUTE=/oidc/callback
   export OIDC_SCOPES="openid email profile"
   export OIDC_ID_TOKEN_COOKIE_NAME="oidc_token"
   ```
4. Run the application:
   ```
   flask run
   ```

## Usage

1. Navigate to `http://localhost:5000` in your web browser.
2. Click on the 'Login' button to log in using your OIDC credentials.
3. After logging in, you will be redirected to your profile page where you can view your profile information and devices.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
```

Please replace `<repository-url>` and `<path-to-client-secrets.json>` with the actual values. You might also want to add more details about the application, its features, and how to use it.
