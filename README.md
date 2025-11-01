# 🏏 Cricbuzz LiveStats

A full-stack cricket statistics application built with FastAPI, Streamlit, and MySQL, integrated with Cricbuzz API via RapidAPI.

## 🚀 Features

- **Live Cricket Data**: Real-time match data, player statistics, and series information
- **Advanced Analytics**: 25 predefined SQL queries for cricket data analysis
- **CRUD Operations**: Create, Read, Update, Delete for matches and players
- **Caching System**: MySQL-based caching for efficient API calls
- **Multi-page Interface**: Clean Streamlit frontend with navigation
- **Portable Setup**: Works on any device with systematic data population
- **API Integration**: All data from live APIs, no hardcoded values

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Database**: MySQL with mysql-connector-python
- **Frontend**: Streamlit (multi-page)
- **API**: Cricbuzz via RapidAPI
- **Caching**: MySQL-based with TTL support

## 📋 Prerequisites

- Python 3.8+
- MySQL Server
- RapidAPI account (API key provided)

## 🎯 **Portable Setup (Any Device)**

### **Quick Setup for New Device:**
```bash
# 1. Clone and install
git clone <repository>
pip install -r requirements.txt

# 2. Configure
# Update config.py with your database and API details

# 3. Fresh database setup
python setup_fresh_database.py

# 4. Start services
python main.py          # Terminal 1
streamlit run app.py    # Terminal 2
```

### **Systematic Query Implementation:**
- **DEPLOYMENT_GUIDE.md** - Complete setup instructions
- **QUERY_IMPLEMENTATION_GUIDE.md** - Template for new queries
- **API_ORGANIZED.md** - All API endpoints documented
- **Individual populate buttons** for each query's data

## 🔧 Installation & Setup

### 1. Clone and Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. MySQL Setup

#### Option A: Automatic Setup (Recommended)
```bash
# Run the setup script
python setup_mysql.py
```

#### Option B: Manual Setup
1. Install MySQL Server
2. Start MySQL service
3. Run the setup script:
```bash
python setup_database.py
```

### 3. Configuration

Update `config.py` with your MySQL credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_mysql_password',  # Update this
    'database': 'cricbuzz_livestats',
    'port': 3306
}
```

### 4. Start the Application

#### Terminal 1: Start FastAPI Backend
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2: Start Streamlit Frontend
```bash
cd frontend
streamlit run app.py
```

## 🌐 API Endpoints

### Cricket Data
- `GET /api/live_matches` - Live cricket matches
- `GET /api/upcoming_matches` - Upcoming matches
- `GET /api/recent_matches` - Recent matches
- `GET /api/top_player_stats` - Top player statistics
- `GET /api/player_stats/{player_id}` - Specific player stats
- `GET /api/series_info` - Series information

### Analytics
- `GET /api/analytics/run_query/{query_number}` - Run predefined SQL queries (1-25)

### CRUD Operations
- `GET /api/matches` - Get all matches
- `POST /api/matches` - Create match
- `PUT /api/matches/{match_id}` - Update match
- `DELETE /api/matches/{match_id}` - Delete match
- `GET /api/players` - Get all players
- `POST /api/players` - Create player
- `PUT /api/players/{player_id}` - Update player
- `DELETE /api/players/{player_id}` - Delete player

## 📊 SQL Analytics Queries

The application includes 25 predefined analytics queries:

### Beginner (1-8)
1. Indian players with their roles and styles
2. Recent matches with venue details
3. Top 10 ODI run scorers
4. Venues with capacity > 30,000
5. Team win statistics
6. Player count by role
7. Highest scores by format
8. 2024 series information

### Intermediate (9-16)
9. All-rounders with 1000+ runs and 50+ wickets
10. Last 20 completed matches
11. Cross-format player performance
12. Home vs away team performance
13. Batting partnerships (100+ runs)
14. Bowling performance by venue
15. Close match performers
16. Year-over-year batting trends

### Advanced (17-25)
17. Toss advantage analysis
18. Most economical bowlers
19. Consistent batsmen analysis
20. Format-wise match analysis
21. Combined ranking system
22. Head-to-head team analysis
23. Player form analysis
24. Successful partnerships
25. Time-series player analysis

## 🗄️ Database Schema

### Tables
- **matches**: Match information with teams, venue, status
- **players**: Player statistics and career data
- **teams**: Team information
- **venues**: Stadium and venue details
- **series**: Tournament and series information
- **match_players**: Player participation in matches
- **api_cache**: Caching system for API responses

## 🎯 Usage

### Frontend Pages

1. **Home**: Overview and API connection test
2. **Matches**: Live, upcoming, and recent matches
3. **Player Stats**: Top players and detailed statistics
4. **Series Info**: Tournament and series information
5. **SQL Analytics**: Run predefined analytics queries
6. **CRUD Operations**: Manage matches and players

### API Caching

The application implements intelligent caching:
- Live matches: 5-minute cache
- Upcoming matches: 30-minute cache
- Player stats: 1-hour cache
- Series info: 1-hour cache

## 🔍 Testing

### Test API Connection
1. Open the Streamlit app
2. Click "Test API Connection" in the sidebar
3. Verify successful connection

### Test Database
```bash
# Test database connection
python -c "
import mysql.connector
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='your_password',
    database='cricbuzz_livestats'
)
print('Database connected successfully!')
conn.close()
"
```

## 🚨 Troubleshooting

### Common Issues

1. **MySQL Connection Failed**
   - Ensure MySQL is running
   - Check credentials in `config.py`
   - Verify MySQL port (default: 3306)

2. **API Connection Failed**
   - Check if FastAPI backend is running on port 8000
   - Verify RapidAPI key is valid
   - Check internet connection

3. **Streamlit Issues**
   - Ensure all dependencies are installed
   - Check Python version (3.8+)
   - Clear Streamlit cache: `streamlit cache clear`

### Logs and Debugging

- FastAPI logs: Check terminal running uvicorn
- Streamlit logs: Check terminal running streamlit
- Database logs: Check MySQL error logs

## 📈 Performance

- **Caching**: Reduces API calls and improves response time
- **Database Indexing**: Optimized queries with proper indexes
- **Connection Pooling**: Efficient database connections
- **Async Operations**: Non-blocking API calls

## 🔒 Security

- API keys stored in configuration
- Database credentials in separate config file
- CORS enabled for frontend-backend communication
- Input validation on all endpoints

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.


---

