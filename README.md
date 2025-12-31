# Beer Web App

A community-driven platform for users to log and share the beers they drink, featuring friendly competition through leaderboards and creating a personal digital journal of their experiences.

## Features

- User authentication and profiles
- Post beer entries with photos and descriptions
- View personal beer history
- Browse community beer feed
- Leaderboard with interactive charts
- Image upload and storage

## Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Backend**: Python + FastAPI
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage
- **Charts**: Chart.js + react-chartjs-2
- **Deployment**: Vercel (Frontend), Railway/Heroku (Backend)

## Setup Instructions

### 1. Supabase Setup

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Run the SQL commands in `database-schema.sql` in the Supabase SQL editor
3. Get your project URL and anon key from the project settings

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your Supabase credentials:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

Run the backend:
```bash
python main.py
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:3000`

## API Endpoints

- `POST /api/register` - User registration
- `POST /api/login` - User login
- `POST /api/beers` - Post a new beer (with image upload)
- `GET /api/beers/my` - Get user's beers
- `GET /api/beers/all` - Get all beers
- `DELETE /api/beers/{beer_id}` - Delete a beer
- `GET /api/leaderboard` - Get leaderboard data

## Project Structure

```
Beer/
├── frontend/           # React frontend
│   ├── src/
│   │   ├── components/ # Reusable components
│   │   ├── pages/      # Page components
│   │   └── ...
├── backend/           # FastAPI backend
│   ├── main.py        # Main API file
│   ├── requirements.txt
│   └── .env.example
├── database-schema.sql # Supabase database schema
└── README.md
```

## Deployment

### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Set build command: `cd frontend && npm run build`
3. Set output directory: `frontend/dist`

### Backend (Railway/Heroku)
1. Create a new project
2. Connect your repository
3. Set environment variables (SUPABASE_URL, SUPABASE_ANON_KEY)
4. Deploy from the `backend` directory

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request