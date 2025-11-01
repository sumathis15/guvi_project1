# 🏏 Cricbuzz LiveStats

A full-stack cricket statistics application built with FastAPI, Streamlit, and MySQL, integrated with Cricbuzz API via RapidAPI.

## 🚀 Features

- **Live Cricket Data**: Real-time match data, player statistics, and series information
- **Advanced Analytics**: 25 predefined SQL queries for cricket data analysis
- **CRUD Operations**: Create, Read, Update, Delete for matches and players
- **Caching System**: MySQL-based caching for efficient API calls
- **Multi-page Interface**: Clean Streamlit frontend with navigation

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Database**: MySQL with mysql-connector-python
- **Frontend**: Streamlit (multi-page)
- **API**: Cricbuzz via RapidAPI

## 📋 Prerequisites

- Python 3.8+
- MySQL Server
- RapidAPI account (API key required)

## 🔧 Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configuration

1. Copy `config_example.py` to `config.py`:
   ```bash
   copy config_example.py config.py
   ```

2. Update `config.py` with your MySQL credentials and RapidAPI key:
   - Database host, user, password, database name
   - RapidAPI key

### 3. Database Setup

Import the database backup to populate all required data for SQL Analytics:
```bash
python import_database.py cricket_database_backup_20251028_231158.sql
```

This ensures the SQL Analytics page runs smoothly with all necessary data.

### 4. Start the Application

#### Terminal 1: Start FastAPI Backend
```bash
python main.py
```

#### Terminal 2: Start Streamlit Frontend
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## 🌐 API Endpoints

### Cricket Data
- `GET /api/live_matches` - Live cricket matches
- `GET /api/upcoming_matches` - Upcoming matches
- `GET /api/recent_matches` - Recent matches
- `GET /api/top_player_stats` - Top player statistics
- `GET /api/series_info` - Series information

### Analytics
- `GET /api/analytics/run_query/{query_number}` - Run predefined SQL queries (1-25)

### CRUD Operations
- `GET /api/matches`, `POST /api/matches`, `PUT /api/matches/{match_id}`, `DELETE /api/matches/{match_id}`
- `GET /api/players`, `POST /api/players`, `PUT /api/players/{player_id}`, `DELETE /api/players/{player_id}`

## 📊 SQL Analytics

The application includes 25 predefined SQL queries for cricket data analysis. Access them through the SQL Analytics page in the Streamlit frontend.

## 🚨 Troubleshooting

1. **MySQL Connection Failed**
   - Ensure MySQL is running
   - Check credentials in `config.py`
   - Verify MySQL port (default: 3306)

2. **API Connection Failed**
   - Check if FastAPI backend is running on port 8000
   - Verify RapidAPI key is valid in `config.py`

3. **SQL Analytics Not Working**
   - Ensure database backup has been imported
   - Run: `python import_database.py cricket_database_backup_20251028_231158.sql`

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.


---

