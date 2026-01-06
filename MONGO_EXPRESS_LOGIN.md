# Mongo Express Login Details

## Default Login Credentials

For the Mongo Express interface at **http://localhost:8081**, the default credentials are:

- **Username**: `admin`
- **Password**: `pass`

---

## How to Login

1. Open your browser and navigate to: `http://localhost:8081`
2. Enter the credentials:
   - **Username**: `admin`
   - **Password**: `pass`
3. Click **"Sign in"**

---

## If Default Credentials Don't Work

If the default credentials don't work, you can check or set custom credentials by updating your `docker-compose.yml` file:

```yaml
mongo-express:
  image: mongo-express:1.0.2-20
  environment:
    - ME_CONFIG_MONGODB_SERVER=mongo
    - ME_CONFIG_BASICAUTH_USERNAME=admin    # Set your username
    - ME_CONFIG_BASICAUTH_PASSWORD=pass     # Set your password
  ports:
    - "8081:8081"
  depends_on:
    - mongo
```

After making changes, restart the containers:
```powershell
docker-compose down
docker-compose up --build
```

---

## What is Mongo Express?

Mongo Express is a web-based MongoDB admin interface that allows you to:
- Browse your MongoDB databases and collections
- View, edit, and delete documents
- Run database queries
- Monitor database statistics
- Manage indexes

It's accessible at **http://localhost:8081** when your Docker containers are running.

---

## Current Configuration

Your current `docker-compose.yml` doesn't explicitly set credentials, so Mongo Express should be using its defaults:
- Username: `admin`
- Password: `pass`

---

## Security Note

⚠️ **Important**: These are default credentials and should be changed in production environments. The current setup is suitable for local development only.

