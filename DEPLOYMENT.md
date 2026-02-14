# Deployment Configuration for Render

## Build Command
```bash
pip install -r backend/requirements.txt
```

## Start Command
```bash
gunicorn --chdir backend app:app --bind 0.0.0.0:$PORT
```

## Environment Variables Required

### MONGO_URI
Your MongoDB Atlas connection string:
```
mongodb+srv://username:password@cluster.mongodb.net/bug_tracker_db?retryWrites=true&w=majority
```

### SECRET_KEY
Generate a random secret key (use this command locally):
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## MongoDB Atlas Setup

1. Go to https://cloud.mongodb.com
2. Create a free M0 cluster
3. Database Access → Add Database User
   - Username: `bugadmin`
   - Password: (generate strong password)
4. Network Access → Add IP Address
   - Allow access from anywhere: `0.0.0.0/0`
5. Connect → Connect your application
   - Copy connection string
   - Replace `<password>` with your database password

## Render Setup

1. Go to https://render.com
2. Sign up with GitHub
3. New → Web Service
4. Connect repository: `AI-Bug-Tracking-System`
5. Configure:
   - **Name:** `ai-bug-tracker` (or your choice)
   - **Environment:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `gunicorn --chdir backend app:app --bind 0.0.0.0:$PORT`
6. Add Environment Variables:
   - `MONGO_URI`: (paste MongoDB Atlas connection string)
   - `SECRET_KEY`: (paste generated secret key)
7. Click "Create Web Service"

## Post-Deployment

After deployment completes:

1. Visit your app URL (Render will provide it)
2. Go to `/create-admin` to create the first admin user
3. Test the application

## Troubleshooting

### Build fails
- Check build logs in Render dashboard
- Verify `requirements.txt` is correct

### App crashes
- Check application logs in Render
- Verify `MONGO_URI` is correct
- Verify MongoDB Atlas network access allows all IPs

### Database connection fails
- Check MongoDB Atlas cluster is running
- Verify database user credentials
- Verify network access settings
