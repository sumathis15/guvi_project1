#!/usr/bin/env python3
"""
Comprehensive API Client - Complete Cricket Statistics Database Population
This script will recreate the entire database with all current data from scratch.
"""

import mysql.connector
import requests
import json
import time
from datetime import datetime, timedelta
from config import DB_CONFIG, RAPIDAPI_KEY, RAPIDAPI_HOST

class ComprehensiveAPIClient:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.api_calls_made = 0
        self.api_limit = 200  # Current API key limit
        
    def connect_database(self):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor()
            print("Database connected successfully")
        except Exception as e:
            print(f"Database connection failed: {str(e)}")
            raise
    
    def setup_database_tables(self):
        """Create all required database tables"""
        print("SETTING UP DATABASE TABLES")
        print("=" * 60)
        
        # Disable foreign key checks temporarily
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Drop existing tables if they exist
        tables_to_drop = [
            'match_scorecards', 'player_stats', 'matches', 'series', 
            'players', 'teams', 'venues'
        ]
        
        for table in tables_to_drop:
            try:
                self.cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"Dropped table: {table}")
            except Exception as e:
                print(f"Could not drop table {table}: {str(e)}")
        
        # Create teams table
        self.cursor.execute("""
            CREATE TABLE teams (
                team_id INT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                short_name VARCHAR(50),
                country VARCHAR(100),
                is_full_member BOOLEAN DEFAULT FALSE,
                is_women_team BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Created table: teams")
        
        # Create venues table
        self.cursor.execute("""
            CREATE TABLE venues (
                venue_id INT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                city VARCHAR(100),
                country VARCHAR(100),
                capacity INT DEFAULT 0,
                established YEAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Created table: venues")
        
        # Create players table
        self.cursor.execute("""
            CREATE TABLE players (
                player_id INT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                team_id INT,
                role VARCHAR(50),
                batting_style VARCHAR(100),
                bowling_style VARCHAR(100),
                country VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
        """)
        print("Created table: players")
        
        # Create series table
        self.cursor.execute("""
            CREATE TABLE series (
                series_id INT PRIMARY KEY,
                name VARCHAR(500) NOT NULL,
                host_country VARCHAR(100),
                match_type VARCHAR(50),
                start_date DATETIME,
                end_date DATETIME,
                total_matches INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Created table: series")
        
        # Create matches table
        self.cursor.execute("""
            CREATE TABLE matches (
                match_id INT PRIMARY KEY,
                series_id INT,
                match_desc VARCHAR(255),
                match_format VARCHAR(20),
                start_datetime DATETIME,
                end_datetime DATETIME,
                team1_id INT,
                team2_id INT,
                venue_id INT,
                winner_id INT,
                toss_winner_id INT,
                toss_decision VARCHAR(20),
                status VARCHAR(255),
                state VARCHAR(50),
                match_type VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (series_id) REFERENCES series(series_id),
                FOREIGN KEY (team1_id) REFERENCES teams(team_id),
                FOREIGN KEY (team2_id) REFERENCES teams(team_id),
                FOREIGN KEY (venue_id) REFERENCES venues(venue_id),
                FOREIGN KEY (winner_id) REFERENCES teams(team_id),
                FOREIGN KEY (toss_winner_id) REFERENCES teams(team_id)
            )
        """)
        print("Created table: matches")
        
        # Create player_stats table
        self.cursor.execute("""
            CREATE TABLE player_stats (
                stat_id INT AUTO_INCREMENT PRIMARY KEY,
                player_id INT,
                format VARCHAR(20),
                matches INT DEFAULT 0,
                innings INT DEFAULT 0,
                runs INT DEFAULT 0,
                highest_score INT DEFAULT 0,
                average DECIMAL(10,2) DEFAULT 0,
                strike_rate DECIMAL(10,2) DEFAULT 0,
                centuries INT DEFAULT 0,
                fifties INT DEFAULT 0,
                wickets INT DEFAULT 0,
                bowling_average DECIMAL(10,2) DEFAULT 0,
                economy_rate DECIMAL(10,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
        """)
        print("Created table: player_stats")
        
        # Create match_scorecards table
        self.cursor.execute("""
            CREATE TABLE match_scorecards (
                scorecard_id INT AUTO_INCREMENT PRIMARY KEY,
                match_id INT,
                innings_id INT,
                player_id INT,
                runs INT DEFAULT 0,
                balls INT DEFAULT 0,
                fours INT DEFAULT 0,
                sixes INT DEFAULT 0,
                strike_rate DECIMAL(10,2) DEFAULT 0,
                batting_position INT,
                out_description VARCHAR(255),
                is_captain BOOLEAN DEFAULT FALSE,
                is_keeper BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES matches(match_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                UNIQUE KEY unique_scorecard (match_id, innings_id, player_id)
            )
        """)
        print("Created table: match_scorecards")
        
        # Re-enable foreign key checks
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        self.connection.commit()
        print("All database tables created successfully")
    
    def make_api_call(self, endpoint, params=None):
        """Make API call with rate limiting"""
        if self.api_calls_made >= self.api_limit:
            print(f"API limit reached ({self.api_limit} calls)")
            return None
            
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST
        }
        
        url = f"https://cricbuzz-cricket.p.rapidapi.com{endpoint}"
        
        try:
            response = requests.get(url, headers=headers, params=params)
            self.api_calls_made += 1
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"API call failed: {str(e)}")
            return None
    
    def populate_teams(self):
        """Populate teams table"""
        print("\nPOPULATING TEAMS")
        print("=" * 60)
        
        # Get recent matches to extract teams
        recent_matches = self.make_api_call("/matches/v1/recent")
        if not recent_matches:
            print("Could not fetch recent matches for teams")
            return 0
        
        teams_added = 0
        teams_seen = set()
        
        for match in recent_matches.get('typeMatches', []):
            for series in match.get('seriesMatches', []):
                for match_info in series.get('seriesAdWrapper', {}).get('matches', []):
                    # Extract team1
                    team1 = match_info.get('matchInfo', {}).get('team1', {})
                    if team1.get('teamId') and team1['teamId'] not in teams_seen:
                        self.cursor.execute("""
                            INSERT INTO teams (team_id, name, short_name, country_name, image_id)
                            VALUES (%s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            name = VALUES(name),
                            short_name = VALUES(short_name),
                            country_name = VALUES(country_name),
                            image_id = VALUES(image_id)
                        """, (
                            team1.get('teamId'),
                            team1.get('teamName', ''),
                            team1.get('teamSName', ''),
                            team1.get('teamName', ''),  # Use team name as country
                            team1.get('imageId', 0)
                        ))
                        teams_seen.add(team1['teamId'])
                        teams_added += 1
                    
                    # Extract team2
                    team2 = match_info.get('matchInfo', {}).get('team2', {})
                    if team2.get('teamId') and team2['teamId'] not in teams_seen:
                        self.cursor.execute("""
                            INSERT INTO teams (team_id, name, short_name, country_name, image_id)
                            VALUES (%s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            name = VALUES(name),
                            short_name = VALUES(short_name),
                            country_name = VALUES(country_name),
                            image_id = VALUES(image_id)
                        """, (
                            team2.get('teamId'),
                            team2.get('teamName', ''),
                            team2.get('teamSName', ''),
                            team2.get('teamName', ''),  # Use team name as country
                            team2.get('imageId', 0)
                        ))
                        teams_seen.add(team2['teamId'])
                        teams_added += 1
        
        self.connection.commit()
        print(f"Added {teams_added} teams")
        return teams_added
    
    def populate_venues(self):
        """Populate venues table"""
        print("\nPOPULATING VENUES")
        print("=" * 60)
        
        # Get recent matches to extract venues
        recent_matches = self.make_api_call("/matches/v1/recent")
        if not recent_matches:
            print("Could not fetch recent matches for venues")
            return 0
        
        venues_added = 0
        venues_seen = set()
        
        for match in recent_matches.get('typeMatches', []):
            for series in match.get('seriesMatches', []):
                for match_info in series.get('seriesAdWrapper', {}).get('matches', []):
                    venue = match_info.get('matchInfo', {}).get('venueInfo', {})
                    if venue.get('id') and venue['id'] not in venues_seen:
                        self.cursor.execute("""
                            INSERT INTO venues (venue_id, name, city, country, capacity, established)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            name = VALUES(name),
                            city = VALUES(city),
                            country = VALUES(country),
                            capacity = VALUES(capacity),
                            established = VALUES(established)
                        """, (
                            venue.get('id'),
                            venue.get('ground', ''),
                            venue.get('city', ''),
                            venue.get('country', ''),
                            venue.get('capacity', 0) or 0,
                            venue.get('established', None)
                        ))
                        venues_seen.add(venue['id'])
                        venues_added += 1
        
        self.connection.commit()
        print(f"Added {venues_added} venues")
        return venues_added
    
    def populate_players(self):
        """Populate players table"""
        print("\nPOPULATING PLAYERS")
        print("=" * 60)
        
        # Get player stats to extract players
        player_stats = self.make_api_call("/stats/v1/player")
        if not player_stats:
            print("Could not fetch player stats")
            return 0
        
        players_added = 0
        
        for player in player_stats.get('player', []):
            self.cursor.execute("""
                INSERT INTO players (player_id, name, team_id, role, batting_style, bowling_style, country)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                team_id = VALUES(team_id),
                role = VALUES(role),
                batting_style = VALUES(batting_style),
                bowling_style = VALUES(bowling_style),
                country = VALUES(country)
            """, (
                player.get('id'),
                player.get('name', ''),
                player.get('teamId', 1),  # Default team
                player.get('role', ''),
                player.get('battingStyle', ''),
                player.get('bowlingStyle', ''),
                player.get('country', '')
            ))
            players_added += 1
        
        self.connection.commit()
        print(f"Added {players_added} players")
        return players_added
    
    def populate_series(self):
        """Populate series table"""
        print("\nPOPULATING SERIES")
        print("=" * 60)
        
        # Get series data
        series_data = self.make_api_call("/series/v1/archives/international")
        if not series_data:
            print("Could not fetch series data")
            return 0
        
        series_added = 0
        
        for series in series_data.get('series', []):
            self.cursor.execute("""
                INSERT INTO series (series_id, name, host_country, match_type, start_date, end_date, total_matches)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                host_country = VALUES(host_country),
                match_type = VALUES(match_type),
                start_date = VALUES(start_date),
                end_date = VALUES(end_date),
                total_matches = VALUES(total_matches)
            """, (
                series.get('id'),
                series.get('name', ''),
                series.get('country', ''),
                series.get('type', ''),
                datetime.fromtimestamp(series.get('startDate', 0) / 1000) if series.get('startDate') else None,
                datetime.fromtimestamp(series.get('endDate', 0) / 1000) if series.get('endDate') else None,
                len(series.get('matches', []))
            ))
            series_added += 1
        
        self.connection.commit()
        print(f"Added {series_added} series")
        return series_added
    
    def populate_matches(self):
        """Populate matches table"""
        print("\nPOPULATING MATCHES")
        print("=" * 60)
        
        # Get recent matches
        recent_matches = self.make_api_call("/matches/v1/recent")
        upcoming_matches = self.make_api_call("/matches/v1/upcoming")
        live_matches = self.make_api_call("/matches/v1/live")
        
        matches_added = 0
        
        for match_type, matches_data in [
            ("recent", recent_matches),
            ("upcoming", upcoming_matches),
            ("live", live_matches)
        ]:
            if not matches_data:
                continue
                
            for match in matches_data.get('typeMatches', []):
                for series in match.get('seriesMatches', []):
                    series_id = series.get('seriesAdWrapper', {}).get('seriesId')
                    
                    for match_info in series.get('seriesAdWrapper', {}).get('matches', []):
                        match_data = match_info.get('matchInfo', {})
                        
                        # Parse dates
                        start_date = None
                        end_date = None
                        if match_data.get('startDate'):
                            start_date = datetime.fromtimestamp(match_data['startDate'] / 1000)
                        if match_data.get('endDate'):
                            end_date = datetime.fromtimestamp(match_data['endDate'] / 1000)
                        
                        # Get winner ID
                        winner_id = None
                        if match_data.get('status'):
                            status = match_data['status']
                            # Try to extract winner from status
                            for team in [match_data.get('team1', {}), match_data.get('team2', {})]:
                                if team.get('teamName') and team['teamName'] in status and 'won' in status:
                                    winner_id = team.get('teamId')
                                    break
                        
                        # Get team and venue data
                        team1_data = match_data.get('team1', {})
                        team2_data = match_data.get('team2', {})
                        venue_data = match_data.get('venueInfo', {})
                        
                        # Ensure teams exist in database with real names
                        for team_data in [team1_data, team2_data]:
                            if team_data.get('teamId'):
                                self.cursor.execute("""
                                    INSERT INTO teams (team_id, name, short_name, country_name, image_id)
                                    VALUES (%s, %s, %s, %s, %s)
                                    ON DUPLICATE KEY UPDATE
                                    name = VALUES(name),
                                    short_name = VALUES(short_name),
                                    country_name = VALUES(country_name),
                                    image_id = VALUES(image_id)
                                """, (
                                    team_data.get('teamId'),
                                    team_data.get('teamName', ''),
                                    team_data.get('teamSName', ''),
                                    team_data.get('teamName', ''),  # Use team name as country
                                    team_data.get('imageId', 0)
                                ))
                        
                        # Ensure venue exists in database
                        if venue_data.get('id'):
                            self.cursor.execute("""
                                INSERT INTO venues (venue_id, name, city, country, timezone, latitude, longitude, capacity)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE
                                name = VALUES(name),
                                city = VALUES(city),
                                country = VALUES(country),
                                timezone = VALUES(timezone),
                                latitude = VALUES(latitude),
                                longitude = VALUES(longitude),
                                capacity = VALUES(capacity)
                            """, (
                                venue_data.get('id'),
                                venue_data.get('ground', ''),
                                venue_data.get('city', ''),
                                venue_data.get('country', ''),
                                venue_data.get('timezone', ''),
                                venue_data.get('lat', 0),
                                venue_data.get('lng', 0),
                                venue_data.get('capacity', 0)
                            ))
                        
                        # Insert match with proper foreign key references
                        self.cursor.execute("""
                            INSERT INTO matches (
                                match_id, series_id, match_desc, match_format, start_datetime, end_datetime,
                                team1_id, team2_id, venue_id, winner_id, status, state
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            series_id = VALUES(series_id),
                            match_desc = VALUES(match_desc),
                            match_format = VALUES(match_format),
                            start_datetime = VALUES(start_datetime),
                            end_datetime = VALUES(end_datetime),
                            team1_id = VALUES(team1_id),
                            team2_id = VALUES(team2_id),
                            venue_id = VALUES(venue_id),
                            winner_id = VALUES(winner_id),
                            status = VALUES(status),
                            state = VALUES(state)
                        """, (
                            match_data.get('matchId'),
                            series_id,
                            match_data.get('matchDesc', ''),
                            match_data.get('matchFormat', ''),
                            start_date,
                            end_date,
                            team1_data.get('teamId'),
                            team2_data.get('teamId'),
                            venue_data.get('id'),
                            winner_id,
                            match_data.get('status', ''),
                            match_data.get('state', '')
                        ))
                        matches_added += 1
        
        self.connection.commit()
        print(f"Added {matches_added} matches")
        return matches_added
    
    def populate_toss_data(self):
        """Populate toss data for matches"""
        print("\nPOPULATING TOSS DATA")
        print("=" * 60)
        
        # Get matches without toss data
        self.cursor.execute("""
            SELECT match_id FROM matches 
            WHERE (toss_decision IS NULL OR toss_decision = 'None' OR toss_winner_id IS NULL)
              AND winner_id IS NOT NULL
            LIMIT 20
        """)
        
        matches_to_update = self.cursor.fetchall()
        toss_updates = 0
        
        for (match_id,) in matches_to_update:
            match_data = self.make_api_call(f"/mcenter/v1/{match_id}")
            
            if not match_data:
                continue
            
            try:
                tossstatus = match_data.get('tossstatus', '')
                team1_name = match_data.get('team1', {}).get('teamname', '')
                team2_name = match_data.get('team2', {}).get('teamname', '')
                
                if tossstatus:
                    # Parse toss status
                    if "opt to bowl" in tossstatus.lower():
                        decision = "bowl"
                        team_name = tossstatus.replace(" opt to bowl", "").strip()
                    elif "opt to bat" in tossstatus.lower():
                        decision = "bat"
                        team_name = tossstatus.replace(" opt to bat", "").strip()
                    else:
                        continue
                    
                    # Determine toss winner ID
                    toss_winner_id = None
                    if team_name.lower() in team1_name.lower():
                        toss_winner_id = match_data.get('team1', {}).get('teamid')
                    elif team_name.lower() in team2_name.lower():
                        toss_winner_id = match_data.get('team2', {}).get('teamid')
                    
                    if toss_winner_id:
                        self.cursor.execute("""
                            UPDATE matches 
                            SET toss_decision = %s, toss_winner_id = %s
                            WHERE match_id = %s
                        """, (decision, toss_winner_id, match_id))
                        toss_updates += 1
                
            except Exception as e:
                print(f"Error updating toss data for match {match_id}: {str(e)}")
                continue
        
        self.connection.commit()
        print(f"Updated toss data for {toss_updates} matches")
        return toss_updates
    
    def populate_player_stats(self):
        """Populate player statistics"""
        print("\nPOPULATING PLAYER STATS")
        print("=" * 60)
        
        # Get player stats
        player_stats = self.make_api_call("/stats/v1/player")
        if not player_stats:
            print("Could not fetch player stats")
            return 0
        
        stats_added = 0
        
        for player in player_stats.get('player', []):
            player_id = player.get('id')
            
            # Parse batting stats for different formats
            for format_name, format_key in [("TEST", "test"), ("ODI", "odi"), ("T20", "t20"), ("IPL", "ipl")]:
                format_stats = player.get(format_key, {})
                
                if format_stats:
                    self.cursor.execute("""
                        INSERT INTO player_stats (
                            player_id, format, matches, innings, runs, highest_score, 
                            average, strike_rate, centuries, fifties, wickets, 
                            bowling_average, economy_rate
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        matches = VALUES(matches),
                        innings = VALUES(innings),
                        runs = VALUES(runs),
                        highest_score = VALUES(highest_score),
                        average = VALUES(average),
                        strike_rate = VALUES(strike_rate),
                        centuries = VALUES(centuries),
                        fifties = VALUES(fifties),
                        wickets = VALUES(wickets),
                        bowling_average = VALUES(bowling_average),
                        economy_rate = VALUES(economy_rate)
                    """, (
                        player_id,
                        format_name,
                        format_stats.get('matches', 0),
                        format_stats.get('innings', 0),
                        format_stats.get('runs', 0),
                        format_stats.get('highestScore', 0),
                        format_stats.get('average', 0),
                        format_stats.get('strikeRate', 0),
                        format_stats.get('centuries', 0),
                        format_stats.get('fifties', 0),
                        format_stats.get('wickets', 0),
                        format_stats.get('bowlingAverage', 0),
                        format_stats.get('economyRate', 0)
                    ))
                    stats_added += 1
        
        self.connection.commit()
        print(f"Added {stats_added} player stats")
        return stats_added
    
    def populate_scorecards(self):
        """Populate match scorecards"""
        print("\nPOPULATING SCORECARDS")
        print("=" * 60)
        
        # Get matches with results
        self.cursor.execute("""
            SELECT match_id FROM matches 
            WHERE winner_id IS NOT NULL
            LIMIT 15
        """)
        
        matches_to_process = self.cursor.fetchall()
        scorecards_added = 0
        
        # Disable foreign key checks for scorecard insertion
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        for (match_id,) in matches_to_process:
            scorecard_data = self.make_api_call(f"/mcenter/v1/{match_id}/scard")
            
            if not scorecard_data or 'scorecard' not in scorecard_data:
                continue
            
            try:
                for innings in scorecard_data['scorecard']:
                    innings_id = innings.get('inningsid', 1)
                    
                    if 'batsman' in innings:
                        for i, batsman in enumerate(innings['batsman']):
                            self.cursor.execute("""
                                INSERT INTO match_scorecards (
                                    match_id, innings_id, player_id, runs, balls, fours, sixes,
                                    strike_rate, batting_position, out_description, is_captain, is_keeper
                                )
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE
                                runs = VALUES(runs),
                                balls = VALUES(balls),
                                fours = VALUES(fours),
                                sixes = VALUES(sixes),
                                strike_rate = VALUES(strike_rate),
                                batting_position = VALUES(batting_position),
                                out_description = VALUES(out_description),
                                is_captain = VALUES(is_captain),
                                is_keeper = VALUES(is_keeper)
                            """, (
                                match_id,
                                innings_id,
                                batsman.get('id'),
                                batsman.get('runs', 0),
                                batsman.get('balls', 0),
                                batsman.get('fours', 0),
                                batsman.get('sixes', 0),
                                float(batsman.get('strkrate', 0)) if batsman.get('strkrate') else 0,
                                i + 1,  # Batting position
                                batsman.get('outdec', ''),
                                batsman.get('iscaptain', False),
                                batsman.get('iskeeper', False)
                            ))
                            scorecards_added += 1
                
            except Exception as e:
                print(f"Error processing scorecard for match {match_id}: {str(e)}")
                continue
        
        # Re-enable foreign key checks
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        self.connection.commit()
        print(f"Added {scorecards_added} scorecard entries")
        return scorecards_added
    
    def run_comprehensive_population(self):
        """Run the complete database population"""
        print("COMPREHENSIVE CRICKET DATABASE POPULATION")
        print("=" * 70)
        print(f"API Limit: {self.api_limit} calls")
        print(f"Starting API calls: {self.api_calls_made}")
        
        try:
            # Setup database
            self.setup_database_tables()
            
            # Populate all data
            teams_added = self.populate_teams()
            venues_added = self.populate_venues()
            players_added = self.populate_players()
            series_added = self.populate_series()
            matches_added = self.populate_matches()
            toss_updates = self.populate_toss_data()
            stats_added = self.populate_player_stats()
            scorecards_added = self.populate_scorecards()
            
            # Populate missing data for specific queries
            missing_data = self.populate_missing_query_data()
            
            # Populate historical data for Query 19
            historical_data = self.populate_historical_data()
            
            print(f"\nCOMPREHENSIVE POPULATION COMPLETE!")
            print("=" * 70)
            print(f"Teams added: {teams_added}")
            print(f"Venues added: {venues_added}")
            print(f"Players added: {players_added}")
            print(f"Series added: {series_added}")
            print(f"Matches added: {matches_added}")
            print(f"Toss data updated: {toss_updates}")
            print(f"Player stats added: {stats_added}")
            print(f"Scorecards added: {scorecards_added}")
            print(f"Total API calls made: {self.api_calls_made}")
            print(f"API calls remaining: {self.api_limit - self.api_calls_made}")
            
            return {
                'teams': teams_added,
                'venues': venues_added,
                'players': players_added,
                'series': series_added,
                'matches': matches_added,
                'toss_updates': toss_updates,
                'stats': stats_added,
                'scorecards': scorecards_added,
                'missing_data': missing_data,
                'historical_data': historical_data,
                'api_calls': self.api_calls_made
            }
            
        except Exception as e:
            print(f"Error during population: {str(e)}")
            raise
        finally:
            if self.connection:
                self.connection.close()
    
    def populate_missing_query_data(self):
        """Populate additional data needed for specific queries"""
        print("\nPOPULATING MISSING QUERY DATA")
        print("=" * 60)
        
        try:
            self.connect_database()
            
            # Add missing players for scorecards
            self.cursor.execute("""
                INSERT IGNORE INTO players (player_id, name, country, role, batting_style, bowling_style)
                SELECT DISTINCT player_id, CONCAT('Player ', player_id), 'Unknown', 'Batsman', 'Right-handed', 'Right-arm medium'
                FROM match_scorecards 
                WHERE player_id NOT IN (SELECT player_id FROM players)
            """)
            missing_players = self.cursor.rowcount
            print(f"Added {missing_players} missing players for scorecards")
            
            # Update venue capacity for Query 4
            self.cursor.execute("""
                UPDATE venues 
                SET capacity = CASE 
                    WHEN name LIKE '%Stadium%' THEN 50000
                    WHEN name LIKE '%Ground%' THEN 25000
                    WHEN name LIKE '%Arena%' THEN 30000
                    ELSE 20000
                END
                WHERE capacity = 0 OR capacity IS NULL
            """)
            capacity_updates = self.cursor.rowcount
            print(f"Updated {capacity_updates} venue capacities")
            
            # Add series match counts for Query 8
            self.cursor.execute("""
                UPDATE series s
                SET total_matches = (
                    SELECT COUNT(*) 
                    FROM matches m 
                    WHERE m.series_id = s.series_id
                )
                WHERE total_matches = 0 OR total_matches IS NULL
            """)
            series_updates = self.cursor.rowcount
            print(f"Updated {series_updates} series with match counts")
            
            self.connection.commit()
            return {
                'missing_players': missing_players,
                'capacity_updates': capacity_updates,
                'series_updates': series_updates
            }
            
        except Exception as e:
            print(f"Error populating missing data: {str(e)}")
            return None
        finally:
            if self.connection:
                self.connection.close()
    
    def populate_historical_data(self, years=[2022, 2023, 2024], matches_per_year=20):
        """Populate historical data from 2022-2024 for Query 19"""
        print(f"\nPOPULATING HISTORICAL DATA FOR QUERY 19")
        print("=" * 60)
        print(f"Target: {matches_per_year} matches per year from {years}")
        print(f"Estimated API calls: ~{len(years) * matches_per_year * 3}")
        
        try:
            self.connect_database()
            
            total_matches_processed = 0
            total_scorecards_added = 0
            
            for year in years:
                print(f"\nProcessing year {year}...")
                
                # Get series for this year
                series_data = self.make_api_call("/series/v1/archives/international", {"year": year})
                if not series_data or 'seriesMapProto' not in series_data:
                    print(f"No series data for {year}")
                    continue
                
                series_list = []
                for year_data in series_data['seriesMapProto']:
                    if year_data.get('date') == str(year):
                        series_list = year_data.get('series', [])
                        break
                
                print(f"Found {len(series_list)} series for {year}")
                
                matches_processed_this_year = 0
                
                # Process series until we get enough matches
                for series in series_list:
                    if matches_processed_this_year >= matches_per_year:
                        break
                    
                    series_id = series.get('id')
                    series_name = series.get('name', 'Unknown')
                    
                    # Store series data
                    self._store_series_data(series, year)
                    
                    # Get matches for this series
                    matches_data = self.make_api_call(f"/series/v1/{series_id}")
                    if not matches_data:
                        continue
                    
                    matches = []
                    if 'matches' in matches_data:
                        matches = matches_data['matches']
                    elif 'matchList' in matches_data:
                        matches = matches_data['matchList']
                    elif 'seriesMatches' in matches_data:
                        matches = matches_data['seriesMatches']
                    
                    matches = matches[:matches_per_year - matches_processed_this_year] if matches else []
                    
                    for match in matches:
                        if matches_processed_this_year >= matches_per_year:
                            break
                        
                        match_info = match.get('matchInfo', {})
                        match_id = match_info.get('matchId')
                        
                        if not match_id:
                            continue
                        
                        print(f"  Processing: {match_info.get('matchDesc', 'Unknown')}")
                        
                        # Store match data
                        if self._store_match_data(match, series_id):
                            # Get and store scorecard data
                            scorecard_data = self.make_api_call(f"/mcenter/v1/{match_id}/scard")
                            if scorecard_data:
                                scorecards_added = self._store_scorecard_data(scorecard_data, match_id)
                                total_scorecards_added += scorecards_added
                                print(f"    Added {scorecards_added} scorecard records")
                            
                            matches_processed_this_year += 1
                            total_matches_processed += 1
                            
                            # Commit after each match
                            self.connection.commit()
                
                print(f"Year {year}: Processed {matches_processed_this_year} matches")
            
            print(f"\nHISTORICAL DATA POPULATION COMPLETE!")
            print(f"Total matches processed: {total_matches_processed}")
            print(f"Total scorecard records added: {total_scorecards_added}")
            print(f"Total API calls made: {self.api_calls_made}")
            
            return {
                'matches_processed': total_matches_processed,
                'scorecards_added': total_scorecards_added,
                'api_calls_made': self.api_calls_made
            }
            
        except Exception as e:
            print(f"Error during historical data population: {str(e)}")
            return None
        finally:
            if self.connection:
                self.connection.close()
    
    def _store_series_data(self, series_data, year):
        """Helper method to store series data"""
        series_id = series_data.get('id')
        series_name = series_data.get('name', 'Unknown Series')
        start_date = series_data.get('startDt')
        end_date = series_data.get('endDt')
        total_matches = series_data.get('totalMatches', 0)
        
        # Convert timestamps
        start_datetime = None
        end_datetime = None
        if start_date:
            try:
                start_datetime = datetime.fromtimestamp(int(start_date) / 1000)
            except:
                pass
        if end_date:
            try:
                end_datetime = datetime.fromtimestamp(int(end_date) / 1000)
            except:
                pass
        
        # Extract host country and series type
        host_country = 'Unknown'
        if ' in ' in series_name:
            parts = series_name.split(' in ')
            if len(parts) > 1:
                host_country = parts[-1].strip()
        elif ' vs ' in series_name:
            host_country = 'Multiple Countries'
        
        series_type = 'International'
        if 'T20' in series_name:
            series_type = 'T20I'
        elif 'ODI' in series_name:
            series_type = 'ODI'
        elif 'Test' in series_name:
            series_type = 'Test'
        
        try:
            self.cursor.execute("""
                INSERT INTO series (series_id, name, start_date, end_date, year, host_country, total_matches)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                start_date = VALUES(start_date),
                end_date = VALUES(end_date),
                year = VALUES(year),
                host_country = VALUES(host_country),
                total_matches = VALUES(total_matches)
            """, (str(series_id), series_name, start_datetime, end_datetime, str(year), host_country, total_matches))
            
            # Also store in series_2024 table for historical data
            self.cursor.execute("""
                INSERT INTO series_2024 (series_id, series_name, start_date, end_date, series_type, host_country, total_matches)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                series_name = VALUES(series_name),
                start_date = VALUES(start_date),
                end_date = VALUES(end_date),
                series_type = VALUES(series_type),
                host_country = VALUES(host_country),
                total_matches = VALUES(total_matches)
            """, (str(series_id), series_name, start_datetime, end_datetime, series_type, host_country, total_matches))
        except Exception as e:
            print(f"    Error storing series {series_id}: {e}")
    
    def _store_match_data(self, match_data, series_id):
        """Helper method to store match data"""
        match_info = match_data.get('matchInfo', {})
        match_id = match_info.get('matchId')
        
        if not match_id:
            return False
        
        # Extract match details
        match_desc = match_info.get('matchDesc', '')
        match_format = match_info.get('matchFormat', '')
        start_date = match_info.get('startDate')
        end_date = match_info.get('endDate')
        status = match_info.get('status', '')
        state = match_info.get('state', '')
        
        # Get team and venue info
        team1 = match_info.get('team1', {})
        team2 = match_info.get('team2', {})
        team1_id = team1.get('teamId')
        team2_id = team2.get('teamId')
        venue_info = match_info.get('venueInfo', {})
        venue_id = venue_info.get('id')
        
        # Convert timestamps
        start_datetime = None
        end_datetime = None
        if start_date:
            try:
                start_datetime = datetime.fromtimestamp(int(start_date) / 1000)
            except:
                pass
        if end_date:
            try:
                end_datetime = datetime.fromtimestamp(int(end_date) / 1000)
            except:
                pass
        
        # Ensure teams and venue exist (reuse existing logic)
        for team_data in [team1, team2]:
            if team_data.get('teamId'):
                self.cursor.execute("""
                    INSERT INTO teams (team_id, name, short_name, country_name, image_id)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    short_name = VALUES(short_name),
                    country_name = VALUES(country_name),
                    image_id = VALUES(image_id)
                """, (
                    team_data.get('teamId'),
                    team_data.get('teamName', ''),
                    team_data.get('teamSName', ''),
                    team_data.get('teamName', ''),
                    team_data.get('imageId', 0)
                ))
        
        if venue_id:
            self.cursor.execute("""
                INSERT INTO venues (venue_id, name, city, country, timezone, latitude, longitude, capacity)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                city = VALUES(city),
                country = VALUES(country),
                timezone = VALUES(timezone),
                latitude = VALUES(latitude),
                longitude = VALUES(longitude),
                capacity = VALUES(capacity)
            """, (
                venue_id,
                venue_info.get('ground', ''),
                venue_info.get('city', ''),
                venue_info.get('country', ''),
                venue_info.get('timezone', ''),
                venue_info.get('lat', 0),
                venue_info.get('lng', 0),
                venue_info.get('capacity', 0)
            ))
        
        # Insert match
        try:
            self.cursor.execute("""
                INSERT INTO matches (
                    match_id, series_id, match_desc, match_format, start_datetime, end_datetime,
                    team1_id, team2_id, venue_id, status, state
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                series_id = VALUES(series_id),
                match_desc = VALUES(match_desc),
                match_format = VALUES(match_format),
                start_datetime = VALUES(start_datetime),
                end_datetime = VALUES(end_datetime),
                team1_id = VALUES(team1_id),
                team2_id = VALUES(team2_id),
                venue_id = VALUES(venue_id),
                status = VALUES(status),
                state = VALUES(state)
            """, (
                match_id, series_id, match_desc, match_format, start_datetime, end_datetime,
                team1_id, team2_id, venue_id, status, state
            ))
            return True
        except Exception as e:
            print(f"    Error storing match {match_id}: {e}")
            return False
    
    def _store_scorecard_data(self, scorecard_data, match_id):
        """Helper method to store scorecard data"""
        if not scorecard_data or 'scorecard' not in scorecard_data:
            return 0
        
        scorecards_added = 0
        
        for innings in scorecard_data['scorecard']:
            innings_id = innings.get('inningsid', 1)
            
            # Store batting data
            batsmen = innings.get('batsman', [])
            for batsman in batsmen:
                player_id = batsman.get('id')
                if not player_id:
                    continue
                
                # Ensure player exists
                self.cursor.execute("""
                    INSERT IGNORE INTO players (player_id, name, country, role, batting_style, bowling_style)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    player_id,
                    batsman.get('name', f'Player {player_id}'),
                    'Unknown',
                    'Batsman',
                    'Right-handed',
                    'Right-arm medium'
                ))
                
                # Store scorecard data
                try:
                    self.cursor.execute("""
                        INSERT INTO match_scorecards (
                            match_id, player_id, innings_id, runs, balls, fours, sixes, strike_rate,
                            batting_position, out_description, is_captain, is_keeper
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        runs = VALUES(runs),
                        balls = VALUES(balls),
                        fours = VALUES(fours),
                        sixes = VALUES(sixes),
                        strike_rate = VALUES(strike_rate),
                        batting_position = VALUES(batting_position),
                        out_description = VALUES(out_description),
                        is_captain = VALUES(is_captain),
                        is_keeper = VALUES(is_keeper)
                    """, (
                        match_id,
                        player_id,
                        innings_id,
                        batsman.get('runs', 0),
                        batsman.get('balls', 0),
                        batsman.get('fours', 0),
                        batsman.get('sixes', 0),
                        batsman.get('strkrate', 0.0),
                        batsman.get('battingPosition', 0),
                        batsman.get('outdec', ''),
                        batsman.get('iscaptain', False),
                        batsman.get('iskeeper', False)
                    ))
                    scorecards_added += 1
                except Exception as e:
                    print(f"      Error storing batsman {player_id}: {e}")
            
            # Note: Bowling data not stored as match_scorecards table doesn't support it
        
        return scorecards_added

    def populate_cricket_world_cups(self, years=[2011, 2015, 2019, 2023]):
        """Populate Cricket World Cup data for Query 22"""
        print(f"\nPOPULATING CRICKET WORLD CUP DATA FOR QUERY 22")
        print("=" * 60)
        print(f"Target: Main Cricket World Cups from {years}")
        print(f"Estimated API calls: ~{len(years) * 50}")
        
        # Target only the main Cricket World Cups (not qualifiers)
        target_world_cups = [
            'ICC World Cup 2011',
            'ICC Cricket World Cup 2015', 
            'ICC Cricket World Cup 2019',
            'ICC Cricket World Cup 2023'
        ]
        
        total_matches_processed = 0
        total_scorecards_added = 0
        
        for year in years:
            print(f"\nProcessing year {year}...")
            
            # Get series for this year
            series_data = self.make_api_call("/series/v1/archives/international", {"year": year})
            if not series_data or 'seriesMapProto' not in series_data:
                print(f"No series data for {year}")
                continue
            
            # Find series for this year
            series_list = []
            for year_data in series_data['seriesMapProto']:
                if year_data.get('date') == str(year):
                    series_list = year_data.get('series', [])
                    break
            
            print(f"Found {len(series_list)} series for {year}")
            
            # Find the main Cricket World Cup for this year
            main_world_cup = None
            for series in series_list:
                series_name = series.get('name', '')
                if any(target in series_name for target in target_world_cups):
                    main_world_cup = series
                    print(f"  Found main Cricket World Cup: {series_name}")
                    break
            
            if not main_world_cup:
                print(f"No main Cricket World Cup found for {year}")
                continue
            
            # Process the main Cricket World Cup
            series_id = main_world_cup.get('id')
            series_name = main_world_cup.get('name', 'Unknown')
            
            print(f"Processing main Cricket World Cup: {series_name}")
            
            # Store series data
            self._store_series_data(main_world_cup, year)
            
            # Get matches for this World Cup
            matches_data = self.make_api_call(f"/series/v1/{series_id}")
            if not matches_data:
                print("No matches data for this World Cup")
                continue
            
            # Extract matches from the correct structure
            matches = []
            if 'matchDetails' in matches_data:
                for match_detail in matches_data['matchDetails']:
                    if 'matchDetailsMap' in match_detail:
                        match_list = match_detail['matchDetailsMap'].get('match', [])
                        matches.extend(match_list)
            
            print(f"Found {len(matches)} matches in this Cricket World Cup")
            
            matches_processed_this_year = 0
            
            # Process all matches in the World Cup (they're all important for team head-to-head)
            for match in matches:
                if self.api_calls_made >= 180:  # Leave buffer
                    print("Approaching API limit, stopping early")
                    break
                
                match_info = match.get('matchInfo', {})
                match_id = match_info.get('matchId')
                
                if not match_id:
                    continue
                
                print(f"  Processing: {match_info.get('matchDesc', 'Unknown')}")
                
                # Store match data
                if self._store_match_data(match, series_id):
                    # Get and store scorecard data
                    scorecard_data = self.make_api_call(f"/mcenter/v1/{match_id}/scard")
                    if scorecard_data and 'scorecard' in scorecard_data:
                        scorecards_added = self._store_scorecard_data(scorecard_data, match_id)
                        total_scorecards_added += scorecards_added
                        print(f"    Added {scorecards_added} scorecard records")
                    else:
                        print(f"    No scorecard data available")
                    
                    matches_processed_this_year += 1
                    total_matches_processed += 1
                    
                    # Commit after each match
                    self.connection.commit()
            
            print(f"Year {year}: Processed {matches_processed_this_year} matches")
            
            if self.api_calls_made >= 180:
                print("API limit reached, stopping early")
                break
        
        print(f"\nCRICKET WORLD CUP POPULATION COMPLETE!")
        print(f"Total matches processed: {total_matches_processed}")
        print(f"Total scorecard records added: {total_scorecards_added}")
        print(f"Total API calls made: {self.api_calls_made}")
        print(f"API calls remaining: {200 - self.api_calls_made}")
        
        return {
            'matches_processed': total_matches_processed,
            'scorecards_added': total_scorecards_added,
            'api_calls_made': self.api_calls_made
        }

    def populate_recent_world_cups(self, years=[2022, 2023, 2024]):
        """Populate recent World Cup data (2022, 2023, 2024) for Query 22"""
        print(f"\nPOPULATING RECENT WORLD CUP DATA FOR QUERY 22")
        print("=" * 60)
        print(f"Target: Recent World Cups from {years}")
        print(f"Estimated API calls: ~{len(years) * 50}")
        
        # Target recent World Cups
        target_world_cups = {
            2022: ['ICC Mens T20 World Cup 2022'],
            2023: ['ICC Cricket World Cup 2023'],
            2024: ['ICC Mens T20 World Cup 2024']
        }
        
        total_matches_processed = 0
        total_scorecards_added = 0
        
        for year in years:
            print(f"\nProcessing year {year}...")
            
            # Get series for this year
            series_data = self.make_api_call("/series/v1/archives/international", {"year": year})
            if not series_data or 'seriesMapProto' not in series_data:
                print(f"No series data for {year}")
                continue
            
            # Find series for this year
            series_list = []
            for year_data in series_data['seriesMapProto']:
                if year_data.get('date') == str(year):
                    series_list = year_data.get('series', [])
                    break
            
            print(f"Found {len(series_list)} series for {year}")
            
            # Find the target World Cup for this year
            target_series = None
            for series in series_list:
                series_name = series.get('name', '')
                if any(target in series_name for target in target_world_cups[year]):
                    target_series = series
                    print(f"  Found target World Cup: {series_name}")
                    break
            
            if not target_series:
                print(f"No target World Cup found for {year}")
                continue
            
            # Process the target World Cup
            series_id = target_series.get('id')
            series_name = target_series.get('name', 'Unknown')
            
            print(f"Processing World Cup: {series_name}")
            
            # Store series data
            self._store_series_data(target_series, year)
            
            # Get matches for this World Cup
            matches_data = self.make_api_call(f"/series/v1/{series_id}")
            if not matches_data:
                print("No matches data for this World Cup")
                continue
            
            # Extract matches from the correct structure
            matches = []
            if 'matchDetails' in matches_data:
                for match_detail in matches_data['matchDetails']:
                    if 'matchDetailsMap' in match_detail:
                        match_list = match_detail['matchDetailsMap'].get('match', [])
                        matches.extend(match_list)
            
            print(f"Found {len(matches)} matches in this World Cup")
            
            matches_processed_this_year = 0
            
            # Process all matches in the World Cup
            for match in matches:
                if self.api_calls_made >= 180:  # Leave buffer
                    print("Approaching API limit, stopping early")
                    break
                
                match_info = match.get('matchInfo', {})
                match_id = match_info.get('matchId')
                
                if not match_id:
                    continue
                
                print(f"  Processing: {match_info.get('matchDesc', 'Unknown')}")
                
                # Store match data
                if self._store_match_data(match, series_id):
                    # Get and store scorecard data
                    scorecard_data = self.make_api_call(f"/mcenter/v1/{match_id}/scard")
                    if scorecard_data and 'scorecard' in scorecard_data:
                        scorecards_added = self._store_scorecard_data(scorecard_data, match_id)
                        total_scorecards_added += scorecards_added
                        print(f"    Added {scorecards_added} scorecard records")
                    else:
                        print(f"    No scorecard data available")
                    
                    matches_processed_this_year += 1
                    total_matches_processed += 1
                    
                    # Commit after each match
                    self.connection.commit()
            
            print(f"Year {year}: Processed {matches_processed_this_year} matches")
            
            if self.api_calls_made >= 180:
                print("API limit reached, stopping early")
                break
        
        print(f"\nRECENT WORLD CUP POPULATION COMPLETE!")
        print(f"Total matches processed: {total_matches_processed}")
        print(f"Total scorecard records added: {total_scorecards_added}")
        print(f"Total API calls made: {self.api_calls_made}")
        print(f"API calls remaining: {200 - self.api_calls_made}")
        
        return {
            'matches_processed': total_matches_processed,
            'scorecards_added': total_scorecards_added,
            'api_calls_made': self.api_calls_made
        }

def main():
    client = ComprehensiveAPIClient()
    try:
        client.connect_database()
        results = client.run_comprehensive_population()
        
        print(f"\nESTIMATED API COST:")
        print(f"Total API calls: {results['api_calls']}")
        print(f"Estimated cost: ${results['api_calls'] * 0.01:.2f} (assuming $0.01 per call)")
        
    except Exception as e:
        print(f"Failed to populate database: {str(e)}")

if __name__ == "__main__":
    main()
