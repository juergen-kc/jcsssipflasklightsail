
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



GitHub Copilot: To host your Flask application on AWS Lightsail as a Docker image, you need to follow these steps:

1. **Dockerize your Flask application**
   First, you need to create a Dockerfile in your project directory. Here's a basic example:

   ```Dockerfile
   FROM python:3.8-slim-buster

   WORKDIR /app

   COPY requirements.txt requirements.txt
   RUN pip install -r requirements.txt

   COPY . .

   CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]
   ```

   This Dockerfile creates a Docker image with Python 3.8, installs the dependencies from your `requirements.txt` file, and runs your Flask application.

2. **Build and test your Docker image locally**
   You can build your Docker image using the `docker build` command:

   ```bash
   docker build -t my-flask-app .
   ```

   And then run it with the `docker run` command:

   ```bash
   docker run -p 5000:5000 my-flask-app
   ```

   Your Flask application should now be running at `http://localhost:5000`.

3. **Push your Docker image to a Docker registry**
   Before you can deploy your Docker image to AWS Lightsail, you need to push it to a Docker registry such as Docker Hub. First, tag your image with the name of your Docker Hub repository:

   ```bash
   docker tag my-flask-app:latest my-dockerhub-username/my-flask-app:latest
   ```

   Then push your image to Docker Hub:

   ```bash
   docker push my-dockerhub-username/my-flask-app:latest
   ```

4. **Create a Lightsail container service**
   In the AWS Lightsail console, create a new container service. Choose a location, capacity, and monthly cost that suit your needs.

5. **Deploy your Docker image to Lightsail**
   In the Lightsail console, choose your container service and then choose "Deploy your containers". In the deployment configuration, specify the name of your Docker Hub repository (`my-dockerhub-username/my-flask-app`) and the tag (`latest`). Then choose "Deploy".

Your Flask application should now be running on AWS Lightsail. You can view it by navigating to the public endpoint of your Lightsail container service.
