# Playto Community Feed

A community feed with threaded discussions and a 24-hour karma leaderboard. Built with Django REST Framework and React.

## What it does

- Users can create posts and comment on them
- Comments can be nested (replies to replies, like Reddit)
- Liking posts gives the author 5 karma, liking comments gives 1 karma
- The leaderboard shows top 5 users by karma earned in the last 24 hours

## Running locally

You need Python 3.10+ and Node.js 18+.

### Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API will be at http://localhost:8000

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The app will be at http://localhost:3000

### Using Docker instead

If you have Docker installed, you can run everything with:

```bash
docker-compose up --build
```

This starts the database, backend, and frontend together. The app will be at http://localhost:3000

## Running tests

```bash
cd backend
python manage.py test
```

## Project structure

```
backend/
  config/         - Django settings and URLs
  feed/           - Main app with models, views, serializers
    models.py     - Post, Comment, PostLike, CommentLike, KarmaTransaction
    views.py      - API endpoints
    tests.py      - Leaderboard and like tests

frontend/
  src/
    components/   - React components
    api.js        - API client
    App.jsx       - Main app with routing
```

## Environment variables

For production, set these on your backend:

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Django secret key
- `DEBUG` - Set to False in production
- `CSRF_TRUSTED_ORIGINS` - Comma-separated list of allowed origins

For the frontend build:

- `VITE_API_URL` - Backend URL (e.g., https://your-api.onrender.com)
