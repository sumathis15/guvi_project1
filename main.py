from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from mysql.connector import Error
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import DB_CONFIG

app = FastAPI(title="Cricbuzz LiveStats API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RapidAPI configuration
RAPIDAPI_KEY = "c898f2b589msh48fdcae0c0d3681p18e812jsn1a5c1547a2ec"
RAPIDAPI_HOST = "cricbuzz-cricket.p.rapidapi.com"
BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com/"

def get_db_connection():
    """Get database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

def get_rapidapi_headers():
    """Get RapidAPI headers"""
    return {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
        "Accept": "application/json"
    }

def check_cache(endpoint: str, cache_key: str = "default") -> Optional[Dict]:
    """Check if data exists in cache and is not expired"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT response_json, last_fetched, ttl_seconds 
        FROM api_cache 
        WHERE endpoint = %s AND cache_key = %s
        """
        cursor.execute(query, (endpoint, cache_key))
        result = cursor.fetchone()
        
        if result:
            last_fetched = result['last_fetched']
            ttl_seconds = result['ttl_seconds']
            
            # Check if cache is still valid
            if datetime.now() - last_fetched < timedelta(seconds=ttl_seconds):
                return json.loads(result['response_json'])
        
        cursor.close()
        conn.close()
        return None
        
    except Error as e:
        print(f"Cache check error: {e}")
        return None

def save_to_cache(endpoint: str, cache_key: str, data: Dict, ttl_seconds: int = 3600):
    """Save data to cache"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO api_cache (endpoint, cache_key, response_json, ttl_seconds)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        response_json = VALUES(response_json),
        last_fetched = CURRENT_TIMESTAMP,
        ttl_seconds = VALUES(ttl_seconds)
        """
        cursor.execute(query, (endpoint, cache_key, json.dumps(data), ttl_seconds))
        conn.commit()
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"Cache save error: {e}")

def fetch_from_rapidapi(endpoint: str) -> Dict:
    """Fetch data from RapidAPI"""
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, headers=get_rapidapi_headers())
        
        # Handle API quota exceeded
        if response.status_code == 429:
            return {"matches": [], "message": "API quota exceeded. Please try again later."}
        
        response.raise_for_status()
        
        # Handle empty responses (204 No Content)
        if response.status_code == 204 or not response.text.strip():
            return {"matches": [], "message": "No data available"}

        data = response.json()
        
        # Debug: Print the actual API response structure (only for debugging)
        # print(f"🔍 DEBUG: API Response for {endpoint}:")
        # print(f"   Status: {response.status_code}")
        # print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        
        # Transform the API response to match expected structure
        if "typeMatches" in data:
            matches = []
            
            for type_match in data["typeMatches"]:
                series_matches = type_match.get("seriesMatches", [])
                
                for series_match in series_matches:
                    # Check if this series_match has matches directly or in a wrapper
                    if "matches" in series_match:
                        match_list = series_match["matches"]
                    elif "seriesAdWrapper" in series_match:
                        match_list = series_match["seriesAdWrapper"].get("matches", [])
                    else:
                        continue
                    
                    for match in match_list:
                        match_info = match.get("matchInfo", {})
                        
                        match_data = {
                            "matchId": str(match_info.get("matchId", "")),
                            "seriesId": str(match_info.get("seriesId", "")),
                            "seriesName": match_info.get("seriesName", ""),
                            "matchDesc": match_info.get("matchDesc", ""),
                            "matchFormat": match_info.get("matchFormat", ""),
                            "team1": {
                                "id": str(match_info.get("team1", {}).get("teamId", "")),
                                "name": match_info.get("team1", {}).get("teamName", ""),
                                "shortName": match_info.get("team1", {}).get("teamSName", "")
                            },
                            "team2": {
                                "id": str(match_info.get("team2", {}).get("teamId", "")),
                                "name": match_info.get("team2", {}).get("teamName", ""),
                                "shortName": match_info.get("team2", {}).get("teamSName", "")
                            },
                            "venue": {
                                "id": str(match_info.get("venueInfo", {}).get("id", "")),
                                "name": match_info.get("venueInfo", {}).get("ground", ""),
                                "city": match_info.get("venueInfo", {}).get("city", "")
                            },
                            "status": match_info.get("status", ""),
                            "state": match_info.get("state", ""),
                            "startDate": match_info.get("startDate", ""),
                            "endDate": match_info.get("endDate", ""),
                            "matchScore": match.get("matchScore", {})  # Include score data
                        }
                        matches.append(match_data)
            
            return {"matches": matches}
        
        return data
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"RapidAPI request failed: {str(e)}")

def get_cached_or_fetch(endpoint: str, cache_key: str = "default", ttl_seconds: int = 3600) -> Dict:
    """Get data from cache or fetch from RapidAPI - ON DEMAND ONLY"""
    # Check cache first
    cached_data = check_cache(endpoint, cache_key)
    if cached_data:
        print(f"Using cached data for {endpoint} (saved API call)")
        return cached_data
    
    # Only fetch from RapidAPI when explicitly requested
    print(f"Fetching from RapidAPI for {endpoint} (on-demand call)")
    data = fetch_from_rapidapi(endpoint)
    
    # Save to cache for future on-demand requests
    save_to_cache(endpoint, cache_key, data, ttl_seconds)
    
    return data




# API Endpoints

@app.get("/")
async def root():
    return {"message": "Cricbuzz LiveStats API", "version": "1.0.0", "auto_reload": "✅ WORKING"}


@app.get("/api/live_matches")
async def get_live_matches():
    """Get live matches - ON DEMAND ONLY"""
    try:
        # Short cache time since we only want on-demand calls (5 minutes)
        data = get_cached_or_fetch("matches/v1/live", "live_matches", 300)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/upcoming_matches")
async def get_upcoming_matches():
    """Get upcoming matches - ON DEMAND ONLY"""
    try:
        # Short cache time since we only want on-demand calls (10 minutes)
        data = get_cached_or_fetch("matches/v1/upcoming", "upcoming_matches", 600)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recent_matches")
async def get_recent_matches():
    """Get recent matches - ON DEMAND ONLY"""
    try:
        # Short cache time since we only want on-demand calls (15 minutes)
        data = get_cached_or_fetch("matches/v1/recent", "recent_matches", 900)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/top_player_stats")
async def get_top_player_stats():
    """Get top player statistics - ON DEMAND ONLY"""
    try:
        # Short cache time since we only want on-demand calls (20 minutes)
        data = get_cached_or_fetch("stats/v1/topstats", "top_stats", 1200)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/player_stats/{player_id}")
async def get_player_stats(player_id: str):
    """Get specific player statistics - ON DEMAND ONLY"""
    try:
        # Short cache time since we only want on-demand calls (30 minutes)
        data = get_cached_or_fetch(f"stats/v1/player/{player_id}", f"player_{player_id}", 1800)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schedule")
async def get_schedule():
    """Get match schedule - ON DEMAND ONLY"""
    try:
        # Short cache time since we only want on-demand calls (30 minutes)
        data = get_cached_or_fetch("schedule/v1/international", "schedule", 1800)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/database_viewer")
async def get_database_viewer():
    """Get database contents for viewing"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all table counts
        tables = ['matches', 'teams', 'venues', 'series', 'players', 'player_stats']
        table_counts = {}
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                result = cursor.fetchone()
                table_counts[table] = result['count'] if result else 0
            except:
                table_counts[table] = 0
        
        cursor.close()
        conn.close()
        
        return {
            "summary": table_counts
        }
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.get("/api/database_tables")
async def get_database_tables():
    """Get list of all database tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {"tables": tables}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.get("/api/database_table/{table_name}")
async def get_database_table(table_name: str):
    """Get data from a specific database table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Validate table name to prevent SQL injection
        allowed_tables = ['matches', 'teams', 'venues', 'series', 'players', 'player_stats']
        if table_name not in allowed_tables:
            raise HTTPException(status_code=400, detail="Invalid table name")
        
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        
        # Get column information
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "table_name": table_name,
            "columns": columns,
            "data": data,
            "total_rows": len(data)
        }
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")


@app.get("/api/analytics/run_query/{query_number}")
async def run_analytics_query(query_number: int):
    """Run predefined analytics query by number (1-25) - Database queries only"""
    try:
        # Get the query from sql_queries
        from sql_queries import get_query_by_number
        
        query_info = get_query_by_number(query_number)
        if not query_info:
            raise HTTPException(status_code=404, detail=f"Query {query_number} not found")
        
        # Execute the query on database (no API calls)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query_info['query'])
        data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "query_number": query_number,
            "title": query_info['title'],
            "description": query_info['description'],
            "category": query_info['category'],
            "query": query_info['query'],
            "data": data,
            "total_rows": len(data)
        }
        
    except ImportError:
        raise HTTPException(status_code=500, detail="SQL queries module not found")
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")

@app.post("/api/analytics/populate_data/{query_number}")
async def populate_query_data(query_number: int):
    """Populate data for a specific query number"""
    try:
        from api_client import ComprehensiveAPIClient
        
        client = ComprehensiveAPIClient()
        
        if query_number == 1:
            result = client.populate_players()  # Indian players
        elif query_number == 2:
            result = client.populate_matches()  # Recent matches
        elif query_number == 3:
            result = client.populate_player_stats()  # ODI stats
        elif query_number == 4:
            result = client.populate_venues()  # Venue capacity
        elif query_number == 5:
            result = client.populate_matches()  # Team wins
        elif query_number == 6:
            result = client.populate_players()  # Player roles
        elif query_number == 7:
            result = True  # Query 7 uses existing data, no population needed
        elif query_number == 8:
            result = client.populate_series()  # Series info
        elif query_number == 9:
            result = True  # Query 9 uses existing data, no population needed
        elif query_number == 10:
            result = client.populate_matches()  # Recent matches
        elif query_number == 13:
            result = client.populate_scorecards()  # Batting partnerships
        elif query_number == 17:
            result = client.populate_toss_data()  # Team head-to-head
        else:
            # For other queries, data is already in database
            result = True
        
        return {
            "query_number": query_number,
            "status": "success",
            "message": f"Data populated for query {query_number}",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error populating data for query {query_number}: {str(e)}")

@app.post("/api/analytics/populate_all_tables")
async def populate_all_tables():
    """Populate all database tables with fresh data"""
    try:
        from api_client import ComprehensiveAPIClient
        
        client = ComprehensiveAPIClient()
        result = client.run_comprehensive_population()
        
        return {
            "status": "success",
            "message": "All tables populated successfully",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error populating all tables: {str(e)}")

@app.post("/api/analytics/update_teams")
async def update_teams():
    """Update only teams table"""
    try:
        from api_client import ComprehensiveAPIClient
        client = ComprehensiveAPIClient()
        result = client.populate_teams()
        if result:
            return {"message": "Teams updated successfully", "success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to update teams")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating teams: {str(e)}")

@app.post("/api/analytics/update_players")
async def update_players():
    """Update only players table"""
    try:
        from api_client import ComprehensiveAPIClient
        client = ComprehensiveAPIClient()
        result = client.populate_players()
        if result:
            return {"message": "Players updated successfully", "success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to update players")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating players: {str(e)}")

@app.post("/api/analytics/update_venues")
async def update_venues():
    """Update only venues table"""
    try:
        from api_client import ComprehensiveAPIClient
        client = ComprehensiveAPIClient()
        result = client.populate_venues()
        if result:
            return {"message": "Venues updated successfully", "success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to update venues")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating venues: {str(e)}")

@app.post("/api/analytics/update_matches")
async def update_matches():
    """Update only matches table"""
    try:
        from api_client import ComprehensiveAPIClient
        client = ComprehensiveAPIClient()
        result = client.populate_matches()
        if result:
            return {"message": "Matches updated successfully", "success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to update matches")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating matches: {str(e)}")

@app.post("/api/analytics/update_series")
async def update_series():
    """Update only series table"""
    try:
        from api_client import ComprehensiveAPIClient
        client = ComprehensiveAPIClient()
        result = client.populate_series()
        if result:
            return {"message": "Series updated successfully", "success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to update series")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating series: {str(e)}")

@app.post("/api/analytics/populate_recent_matches")
async def populate_recent_matches():
    """Populate recent matches data for Queries 2 and 10"""
    try:
        from api_client import ComprehensiveAPIClient
        client = ComprehensiveAPIClient()
        result = client.populate_matches()  # Recent matches are part of matches population
        if result:
            return {"message": "Recent matches populated successfully", "success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to populate recent matches")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error populating recent matches: {str(e)}")

@app.post("/api/analytics/populate_2024_series")
async def populate_2024_series_endpoint():
    """Populate 2024 series data from archives"""
    try:
        from api_client import ComprehensiveAPIClient
        client = ComprehensiveAPIClient()
        result = client.populate_series()  # Series population includes 2024 data
        if result:
            return {"message": "2024 series populated successfully", "success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to populate 2024 series")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error populating 2024 series: {str(e)}")

@app.post("/api/database_query")
async def execute_database_query(request: dict):
    """Execute a custom SQL query"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Extract query from request
        query = request.get('query', '')
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        cursor.execute(query)
        
        # Check if this is a SHOW command or other special commands
        query_upper = query.strip().upper()
        if query_upper.startswith(('SHOW', 'DESCRIBE', 'DESC', 'EXPLAIN')):
            # For SHOW/DESCRIBE commands, fetch all results
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return {
                "query": query,
                "data": data,
                "total_rows": len(data),
                "query_type": "SHOW"
            }
        elif query_upper.startswith('SELECT'):
            # For SELECT queries, fetch data
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return {
                "query": query,
                "data": data,
                "total_rows": len(data),
                "query_type": "SELECT"
            }
        else:
            # For non-SELECT queries, commit and return success message
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            conn.close()
            
            return {
                "query": query,
                "data": [],
                "total_rows": 0,
                "affected_rows": affected_rows,
                "query_type": "MODIFY",
                "message": f"Query executed successfully. {affected_rows} rows affected."
        }
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")






# Legacy analytics endpoint (keeping for backward compatibility)
@app.get("/api/analytics/run_query_legacy/{query_number}")
async def run_analytics_query_legacy(query_number: int):
    """Run predefined analytics query (1-25) - Legacy version"""
    if query_number < 1 or query_number > 25:
        raise HTTPException(status_code=400, detail="Query number must be between 1 and 25")
    
    # Define the 25 SQL queries - FIXED to work with actual data
    queries = {
        1: """
        SELECT name, role, country, created_at
        FROM players 
        WHERE name LIKE '%India%' OR country LIKE '%India%'
        """,
        2: """
        SELECT m.match_id, t1.name as team1_name, t2.name as team2_name, 
               v.name as venue_name, v.city, m.start_datetime, m.status
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        JOIN venues v ON m.venue_id = v.venue_id
        WHERE m.start_datetime >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        ORDER BY m.start_datetime DESC
        LIMIT 20
        """,
        3: """
        SELECT name, total_runs, batting_average, strike_rate, role
        FROM players 
        WHERE total_runs > 0 OR batting_average > 0
        ORDER BY total_runs DESC, batting_average DESC
        LIMIT 10
        """,
        4: """
        SELECT name, city, country, capacity, timezone
        FROM venues 
        WHERE capacity > 0 OR name LIKE '%Stadium%' OR name LIKE '%Ground%'
        ORDER BY capacity DESC, name
        """,
        5: """
        SELECT t.name, COUNT(m.match_id) as wins, 
               COUNT(CASE WHEN m.winner_id = t.team_id THEN 1 END) as actual_wins
        FROM teams t
        LEFT JOIN matches m ON (t.team_id = m.team1_id OR t.team_id = m.team2_id)
        GROUP BY t.team_id, t.name
        ORDER BY actual_wins DESC, wins DESC
        """,
        6: """
        SELECT role, COUNT(*) as player_count
        FROM players 
        WHERE role IS NOT NULL AND role != ''
        GROUP BY role
        ORDER BY player_count DESC
        """,
        7: """
        SELECT 'Current Data' as format, MAX(total_runs) as highest_score, 
               MAX(batting_average) as best_average, COUNT(*) as players_with_stats
        FROM players 
        WHERE total_runs > 0 OR batting_average > 0
        """,
        8: """
        SELECT name, host_country, start_date, total_matches, 
               DATEDIFF(end_date, start_date) as duration_days
        FROM series 
        WHERE start_date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
        ORDER BY start_date DESC
        """,
        9: """
        SELECT name, total_runs, total_wickets, role,
               (total_runs + total_wickets * 20) as all_rounder_score
        FROM players 
        WHERE role = 'All-rounder' OR (total_runs > 0 AND total_wickets > 0)
        ORDER BY all_rounder_score DESC
        """,
        10: """
        SELECT m.match_id, t1.name as team1_name, t2.name as team2_name, 
               tw.name as winner_name, m.victory_margin, m.victory_type, 
               v.name as venue_name, m.start_datetime
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        LEFT JOIN teams tw ON m.winner_id = tw.team_id
        JOIN venues v ON m.venue_id = v.venue_id
        WHERE m.winner_id IS NOT NULL OR m.status LIKE '%completed%'
        ORDER BY m.start_datetime DESC
        LIMIT 20
        """,
        11: """
        SELECT p.name, p.total_runs, p.batting_average, p.strike_rate, p.role,
               p.total_wickets, p.bowling_average
        FROM players p
        WHERE p.total_runs > 0 OR p.total_wickets > 0
        ORDER BY p.total_runs DESC, p.total_wickets DESC
        """,
        12: """
        SELECT t.name as team_name, t.country,
               COUNT(CASE WHEN m.team1_id = t.team_id THEN 1 END) as matches_as_team1,
               COUNT(CASE WHEN m.team2_id = t.team_id THEN 1 END) as matches_as_team2,
               COUNT(CASE WHEN m.winner_id = t.team_id THEN 1 END) as wins
        FROM teams t
        LEFT JOIN matches m ON (t.team_id = m.team1_id OR t.team_id = m.team2_id)
        GROUP BY t.team_id, t.name, t.country
        ORDER BY wins DESC
        """,
        13: """
        SELECT p1.name as player1, p2.name as player2, 
           (p1.total_runs + p2.total_runs) as combined_runs,
           p1.role as player1_role, p2.role as player2_role
        FROM players p1, players p2
        WHERE p1.player_id != p2.player_id 
        AND (p1.total_runs + p2.total_runs) > 0
        ORDER BY combined_runs DESC
        LIMIT 10
        """,
        14: """
        SELECT v.name as venue_name, v.city, v.country,
               COUNT(m.match_id) as total_matches,
               COUNT(CASE WHEN m.winner_id IS NOT NULL THEN 1 END) as completed_matches
        FROM venues v
        LEFT JOIN matches m ON v.venue_id = m.venue_id
        GROUP BY v.venue_id, v.name, v.city, v.country
        ORDER BY total_matches DESC
        """,
        15: """
        SELECT p.name, p.total_runs, p.batting_average, p.role,
               COUNT(m.match_id) as total_matches
        FROM players p
        LEFT JOIN match_players mp ON p.player_id = mp.player_id
        LEFT JOIN matches m ON mp.match_id = m.match_id
        WHERE p.total_runs > 0 OR p.batting_average > 0
        GROUP BY p.player_id, p.name, p.total_runs, p.batting_average, p.role
        ORDER BY p.total_runs DESC
        """,
        16: """
        SELECT p.name, p.role, p.total_runs, p.batting_average,
               p.total_wickets, p.bowling_average, p.created_at
        FROM players p
        WHERE p.total_runs > 0 OR p.total_wickets > 0
        ORDER BY p.created_at DESC
        """,
        17: """
        SELECT 'Match Results' as analysis_type,
               COUNT(CASE WHEN m.winner_id IS NOT NULL THEN 1 END) as completed_matches,
               COUNT(CASE WHEN m.winner_id IS NULL THEN 1 END) as pending_matches,
               COUNT(*) as total_matches
        FROM matches m
        """,
        18: """
        SELECT p.name, p.role, p.total_wickets, p.bowling_average,
               CASE 
                   WHEN p.bowling_average > 0 AND p.bowling_average < 25 THEN 'Excellent'
                   WHEN p.bowling_average >= 25 AND p.bowling_average < 35 THEN 'Good'
                   WHEN p.bowling_average >= 35 AND p.bowling_average < 50 THEN 'Average'
                   ELSE 'Poor'
               END as bowling_rating
        FROM players p
        WHERE p.total_wickets > 0
        ORDER BY p.bowling_average ASC
        """,
        19: """
        SELECT p.name, p.total_runs, p.batting_average, p.strike_rate,
               CASE 
                   WHEN p.batting_average > 0 AND p.batting_average > 50 THEN 'Excellent'
                   WHEN p.batting_average > 0 AND p.batting_average > 35 THEN 'Good'
                   WHEN p.batting_average > 0 AND p.batting_average > 25 THEN 'Average'
                   ELSE 'Poor'
               END as batting_rating
        FROM players p
        WHERE p.total_runs > 0
        ORDER BY p.batting_average DESC
        """,
        20: """
        SELECT p.name, p.role, p.total_runs, p.total_wickets,
               (p.total_runs + p.total_wickets * 20) as all_rounder_score,
               p.created_at
        FROM players p
        WHERE p.total_runs > 0 OR p.total_wickets > 0
        ORDER BY all_rounder_score DESC
        """,
        21: """
        SELECT p.name, p.role, p.total_runs, p.batting_average,
               p.total_wickets, p.bowling_average,
               (p.total_runs * 0.01 + p.batting_average * 0.5 + p.strike_rate * 0.3) as batting_points,
               (p.total_wickets * 2 + (50 - p.bowling_average) * 0.5) as bowling_points
        FROM players p
        WHERE p.total_runs > 0 OR p.total_wickets > 0
        ORDER BY (batting_points + bowling_points) DESC
        """,
        22: """
        SELECT t1.name as team1, t2.name as team2,
               COUNT(m.match_id) as matches_played,
               SUM(CASE WHEN m.winner_id = t1.team_id THEN 1 ELSE 0 END) as team1_wins,
               SUM(CASE WHEN m.winner_id = t2.team_id THEN 1 ELSE 0 END) as team2_wins
        FROM matches m
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        GROUP BY t1.team_id, t2.team_id
        HAVING matches_played > 0
        ORDER BY matches_played DESC
        """,
        23: """
        SELECT p.name, p.role, p.total_runs, p.batting_average,
               p.total_wickets, p.bowling_average, p.created_at,
               CASE 
                   WHEN p.batting_average > 50 THEN 'Excellent'
                   WHEN p.batting_average > 35 THEN 'Good'
                   WHEN p.batting_average > 25 THEN 'Average'
                   ELSE 'Poor'
               END as form_rating
        FROM players p
        WHERE p.total_runs > 0 OR p.total_wickets > 0
        ORDER BY p.created_at DESC
        """,
        24: """
        SELECT p1.name as player1, p2.name as player2,
           p1.total_runs as player1_runs, p2.total_runs as player2_runs,
           (p1.total_runs + p2.total_runs) as combined_runs,
           p1.role as player1_role, p2.role as player2_role
        FROM players p1, players p2
        WHERE p1.player_id != p2.player_id 
        AND (p1.total_runs > 0 OR p2.total_runs > 0)
        ORDER BY combined_runs DESC
        LIMIT 10
        """,
        25: """
        SELECT p.name, p.role, p.total_runs, p.batting_average,
               p.total_wickets, p.bowling_average, p.created_at,
               DATEDIFF(NOW(), p.created_at) as days_since_added
        FROM players p
        WHERE p.total_runs > 0 OR p.total_wickets > 0
        ORDER BY p.created_at DESC
        """
    }
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = queries[query_number]
        cursor.execute(query)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "query_number": query_number,
            "results": results,
            "count": len(results)
        }
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

# CRUD endpoints for matches
@app.get("/api/matches")
async def get_matches():
    """Get all matches from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT m.*, t1.name as team1_name, t2.name as team2_name, 
               v.name as venue_name, tw.name as winner_name
        FROM matches m
        LEFT JOIN teams t1 ON m.team1_id = t1.team_id
        LEFT JOIN teams t2 ON m.team2_id = t2.team_id
        LEFT JOIN venues v ON m.venue_id = v.venue_id
        LEFT JOIN teams tw ON m.winner_id = tw.team_id
        ORDER BY m.start_datetime DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return results
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.post("/api/matches")
async def create_match(match_data: Dict[str, Any]):
    """Create a new match"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO matches (match_id, series_id, team1_id, team2_id, venue_id, 
                           status, start_datetime, winner_id, victory_margin, victory_type, raw_json)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            match_data.get('match_id'),
            match_data.get('series_id'),
            match_data.get('team1_id'),
            match_data.get('team2_id'),
            match_data.get('venue_id'),
            match_data.get('status'),
            match_data.get('start_datetime'),
            match_data.get('winner_id'),
            match_data.get('victory_margin'),
            match_data.get('victory_type'),
            json.dumps(match_data.get('raw_json', {}))
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Match created successfully", "match_id": match_data.get('match_id')}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database insert failed: {str(e)}")

@app.put("/api/matches/{match_id}")
async def update_match(match_id: str, match_data: Dict[str, Any]):
    """Update a match"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE matches SET 
            series_id = %s, team1_id = %s, team2_id = %s, venue_id = %s,
            status = %s, start_datetime = %s, winner_id = %s, 
            victory_margin = %s, victory_type = %s, raw_json = %s
        WHERE match_id = %s
        """
        
        cursor.execute(query, (
            match_data.get('series_id'),
            match_data.get('team1_id'),
            match_data.get('team2_id'),
            match_data.get('venue_id'),
            match_data.get('status'),
            match_data.get('start_datetime'),
            match_data.get('winner_id'),
            match_data.get('victory_margin'),
            match_data.get('victory_type'),
            json.dumps(match_data.get('raw_json', {})),
            match_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Match updated successfully"}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")

@app.delete("/api/matches/{match_id}")
async def delete_match(match_id: str):
    """Delete a match"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM matches WHERE match_id = %s"
        cursor.execute(query, (match_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Match deleted successfully"}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database delete failed: {str(e)}")

# CRUD endpoints for players
@app.get("/api/players")
async def get_players():
    """Get all players from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM players ORDER BY name"
        cursor.execute(query)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return results
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.get("/api/players/{player_id}")
async def get_player(player_id: str):
    """Get a single player by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM players WHERE player_id = %s"
        cursor.execute(query, (player_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Player not found")
        
    except HTTPException:
        raise
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.post("/api/players")
async def create_player(player_data: Dict[str, Any]):
    """Create a new player"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO players (player_id, name, country, role, batting_style, bowling_style, team_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            player_data.get('player_id'),
            player_data.get('name'),
            player_data.get('country'),
            player_data.get('role'),
            player_data.get('batting_style'),
            player_data.get('bowling_style'),
            player_data.get('team_id')
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Player created successfully", "player_id": player_data.get('player_id')}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database insert failed: {str(e)}")

@app.put("/api/players/{player_id}")
async def update_player(player_id: str, player_data: Dict[str, Any]):
    """Update a player"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE players SET 
            name = %s, country = %s, role = %s, batting_style = %s, bowling_style = %s, team_id = %s
        WHERE player_id = %s
        """
        
        cursor.execute(query, (
            player_data.get('name'),
            player_data.get('country'),
            player_data.get('role'),
            player_data.get('batting_style'),
            player_data.get('bowling_style'),
            player_data.get('team_id'),
            player_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Player updated successfully"}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")

@app.delete("/api/players/{player_id}")
async def delete_player(player_id: str):
    """Delete a player"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM players WHERE player_id = %s"
        cursor.execute(query, (player_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": "Player deleted successfully"}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database delete failed: {str(e)}")

# Enhanced Player Statistics Endpoints
@app.get("/api/players/search")
async def search_players(query: str, limit: int = 10):
    """Search players by name with autocomplete functionality"""
    try:
        # Fetch from Cricbuzz API - use the correct search endpoint
        headers = get_rapidapi_headers()
        response = requests.get(f"{BASE_URL}stats/v1/player/search", 
                              headers=headers, 
                              params={"plrN": query})
        
        if response.status_code == 200:
            api_data = response.json()
            players = api_data.get('player', [])
            
            # Limit results based on limit parameter
            filtered_players = players[:limit]
            
            return {"players": filtered_players, "source": "api"}
        else:
            raise HTTPException(status_code=500, detail="API request failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/players/{player_id}/info")
async def get_player_info(player_id: str):
    """Get detailed player information"""
    try:
        # Fetch from API - use player info endpoint
        headers = get_rapidapi_headers()
        response = requests.get(f"{BASE_URL}stats/v1/player/{player_id}", headers=headers)
        
        if response.status_code == 200:
            player_data = response.json()
            return {"player_info": player_data, "source": "api"}
        else:
            raise HTTPException(status_code=404, detail="Player not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch player info: {str(e)}")

@app.get("/api/players/{player_id}/batting")
async def get_player_batting_stats(player_id: str):
    """Get detailed batting statistics for a player"""
    try:
        # Fetch from API - use batting stats endpoint
        headers = get_rapidapi_headers()
        response = requests.get(f"{BASE_URL}stats/v1/player/{player_id}/batting", headers=headers)
        
        if response.status_code == 200:
            batting_data = response.json()
            return {"batting_stats": batting_data, "source": "api"}
        else:
            raise HTTPException(status_code=404, detail="Batting stats not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch batting stats: {str(e)}")

@app.get("/api/players/{player_id}/bowling")
async def get_player_bowling_stats(player_id: str):
    """Get detailed bowling statistics for a player"""
    try:
        # Fetch from API - use bowling stats endpoint
        headers = get_rapidapi_headers()
        response = requests.get(f"{BASE_URL}stats/v1/player/{player_id}/bowling", headers=headers)
        
        if response.status_code == 200:
            bowling_data = response.json()
            return {"bowling_stats": bowling_data, "source": "api"}
        else:
            raise HTTPException(status_code=404, detail="Bowling stats not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bowling stats: {str(e)}")

@app.get("/api/players/{player_id}/teams")
async def get_player_teams(player_id: str):
    """Get teams played for by a player"""
    try:
        # Fetch from API
        headers = get_rapidapi_headers()
        response = requests.get(f"{BASE_URL}stats/v1/player/{player_id}/teams", headers=headers)
        
        if response.status_code == 200:
            teams_data = response.json()
            return {"teams": teams_data, "source": "api"}
        else:
            raise HTTPException(status_code=404, detail="Teams data not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch teams: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
