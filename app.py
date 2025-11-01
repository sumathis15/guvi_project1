import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="Cricket Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:8000"

def make_api_request(endpoint, method="GET", data=None):
    """Make API request to FastAPI backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        else:
            st.error(f"Unsupported HTTP method: {method}")
            return None
            
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return None

def fetch_scorecard_data(match_id):
    """Fetch scorecard data for a specific match"""
    try:
        # Use the Cricbuzz API directly for scorecard data
        from config import RAPIDAPI_KEY
        
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
        }
        
        url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/scard"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch scorecard: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error fetching scorecard: {str(e)}")
        return None

def display_scorecard(scorecard_data, match_info):
    """Display comprehensive scorecard data"""
    if not scorecard_data or 'scorecard' not in scorecard_data:
        st.error("❌ No scorecard data available for this match")
        return
    
    st.markdown("---")
    st.markdown("### 📊 Match Scorecard")
    
    # Match header
    team1_name = match_info.get('team1', {}).get('name', 'Team 1')
    team2_name = match_info.get('team2', {}).get('name', 'Team 2')
    match_desc = match_info.get('matchDesc', 'Match')
    
    st.markdown(f"#### 🏏 {team1_name} vs {team2_name} - {match_desc}")
    
    scorecard = scorecard_data['scorecard']
    
    # Display each innings
    for innings_idx, innings in enumerate(scorecard):
        innings_id = innings.get('inningsid', innings_idx + 1)
        
        st.markdown(f"### 🏏 Innings {innings_id}")
        
        # Determine team names based on innings number
        # For most cricket matches: Innings 1 = Team 1 bats, Innings 2 = Team 2 bats
        if innings_idx == 0:  # First innings
            batting_team_name = team1_name
            bowling_team_name = team2_name
        else:  # Second innings (or more)
            batting_team_name = team2_name
            bowling_team_name = team1_name
        
        # Try to get team names from scorecard data if available
        if 'batTeamName' in innings and innings['batTeamName']:
            batting_team_name = innings['batTeamName']
        if 'bowlTeamName' in innings and innings['bowlTeamName']:
            bowling_team_name = innings['bowlTeamName']
        
        # Batting details
        if 'batsman' in innings and innings['batsman']:
            st.markdown(f"#### 🏏 {batting_team_name} Batting")
            
            # Create batting table
            batting_data = []
            for batsman in innings['batsman']:
                batting_data.append({
                    'Player': batsman.get('name', 'N/A'),
                    'Runs': batsman.get('runs', 0),
                    'Balls': batsman.get('balls', 0),
                    '4s': batsman.get('fours', 0),
                    '6s': batsman.get('sixes', 0),
                    'SR': batsman.get('strkrate', '0.0'),
                    'Out': batsman.get('outdec', 'Not Out') if batsman.get('outdec') else 'Not Out',
                    'Captain': '👑' if batsman.get('iscaptain') else '',
                    'Keeper': '🥅' if batsman.get('iskeeper') else ''
                })
            
            if batting_data:
                batting_df = pd.DataFrame(batting_data)
                st.dataframe(batting_df, use_container_width=True)
        
        # Bowling details
        if 'bowler' in innings and innings['bowler']:
            st.markdown(f"#### 🎯 {bowling_team_name} Bowling")
            
            # Create bowling table
            bowling_data = []
            for bowler in innings['bowler']:
                bowling_data.append({
                    'Player': bowler.get('name', 'N/A'),
                    'Overs': bowler.get('overs', '0.0'),
                    'Maidens': bowler.get('maidens', 0),
                    'Runs': bowler.get('runs', 0),
                    'Wickets': bowler.get('wickets', 0),
                    'Economy': bowler.get('economy', '0.0'),
                    'Captain': '👑' if bowler.get('iscaptain') else '',
                    'Keeper': '🥅' if bowler.get('iskeeper') else ''
                })
            
            if bowling_data:
                bowling_df = pd.DataFrame(bowling_data)
                st.dataframe(bowling_df, use_container_width=True)
        
        st.markdown("---")
    
    # Match summary
    st.markdown("### 📈 Match Summary")
    
    # Try to get match score from the original match data
    if 'matchScore' in match_info:
        match_score = match_info['matchScore']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'team1Score' in match_score:
                team1_score = match_score['team1Score']
                st.markdown(f"#### {team1_name}")
                for innings_key, innings_data in team1_score.items():
                    if isinstance(innings_data, dict):
                        runs = innings_data.get('runs', 0)
                        wickets = innings_data.get('wickets', 0)
                        overs = innings_data.get('overs', '0.0')
                        st.write(f"**{runs}/{wickets} ({overs} overs)**")
        
        with col2:
            if 'team2Score' in match_score:
                team2_score = match_score['team2Score']
                st.markdown(f"#### {team2_name}")
                for innings_key, innings_data in team2_score.items():
                    if isinstance(innings_data, dict):
                        runs = innings_data.get('runs', 0)
                        wickets = innings_data.get('wickets', 0)
                        overs = innings_data.get('overs', '0.0')
                        st.write(f"**{runs}/{wickets} ({overs} overs)**")
    
    # Close button
    if st.button("❌ Close Scorecard", key=f"close_scorecard_{match_info.get('matchId', '')}"):
        # Clear the scorecard display state
        for key in list(st.session_state.keys()):
            if key.startswith('show_scorecard_'):
                st.session_state[key] = False
        st.rerun()

def test_api_connection():
    """Test API connection"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"API returned status code: {response.status_code}"
    except requests.RequestException as e:
        return False, f"Connection failed: {str(e)}"

# Main app
def main():
    st.title("🏏 Cricbuzz LiveStats")
    st.markdown("---")
    
    # Sidebar navigation with buttons
    st.sidebar.selectbox("🏏 Navigation", ["Home", "Matches", "Player Stats", "SQL Analytics", "CRUD Operations", "Database Viewer"])
    
    # Navigation buttons
    if st.sidebar.button("🏠 Home", width='stretch'):
        st.session_state.page = "Home"
    if st.sidebar.button("🏏 Matches", width='stretch'):
        st.session_state.page = "Matches"
    if st.sidebar.button("👤 Player Stats", width='stretch'):
        st.session_state.page = "Player Stats"
    if st.sidebar.button("📊 SQL Analytics", width='stretch'):
        st.session_state.page = "SQL Analytics"
    if st.sidebar.button("🔧 CRUD Operations", width='stretch'):
        st.session_state.page = "CRUD Operations"
    if st.sidebar.button("🗄️ Database Viewer", width='stretch'):
        st.session_state.page = "Database Viewer"
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "Home"
    
    page = st.session_state.page
    
    st.sidebar.markdown("---")    
    # Route to different pages
    if page == "Home":
        show_home_page()
    elif page == "Matches":
        show_matches_page()
    elif page == "Player Stats":
        show_player_stats_page()
    elif page == "SQL Analytics":
        show_sql_analytics_from_new_app()
    elif page == "CRUD Operations":
        show_crud_page()
    elif page == "Database Viewer":
        show_database_viewer_page()

def show_home_page():
    """Home page with project description and navigation"""
    
    # Project Description
    st.subheader("📋 Project Description")
    st.write("""
    **Cricbuzz LiveStats** is a comprehensive cricket statistics application that provides real-time cricket data, 
    player statistics, and advanced analytics. The application fetches live cricket data from Cricbuzz API 
    and provides detailed insights into matches, players, and series.
    """)
    
    # Tools Used
    st.subheader("🛠️ Tools & Technologies Used")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("""
        **Backend:**
        - FastAPI (Python web framework)
        - MySQL Database
        - mysql-connector-python
        - RapidAPI (Cricbuzz API)
        """)
    
    with col2:
        st.write("""
        **Frontend:**
        - Streamlit (Multi-page web app)
        - Pandas (Data manipulation)
        - Requests (API calls)
        """)
    
    # Instructions
    st.subheader("📖 Instructions")
    st.info("""
    **How to Use:**
    1. **Navigation**: Use the sidebar to switch between different pages
    2. **API Calls**: All data fetching is on-demand (click buttons to fetch)
    3. **Real-time**: Live match data is fetched when you request it
    4. **No Fallbacks**: If no data is available, an error will be shown
    """)
    
    # Available Pages
    st.subheader("📄 Available Pages")
    st.write("""
    - **🏏 Matches**: View live, upcoming, and recent matches with scorecard integration
    - **👤 Player Stats**: Browse top players with comprehensive batting/bowling statistics  
    - **📊 SQL Analytics**: Run 25 predefined analytics queries across 3 difficulty levels
    - **🔧 CRUD Operations**: Manage players in database with visual SQL query builder
    - **🗄️ Database Viewer**: View database tables and execute custom SQL queries
    """)
    
    # Project Structure
    st.subheader("📁 Project Structure")
    st.code("""
    cric/
    ├── app.py                      # Streamlit frontend application
    ├── main.py                     # FastAPI backend server
    ├── config.py                   # Database and API configuration
    ├── sql_queries.py              # 25 predefined SQL queries
    ├── api_client.py               # Data population and API interactions
    ├── api_endpoint_format.md      # API documentation and examples
    ├── sql_questions.md            # SQL query questions reference
    ├── README.md                   # Basic project documentation
    ├── requirements.txt            # Python dependencies
    ├── start_app.bat               # Windows batch start script
    ├── start_app.ps1               # PowerShell start script
    ├── export_database.py          # Database export utility
    ├── import_database.py          # Database import utility
    └── cricket_database_backup_*.sql  # Database backup files
    """)
    
    # Developer Credit
    st.markdown("---")
    st.markdown("""
    <style>
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .credit-container {
            animation: fadeInUp 0.6s ease-out;
        }
        .linkedin-btn {
            position: relative;
            overflow: hidden;
        }
        .linkedin-btn::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        .linkedin-btn:hover::before {
            width: 300px;
            height: 300px;
        }
    </style>
    <div class="credit-container" style='
        text-align: center; 
        padding: 40px 30px; 
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 50%, #0077b5 100%); 
        border-radius: 15px; 
        margin-top: 40px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    '>
        <div style='
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 50px 50px;
            animation: rotate 20s linear infinite;
        '></div>
        <div style='position: relative; z-index: 1;'>
            <p style='
                font-size: 25px; 
                color: #ffffff; 
                margin-bottom: 15px; 
                font-weight: 500;
                text-shadow: 0 2px 10px rgba(0,0,0,0.2);
            '>
                Developed and maintained by <strong style='color: #ffffff; font-weight: 600;'>Sumathi S</strong>
            </p>
            <div style='display: inline-block;'>
                <a href='https://www.linkedin.com/in/sumathisaravanan/' 
                   target='_blank' 
                   class="linkedin-btn"
                   style='
                        display: inline-flex; 
                        align-items: center; 
                        gap: 10px; 
                        text-decoration: none; 
                        color: #0077b5; 
                        font-weight: 600; 
                        font-size: 16px;
                        padding: 14px 28px; 
                        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                        border: none;
                        border-radius: 50px;
                        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                        box-shadow: 0 4px 15px rgba(0,119,181,0.25), 
                                    0 2px 5px rgba(0,0,0,0.1),
                                    inset 0 1px 0 rgba(255,255,255,0.9);
                        position: relative;
                        overflow: hidden;
                    '
                   onmouseover="
                        this.style.transform='translateY(-3px) scale(1.05)';
                        this.style.boxShadow='0 8px 25px rgba(0,119,181,0.4), 0 4px 10px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.9)';
                        this.style.background='linear-gradient(135deg, #0077b5 0%, #005885 100%)';
                        this.style.color='#ffffff';
                   "
                   onmouseout="
                        this.style.transform='translateY(0) scale(1)';
                        this.style.boxShadow='0 4px 15px rgba(0,119,181,0.25), 0 2px 5px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.9)';
                        this.style.background='linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)';
                        this.style.color='#0077b5';
                   ">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg" style='filter: drop-shadow(0 1px 2px rgba(0,0,0,0.1));'>
                        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                    </svg>
                    <span style='font-weight: 600;'>Connect on LinkedIn</span>
                </a>
            </div>
        </div>
    </div>
    <style>
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    </style>
    """, unsafe_allow_html=True)
    

def show_matches_page():
    """Matches page with dropdown for match types"""
    st.header("🏏 Matches")
    
    # Match type selection with better styling
    st.markdown("### 📊 Select Match Type")
    match_type = st.selectbox(
        "Choose the type of matches you want to view:",
        ["Live", "Upcoming", "Recent"],
        help="Live: Matches happening now | Upcoming: All future matches | Recent: Recently finished matches"
    )

    # Initialize session state for current match type
    current_matches_key = f'current_{match_type.lower()}_matches'

    if st.button(f"Fetch {match_type} Matches", type="primary"):
        with st.spinner(f"Fetching {match_type.lower()} matches..."):
            if match_type == "Live":
                data = make_api_request("/api/live_matches")
            elif match_type == "Recent":
                data = make_api_request("/api/recent_matches")
            else:  # Upcoming
                data = make_api_request("/api/upcoming_matches")

            if data and 'matches' in data:
                matches = data['matches']
                # Store matches in session state
                st.session_state[current_matches_key] = matches
                st.rerun()  # Rerun to display the matches
            else:
                st.error(f"❌ Failed to fetch {match_type.lower()} matches")
                    
    # Display matches from session state
    if current_matches_key in st.session_state:
        matches = st.session_state[current_matches_key]
        
        if len(matches) > 0:
            st.markdown(f"### ✅ Found {len(matches)} {match_type.lower()} matches")
            st.markdown("---")
            
            # Sort matches based on match type
            if match_type == "Recent":
                # For recent matches, sort by end date (latest first)
                def get_end_date(match):
                    end_date = match.get('endDate', '')
                    if end_date:
                        try:
                            return int(end_date)
                        except:
                            return 0
                    return 0
                
                matches.sort(key=get_end_date, reverse=True)  # Latest first
            else:
                # For live and upcoming matches, sort by start date (earliest first)
                def get_start_date(match):
                    start_date = match.get('startDate', '')
                    if start_date:
                        try:
                            return int(start_date)
                        except:
                            return 0
                    return 0
                
                matches.sort(key=get_start_date)
            
            # Display all matches in chronological order
            for i, match in enumerate(matches):
                team1_name = match.get('team1', {}).get('name', 'N/A')
                team2_name = match.get('team2', {}).get('name', 'N/A')
                
                with st.expander(f"🏏 {team1_name} vs {team2_name} - {match.get('matchDesc', 'N/A')}", expanded=False):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("#### 🏏 Match Details")
                        st.write(f"**Series:** {match.get('seriesName', 'N/A')}")
                        st.write(f"**Description:** {match.get('matchDesc', 'N/A')}")
                        st.write(f"**Format:** {match.get('matchFormat', 'N/A')}")
                        st.write(f"**Status:** {match.get('status', 'N/A')}")
                        st.write(f"**State:** {match.get('state', 'N/A')}")
                        
                        # Add date/time information based on match type
                        if match_type == "Recent":
                            # For recent matches, show when it ended
                            end_date = match.get('endDate', '')
                            if end_date:
                                try:
                                    from datetime import datetime
                                    end_timestamp = int(end_date) / 1000
                                    end_datetime = datetime.fromtimestamp(end_timestamp)
                                    st.write(f"**Match Ended At:** {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                                except:
                                    st.write(f"**Match Ended At:** {end_date}")
                            else:
                                st.write("**Match Ended At:** N/A")
                        elif match_type == "Upcoming":
                            # For upcoming matches, show when it starts
                            start_date = match.get('startDate', '')
                            if start_date:
                                try:
                                    from datetime import datetime
                                    start_timestamp = int(start_date) / 1000
                                    start_datetime = datetime.fromtimestamp(start_timestamp)
                                    st.write(f"**Match Starts At:** {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                                except:
                                    st.write(f"**Match Starts At:** {start_date}")
                            else:
                                st.write("**Match Starts At:** N/A")
                        elif match_type == "Live":
                            # For live matches, show when it started
                            start_date = match.get('startDate', '')
                            if start_date:
                                try:
                                    from datetime import datetime
                                    start_timestamp = int(start_date) / 1000
                                    start_datetime = datetime.fromtimestamp(start_timestamp)
                                    st.write(f"**Match Started At:** {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                                except:
                                    st.write(f"**Match Started At:** {start_date}")
                            else:
                                st.write("**Match Started At:** N/A")

                    with col2:
                        st.markdown("#### 🏟️ Venue Information")
                        st.write(f"**Venue:** {match.get('venue', {}).get('name', 'N/A')}")
                        st.write(f"**City:** {match.get('venue', {}).get('city', 'N/A')}")

                        st.markdown("#### 👥 Teams")
                        st.write(f"**Team 1:** {match.get('team1', {}).get('name', 'N/A')} ({match.get('team1', {}).get('shortName', 'N/A')})")
                        st.write(f"**Team 2:** {match.get('team2', {}).get('name', 'N/A')} ({match.get('team2', {}).get('shortName', 'N/A')})")
                    
                    # Add View Scorecard button for Live and Recent matches
                    if match_type in ["Live", "Recent"]:
                        st.markdown("---")
                        match_id = match.get('matchId', '')
                        if match_id:
                            if st.button(f"📊 View Scorecard", key=f"scorecard_{match_id}_{i}", type="secondary"):
                                st.session_state[f'show_scorecard_{match_id}'] = True
                                st.session_state[f'selected_match_{match_id}'] = match
                                st.rerun()
                
                # Check if scorecard should be displayed for this match
                match_id = match.get('matchId', '')
                if match_id and st.session_state.get(f'show_scorecard_{match_id}', False):
                    selected_match = st.session_state.get(f'selected_match_{match_id}')
                    if selected_match:
                        with st.spinner("Fetching scorecard data..."):
                            scorecard_data = fetch_scorecard_data(match_id)
                            if scorecard_data:
                                display_scorecard(scorecard_data, selected_match)
                            else:
                                st.error("❌ Failed to fetch scorecard data")
        else:
            st.error(f"❌ No {match_type.lower()} matches found")

def show_player_stats_page():
    """Enhanced Player Statistics page with search and detailed stats"""
    st.header("🏏 Cricket Player Statistics")
    st.markdown("---")
    
    # Initialize session state
    if 'selected_player' not in st.session_state:
        st.session_state.selected_player = None
    if 'player_tab' not in st.session_state:
        st.session_state.player_tab = "Profile"
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    
    # Search Section with Autocomplete
    st.markdown("### 🔍 Search for a Player")
    
    # Search input with autocomplete
    col1, col2 = st.columns([5, 1])
    
    with col1:
        # Use dynamic key to clear input when needed
        input_key = f"search_input_{st.session_state.get('clear_search', 0)}"
        search_query = st.text_input(
            "Enter player name:",
            placeholder="e.g., Virat, Kohli, KL Rahul, MS Dhoni",
            help="Start typing and press enter to see player suggestions",
            key=input_key
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing to align with input
        if st.button("🔄 Clear", help="Clear search and results", width='stretch'):
            st.session_state.search_results = []
            st.session_state.search_query = ""
            st.session_state.selected_player = None
            # Clear the input field by using a key that changes
            st.session_state.clear_search = st.session_state.get('clear_search', 0) + 1
            st.rerun()
    
    # Auto-search as user types (with debouncing)
    if search_query and len(search_query) >= 2:
        if search_query != st.session_state.search_query:
            st.session_state.search_query = search_query
            # Show loading indicator
            with st.spinner("🔍 Searching players..."):
                search_data = make_api_request(f"/api/players/search?query={search_query}&limit=10")
                
                if search_data and 'players' in search_data:
                    st.session_state.search_results = search_data['players']
                else:
                    st.session_state.search_results = []
    
    # Display autocomplete dropdown (only when no player is selected)
    if st.session_state.search_results and len(st.session_state.search_results) > 0 and not st.session_state.selected_player:
        st.markdown("#### 📋 Select a Player")
        
        # Create a more user-friendly display
        for i, player in enumerate(st.session_state.search_results):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.write(f"**{player.get('name', 'N/A')}**")
            
            with col2:
                if st.button(f"Select", key=f"select_{i}", type="primary"):
                    st.session_state.selected_player = player
                    st.session_state.search_results = []  # Clear search results
                    st.rerun()
    
    # Show message if no results (only when no player is selected)
    elif search_query and len(search_query) >= 2 and len(st.session_state.search_results) == 0 and not st.session_state.selected_player:
        st.error("No players found for your search")
    
    # Display selected player details
    if st.session_state.selected_player:
        player = st.session_state.selected_player
        player_id = player.get('id')  # Changed from 'player_id' to 'id'
        
        # Check if player ID exists
        if not player_id:
            st.error("Player ID not found in search results")
            return
        
        # Player Header with Back button
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"### 🏏 {player.get('name', 'Player')} - Player Profile")
        with col2:
            if st.button("← Back to Search", help="Go back to search"):
                st.session_state.selected_player = None
                st.session_state.search_results = []
                st.session_state.search_query = ""
                st.session_state.clear_search = st.session_state.get('clear_search', 0) + 1
                st.rerun()
        
        
        # Navigation Tabs
        tab1, tab2, tab3 = st.tabs(["👤 Profile", "🏏 Batting Stats", "⚾ Bowling Stats"])
        
        with tab1:
            if player_id:
                show_player_profile(player_id)
            else:
                st.error("Player ID not found")
        
        with tab2:
            if player_id:
                show_player_batting_stats(player_id)
            else:
                st.error("Player ID not found")
        
        with tab3:
            if player_id:
                show_player_bowling_stats(player_id)
            else:
                st.error("Player ID not found")

def show_player_profile(player_id):
    """Display player profile information"""
    with st.spinner("Loading player profile..."):
        # Get player info
        info_data = make_api_request(f"/api/players/{player_id}/info")
        
        if info_data and 'player_info' in info_data:
            player_info = info_data['player_info']
            
            st.markdown("#### 📋 Personal Information")
            
            # Create three equal columns for information
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                st.markdown("##### 🏏 Cricket Details")
                st.markdown(f"**Role:** {player_info.get('role', 'N/A')}")
                st.markdown(f"**Batting:** {player_info.get('bat', 'N/A')}")
                st.markdown(f"**Bowling:** {player_info.get('bowl', 'N/A')}")
                st.markdown(f"**International Team:** {player_info.get('intlTeam', 'N/A')}")
            
            with col2:
                st.markdown("##### 👤 Personal Details")
                dob = player_info.get('DoB', 'N/A')
                st.markdown(f"**Date of Birth:** {dob}")
                st.markdown(f"**Birth Place:** {player_info.get('birthPlace', 'N/A')}")
                st.markdown(f"**Height:** {player_info.get('height', 'N/A')}")
                st.markdown(f"**Nickname:** {player_info.get('nickName', 'N/A')}")
            
            with col3:
                st.markdown("##### 🏆 Teams Played For")
                teams = player_info.get('teams', 'N/A')
                if teams != 'N/A':
                    # Split the teams string and display them
                    team_list = [team.strip() for team in teams.split(',')]
                    for team in team_list[:5]:  # Show first 5 teams
                        st.markdown(f"• {team}")
                    
                    if len(team_list) > 5:
                        with st.expander(f"Show all {len(team_list)} teams"):
                            for team in team_list:
                                st.markdown(f"• {team}")
                else:
                    st.markdown("No team information available")
            
            # Bio section
            bio = player_info.get('bio', '')
            if bio:
                st.markdown("---")
                st.markdown("#### 📖 Biography")
                # Clean up HTML tags for better display
                import re
                clean_bio = re.sub(r'<[^>]+>', '', bio)
                if len(clean_bio) > 500:
                    st.markdown(clean_bio[:500] + "...")
                    with st.expander("Read full biography"):
                        st.markdown(clean_bio)
                else:
                    st.markdown(clean_bio)
        else:
            st.error("Failed to load player profile")

def show_player_batting_stats(player_id):
    """Display player batting statistics"""
    with st.spinner("Loading batting statistics..."):
        batting_data = make_api_request(f"/api/players/{player_id}/batting")
        
        if batting_data and 'batting_stats' in batting_data:
            batting_stats = batting_data['batting_stats']
            
            # Handle the actual data format from API
            if isinstance(batting_stats, dict) and 'headers' in batting_stats and 'values' in batting_stats:
                headers = batting_stats.get('headers', [])
                values = batting_stats.get('values', [])
                
                # First Image Component: Batting Overview (4 columns)
                st.markdown("### ⚡ Batting Career Statistics")
                st.markdown("#### 🔗 📊 Batting Overview")
                
                # Create 4 columns for Test, ODI, T20, IPL
                col1, col2, col3, col4 = st.columns(4)
                formats = ['Test', 'ODI', 'T20', 'IPL']
                columns = [col1, col2, col3, col4]
                
                # Key stats for overview: Matches, Runs, Average, SR
                overview_stats = ['Matches', 'Runs', 'Average', 'SR']
                
                for i, (format_name, col) in enumerate(zip(formats, columns)):
                    with col:
                        st.markdown(f"**{format_name}**")
                        for stat_name in overview_stats:
                            # Find the stat in values
                            stat_row = next((row for row in values if row.get('values', [{}])[0] == stat_name), None)
                            if stat_row:
                                stat_values = stat_row.get('values', [])
                                if i + 1 < len(stat_values):
                                    value = stat_values[i + 1]
                                    st.markdown(f"**{stat_name}**")
                                    st.markdown(f"<span style='font-size: 24px; font-weight: bold;'>{value}</span>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"**{stat_name}**")
                                    st.markdown(f"<span style='font-size: 24px; font-weight: bold;'>0</span>", unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Second Image Component: Detailed Batting Statistics Table
                st.markdown("#### 📈 Detailed Batting Statistics")
                
                # Create detailed table with all statistics
                table_data = []
                column_names = ['Statistic'] + headers[1:]  # ['Statistic', 'Test', 'ODI', 'T20', 'IPL']
                
                for row in values:
                    if isinstance(row, dict) and 'values' in row:
                        stat_values = row.get('values', [])
                        if len(stat_values) > 0:
                            stat_name = stat_values[0]
                            row_data = {'Statistic': stat_name}
                            for i, format_name in enumerate(headers[1:], 1):
                                if i < len(stat_values):
                                    row_data[format_name] = stat_values[i]
                                else:
                                    row_data[format_name] = '0'
                            table_data.append(row_data)
                
                if table_data:
                    df = pd.DataFrame(table_data, columns=column_names)
                    st.dataframe(df, width='stretch', hide_index=True)
                else:
                    st.info("No detailed batting statistics available")
            else:
                # Handle case where batting_stats is not in expected format
                st.info("Batting statistics data format not recognized")
                st.write("Raw data:", batting_stats)
        else:
            st.error("Failed to load batting statistics")
            if batting_data:
                st.write("API Response:", batting_data)

def show_player_bowling_stats(player_id):
    """Display player bowling statistics"""
    with st.spinner("Loading bowling statistics..."):
        bowling_data = make_api_request(f"/api/players/{player_id}/bowling")
        
        if bowling_data and 'bowling_stats' in bowling_data:
            bowling_stats = bowling_data['bowling_stats']
            
            # Handle the actual data format from API
            if isinstance(bowling_stats, dict) and 'headers' in bowling_stats and 'values' in bowling_stats:
                headers = bowling_stats.get('headers', [])
                values = bowling_stats.get('values', [])
                
                # Third Image Component: Bowling Overview (4 columns)
                st.markdown("### ⚡ Bowling Career Statistics")
                st.markdown("#### 🔗 📊 Bowling Overview")
                
                # Create 4 columns for Test, ODI, T20, IPL
                col1, col2, col3, col4 = st.columns(4)
                formats = ['Test', 'ODI', 'T20', 'IPL']
                columns = [col1, col2, col3, col4]
                
                # Key stats for overview: Matches, Wickets, Avg, Eco
                overview_stats = ['Matches', 'Wickets', 'Avg', 'Eco']
                
                for i, (format_name, col) in enumerate(zip(formats, columns)):
                    with col:
                        st.markdown(f"**{format_name}**")
                        for stat_name in overview_stats:
                            # Find the stat in values
                            stat_row = next((row for row in values if row.get('values', [{}])[0] == stat_name), None)
                            if stat_row:
                                stat_values = stat_row.get('values', [])
                                if i + 1 < len(stat_values):
                                    value = stat_values[i + 1]
                                    st.markdown(f"**{stat_name}**")
                                    st.markdown(f"<span style='font-size: 24px; font-weight: bold;'>{value}</span>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"**{stat_name}**")
                                    st.markdown(f"<span style='font-size: 24px; font-weight: bold;'>0</span>", unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Fourth Image Component: Detailed Bowling Statistics Table
                st.markdown("#### 📈 Detailed Bowling Statistics")
                
                # Create detailed table with all statistics
                table_data = []
                column_names = ['Statistic'] + headers[1:]  # ['Statistic', 'Test', 'ODI', 'T20', 'IPL']
                
                for row in values:
                    if isinstance(row, dict) and 'values' in row:
                        stat_values = row.get('values', [])
                        if len(stat_values) > 0:
                            stat_name = stat_values[0]
                            row_data = {'Statistic': stat_name}
                            for i, format_name in enumerate(headers[1:], 1):
                                if i < len(stat_values):
                                    row_data[format_name] = stat_values[i]
                                else:
                                    row_data[format_name] = '0'
                            table_data.append(row_data)
                
                if table_data:
                    df = pd.DataFrame(table_data, columns=column_names)
                    st.dataframe(df, width='stretch', hide_index=True)
                else:
                    st.info("No detailed bowling statistics available")
            else:
                # Handle case where bowling_stats is not in expected format
                st.info("Bowling statistics data format not recognized")
                st.write("Raw data:", bowling_stats)
            
        else:
            st.error("Failed to load bowling statistics")
            if bowling_data:
                st.write("API Response:", bowling_data)

def show_sql_analytics_from_new_app():
    """SQL Analytics page with 25 predefined queries"""
    st.header("📊 SQL Analytics")
    st.markdown("---")
    
    # Import the SQL queries
    try:
        from sql_queries import get_all_queries, get_query, get_queries_by_category
        all_queries = get_all_queries()
    except ImportError:
        st.error("❌ SQL queries module not found. Please ensure sql_queries.py is in the same directory.")
        return
    
    # Query category selection
    st.sidebar.markdown("### 📚 Query Categories")
    category = st.sidebar.selectbox(
        "Select Category:",
        ["All", "Beginner", "Intermediate", "Advanced"]
    )
    
    # Get queries based on category
    if category == "All":
        queries = get_all_queries()
    else:
        queries = get_queries_by_category(category)
    
    # Main content
    st.markdown(f"### 📋 {category} Queries ({len(queries)} queries)")
    
    # Query selection
    query_options = {f"Query {num}: {info['title']}": num for num, info in queries.items()}
    selected_query_name = st.selectbox("Select a query to run:", list(query_options.keys()))
    selected_query_num = query_options[selected_query_name]
    
    # Display query information
    query_info = queries[selected_query_num]
    
    st.markdown(f"**Description:** {query_info['description']}")
    st.markdown(f"**Category:** {query_info['category']}")
    
    # Execute query button
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🚀 Run Query", type="primary"):
            with st.spinner("Executing query..."):
                try:
                    import mysql.connector
                    from config import DB_CONFIG
                    import pandas as pd
                    
                    connection = mysql.connector.connect(**DB_CONFIG)
                    cursor = connection.cursor()
                    
                    cursor.execute(query_info['query'])
                    results = cursor.fetchall()
                    
                    if results:
                        # Get column names
                        columns = [desc[0] for desc in cursor.description]
                        
                        # Create DataFrame
                        df = pd.DataFrame(results, columns=columns)
                        
                        st.success(f"✅ Query executed successfully! Found {len(df)} results.")
                        
                        # Display results
                        st.markdown("### 📊 Results")
                        st.dataframe(df, use_container_width=True)
                        
                        # Download button
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv,
                            file_name=f"query_{selected_query_num}_results.csv",
                            mime="text/csv"
                        )
                        
                        # Show query SQL
                        with st.expander("🔍 View SQL Query"):
                            st.code(query_info['query'], language="sql")
                            
                    else:
                        st.warning("⚠️ Query executed successfully but returned no results.")
                        st.info("💡 This might be because the required data is not yet populated.")
                        
                        # Show query SQL
                        with st.expander("🔍 View SQL Query"):
                            st.code(query_info['query'], language="sql")
                    
                    cursor.close()
                    connection.close()
                        
                except Exception as e:
                    st.error(f"❌ Query execution failed: {str(e)}")
    

def show_crud_page():
    """CRUD operations page"""
    st.header("🔧 CRUD Operations")
    
    st.subheader("👤 Players CRUD")
        
    operation = st.selectbox(
        "Select Operation:",
        ["Read All", "Create", "Update", "Delete"],
        key="player_operation"
    )
    
    if operation == "Read All":
        st.subheader("Read All Players")
        st.markdown("### 📝 Building SQL Query: SELECT")
        
        # SQL Query Builder UI
        with st.container():
            st.markdown("**SELECT** `*` **FROM** `players`")
            
            # WHERE clause builder
            st.markdown("**WHERE** (optional filters)")
            
            # Create filter form
            with st.form("filter_players_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Column:** `player_id`")
                    filter_player_id = st.text_input("Value:", placeholder="Enter player ID...", key="filter_player_id")
                    
                    st.markdown("**Column:** `name`")
                    filter_name = st.text_input("Value:", placeholder="Enter player name...", key="filter_name")
                    
                    st.markdown("**Column:** `country`")
                    filter_country = st.text_input("Value:", placeholder="Enter country...", key="filter_country")
                
                with col2:
                    st.markdown("**Column:** `role`")
                    filter_role = st.selectbox("Value:", ["All", "Batsman", "Bowler", "All-rounder", "Wicket-keeper"], key="filter_role")
                    
                    st.markdown("**Column:** `team_id`")
                    filter_team_id = st.text_input("Value:", placeholder="Enter team ID...", key="filter_team_id")
                
                with col3:
                    st.markdown("**Column:** `batting_style`")
                    filter_batting_style = st.text_input("Value:", placeholder="e.g., Right handed...", key="filter_batting")
                    
                    st.markdown("**Column:** `bowling_style`")
                    filter_bowling_style = st.text_input("Value:", placeholder="e.g., Left arm seamer...", key="filter_bowling")
                
                # Build WHERE clause
                where_conditions = []
                if filter_player_id:
                    where_conditions.append(f"player_id LIKE '%{filter_player_id}%'")
                if filter_name:
                    where_conditions.append(f"name LIKE '%{filter_name}%'")
                if filter_country:
                    where_conditions.append(f"country LIKE '%{filter_country}%'")
                if filter_role != "All":
                    where_conditions.append(f"role = '{filter_role}'")
                if filter_team_id:
                    where_conditions.append(f"team_id LIKE '%{filter_team_id}%'")
                if filter_batting_style:
                    where_conditions.append(f"batting_style LIKE '%{filter_batting_style}%'")
                if filter_bowling_style:
                    where_conditions.append(f"bowling_style LIKE '%{filter_bowling_style}%'")
                
                # Show the SQL query being built
                st.markdown("---")
                st.markdown("### 🔍 Generated SQL Query:")
                
                if where_conditions:
                    sql_query = f"SELECT * FROM players WHERE {' AND '.join(where_conditions)};"
                else:
                    sql_query = "SELECT * FROM players;"
                
                st.code(sql_query, language="sql")
                
                if st.form_submit_button("🚀 Execute SELECT Query", type="primary"):
                    with st.spinner("Executing SELECT query..."):
                        # Make API request with filters
                        if where_conditions:
                            # For now, we'll fetch all and filter client-side
                            # In a real app, you'd pass filters to the API
                            data = make_api_request("/api/players")
                            if data:
                                df = pd.DataFrame(data)
                                
                                # Apply filters
                                if filter_player_id:
                                    df = df[df['player_id'].astype(str).str.contains(filter_player_id, case=False, na=False)]
                                if filter_name:
                                    df = df[df['name'].str.contains(filter_name, case=False, na=False)]
                                if filter_country:
                                    df = df[df['country'].str.contains(filter_country, case=False, na=False)]
                                if filter_role != "All":
                                    df = df[df['role'] == filter_role]
                                if filter_team_id:
                                    df = df[df['team_id'].astype(str).str.contains(filter_team_id, na=False)]
                                if filter_batting_style:
                                    df = df[df['batting_style'].str.contains(filter_batting_style, case=False, na=False)]
                                if filter_bowling_style:
                                    df = df[df['bowling_style'].str.contains(filter_bowling_style, case=False, na=False)]
                                
                                st.success(f"✅ SELECT query executed successfully! Found {len(df)} players")
                                st.dataframe(df, width='stretch')
                                
                                # Show filter summary
                                st.info(f"**Applied WHERE conditions:** {', '.join([f'{k}: {v}' for k, v in {'player_id': filter_player_id, 'name': filter_name, 'country': filter_country, 'role': filter_role, 'team_id': filter_team_id, 'batting_style': filter_batting_style, 'bowling_style': filter_bowling_style}.items() if v and v != 'All'])}")
                            else:
                                st.error("❌ SELECT query failed: Failed to fetch players")
                        else:
                            # No filters, get all players
                            data = make_api_request("/api/players")
                            if data:
                                df = pd.DataFrame(data)
                                st.success(f"✅ SELECT query executed successfully! Found {len(df)} players")
                                st.dataframe(df, width='stretch')
                            else:
                                st.error("❌ SELECT query failed: Failed to fetch players")
        
        # Quick filter buttons
        with st.expander("### Quick Filters", expanded=True):
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if st.button("📋 Show All Players", type="primary", key="show_all_players"):
                    with st.spinner("Fetching all players..."):
                        data = make_api_request("/api/players")
                        if data:
                            df = pd.DataFrame(data)
                            st.success(f"Found {len(df)} players")
                            st.dataframe(df, width='stretch')
                        else:
                            st.error("Failed to fetch players")
            
            with col2:
                if st.button("Show All Batsmen"):
                    data = make_api_request("/api/players")
                    if data:
                        df = pd.DataFrame(data)
                        df = df[df['role'] == 'Batsman']
                        st.dataframe(df, width='stretch')
            
            with col3:
                if st.button("Show All Bowlers"):
                    data = make_api_request("/api/players")
                    if data:
                        df = pd.DataFrame(data)
                        df = df[df['role'] == 'Bowler']
                        st.dataframe(df, width='stretch')
            
            with col4:
                if st.button("Show All-rounders"):
                    data = make_api_request("/api/players")
                    if data:
                        df = pd.DataFrame(data)
                        df = df[df['role'] == 'All-rounder']
                        st.dataframe(df, width='stretch')
            
            with col5:
                if st.button("Show Wicket-keepers"):
                    data = make_api_request("/api/players")
                    if data:
                        df = pd.DataFrame(data)
                        df = df[df['role'] == 'Wicket-keeper']
                        st.dataframe(df, width='stretch')
        
    elif operation == "Create":
        st.subheader("Create New Player")
        st.markdown("### 📝 Building SQL Query: INSERT")
        
        # SQL Query Builder UI
        with st.container():
            st.markdown("**INSERT INTO** `players` **VALUES**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Column:** `player_id`")
                player_id = st.text_input("Value:", key="create_player_id", placeholder="Enter player ID...")
                
                st.markdown("**Column:** `name`")
                name = st.text_input("Value:", key="create_name", placeholder="Enter player name...")
                
                st.markdown("**Column:** `country`")
                country = st.text_input("Value:", key="create_country", placeholder="Enter country...")
                
                st.markdown("**Column:** `role`")
                role = st.selectbox("Value:", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"], key="create_role")
            
            with col2:
                st.markdown("**Column:** `batting_style`")
                batting_style = st.text_input("Value:", key="create_batting", placeholder="e.g., Right handed...")
                
                st.markdown("**Column:** `bowling_style`")
                bowling_style = st.text_input("Value:", key="create_bowling", placeholder="e.g., Left arm seamer...")
                
                st.markdown("**Column:** `team_id`")
                team_id = st.text_input("Value:", key="create_team_id", placeholder="Enter team ID (optional)...")
            
            # Show the SQL query being built
            st.markdown("---")
            st.markdown("### 🔍 Generated SQL Query:")
            
            sql_query = f"""INSERT INTO players (player_id, name, country, role, batting_style, bowling_style, team_id)
VALUES ('{player_id}', '{name}', '{country}', '{role}', '{batting_style}', '{bowling_style}', {f"'{team_id}'" if team_id else "NULL"});"""
            
            st.code(sql_query, language="sql")
            
            if st.button("🚀 Execute INSERT Query", type="primary"):
                if not player_id or not name or not country:
                    st.error("❌ Please fill in required fields: Player ID, Name, and Country")
                else:
                    player_data = {
                        "player_id": player_id,
                        "name": name,
                        "country": country,
                        "role": role,
                        "batting_style": batting_style,
                        "bowling_style": bowling_style,
                        "team_id": team_id if team_id else None
                    }
                    
                    try:
                        with st.spinner("Executing INSERT query..."):
                            response = requests.post(f"{API_BASE_URL}/api/players", json=player_data)
                            if response.status_code == 200:
                                st.success("✅ INSERT query executed successfully!")
                                st.balloons()
                            else:
                                st.error(f"❌ INSERT query failed: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Error executing query: {str(e)}")
        
    elif operation == "Update":
        st.subheader("Update Player")
        st.markdown("### 📝 Building SQL Query: UPDATE")
        
        # SQL Query Builder UI
        with st.container():
            st.markdown("**UPDATE** `players` **SET**")
            
            # WHERE clause for player_id
            st.markdown("**WHERE** `player_id` = ?")
            player_id = st.text_input("Enter Player ID:", placeholder="Enter player ID...", key="update_player_id")
            
            if not player_id:
                st.warning("⚠️ Please enter a Player ID to update")
            else:
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Column:** `name`")
                    new_name = st.text_input("New Value:", placeholder="Enter new name...", key="update_name")
                    
                    st.markdown("**Column:** `country`")
                    new_country = st.text_input("New Value:", placeholder="Enter new country...", key="update_country")
                    
                    st.markdown("**Column:** `role`")
                    new_role = st.selectbox("New Value:", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"], key="update_role")
                
                with col2:
                    st.markdown("**Column:** `batting_style`")
                    new_batting_style = st.text_input("New Value:", placeholder="e.g., Right handed...", key="update_batting")
                    
                    st.markdown("**Column:** `bowling_style`")
                    new_bowling_style = st.text_input("New Value:", placeholder="e.g., Left arm seamer...", key="update_bowling")
                    
                    st.markdown("**Column:** `team_id`")
                    new_team_id = st.text_input("New Value:", placeholder="Enter new team ID (optional)...", key="update_team_id")
                
                # Show the SQL query being built
                st.markdown("---")
                st.markdown("### 🔍 Generated SQL Query:")
                
                sql_query = f"""UPDATE players SET 
    name = '{new_name}',
    country = '{new_country}',
    role = '{new_role}',
    batting_style = '{new_batting_style}',
    bowling_style = '{new_bowling_style}',
    team_id = {f"'{new_team_id}'" if new_team_id else "NULL"}
WHERE player_id = '{player_id}';"""
                
                st.code(sql_query, language="sql")
                
                if st.button("🚀 Execute UPDATE Query", type="primary"):
                    if not new_name or not new_country:
                        st.error("❌ Please fill in required fields: Name and Country")
                    else:
                        # Prepare update data
                        update_data = {
                            "name": new_name,
                            "country": new_country,
                            "role": new_role,
                            "batting_style": new_batting_style,
                            "bowling_style": new_bowling_style,
                            "team_id": new_team_id if new_team_id else None
                        }
                        
                        # Make update request
                        try:
                            with st.spinner("Executing UPDATE query..."):
                                response = requests.put(f"{API_BASE_URL}/api/players/{player_id}", json=update_data)
                                if response.status_code == 200:
                                    st.success("✅ UPDATE query executed successfully!")
                                    st.balloons()
                                else:
                                    st.error(f"❌ UPDATE query failed: {response.text}")
                        except Exception as e:
                            st.error(f"❌ Error executing query: {str(e)}")
        
    elif operation == "Delete":
        st.subheader("Delete Player")
        st.markdown("### 📝 Building SQL Query: DELETE")
        
        # SQL Query Builder UI
        with st.container():
            st.markdown("**DELETE FROM** `players` **WHERE** `player_id` = ?")
            
            player_id = st.text_input("Enter Player ID:", placeholder="Enter player ID to delete...", key="delete_player_id")
            
            # Show the SQL query being built
            st.markdown("---")
            st.markdown("### 🔍 Generated SQL Query:")
            
            sql_query = f"DELETE FROM players WHERE player_id = '{player_id}';"
            
            st.code(sql_query, language="sql")
            
            if st.button("🚀 Execute DELETE Query", type="primary"):
                if not player_id:
                    st.error("❌ Please enter a Player ID to delete")
                else:
                    try:
                        with st.spinner("Executing DELETE query..."):
                            response = requests.delete(f"{API_BASE_URL}/api/players/{player_id}")
                            if response.status_code == 200:
                                st.success("✅ DELETE query executed successfully!")
                                st.balloons()
                            else:
                                st.error(f"❌ DELETE query failed: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Error executing query: {str(e)}")


def show_database_viewer_page():
    """Database viewer page with table selection and query functionality"""
    st.header("🗄️ Database Viewer")
    st.markdown("---")
    
    
    # Table selection
    st.subheader("📋 Browse Tables")
    
    # Load tables button
    if st.button("📊 Load Available Tables"):
        # Clear previous data
        if 'available_tables' in st.session_state:
            del st.session_state.available_tables
        if 'selected_table' in st.session_state:
            del st.session_state.selected_table
        st.rerun()
    
    # Load tables automatically or on button click
    if 'available_tables' not in st.session_state:
        with st.spinner("Loading tables..."):
            tables_data = make_api_request("/api/database_tables")
            if tables_data:
                tables = tables_data.get('tables', [])
                st.session_state.available_tables = tables
                st.success(f"Found {len(tables)} tables")
            else:
                st.error("Failed to load tables")
    
    # Display tables if available
    if 'available_tables' in st.session_state:
        tables = st.session_state.available_tables
        st.markdown(f"**Available Tables ({len(tables)}):**")
        
        # Display tables in columns
        cols = st.columns(3)
        for i, table in enumerate(tables):
            with cols[i % 3]:
                if st.button(f"📋 {table}", key=f"table_{table}"):
                    st.session_state.selected_table = table
                    st.rerun()
    
    # Show selected table
    if 'selected_table' in st.session_state:
        table_name = st.session_state.selected_table
        st.markdown(f"### 📋 Table: {table_name}")
        
        # Load table data automatically when table is selected
        if f"table_data_{table_name}" not in st.session_state:
            with st.spinner(f"Loading data from {table_name}..."):
                table_data = make_api_request(f"/api/database_table/{table_name}")
                if table_data:
                    st.session_state[f"table_data_{table_name}"] = table_data
                    st.success(f"✅ Loaded {table_data.get('total_rows', 0)} rows from {table_name}")
                else:
                    st.error(f"❌ Failed to load data from {table_name}")
        
        # Display table data if available
        if f"table_data_{table_name}" in st.session_state:
            table_data = st.session_state[f"table_data_{table_name}"]
            
            # Display data first
            data = table_data.get('data', [])
            if data:
                st.markdown("#### 📈 Table Data:")
                st.dataframe(data, width='stretch')
            else:
                st.error(f"❌ No data found in {table_name} table")
            
            # Display columns below the data
            columns = table_data.get('columns', [])
            if columns:
                st.markdown("#### 📊 Table Structure:")
                col_df = []
                for col in columns:
                    col_df.append({
                        'Column': col.get('Field', 'N/A'),
                        'Type': col.get('Type', 'N/A'),
                        'Null': col.get('Null', 'N/A'),
                        'Key': col.get('Key', 'N/A'),
                        'Default': col.get('Default', 'N/A')
                    })
                st.dataframe(col_df, width='stretch')
    
    st.markdown("---")
    
    # Custom SQL query
    st.subheader("🔍 Custom SQL Query")
    st.markdown("**Note:** Execute any SQL command (SELECT, INSERT, UPDATE, DELETE, etc.)")
    
    query = st.text_area(
        "Enter your SQL query:",
        placeholder="SELECT * FROM matches LIMIT 10;\n-- Or try: INSERT INTO teams (name) VALUES ('New Team');\n-- Or: UPDATE teams SET name = 'Updated' WHERE team_id = 1;\n-- Or: DELETE FROM teams WHERE team_id = 999;",
        height=120
    )
    
    if st.button("🚀 Execute Query", type="primary"):
        if query.strip():
            with st.spinner("Executing query..."):
                try:
                    # Use requests to send POST request with proper format
                    import requests
                    response = requests.post("http://localhost:8000/api/database_query", 
                                           json={"query": query}, 
                                           headers={"Content-Type": "application/json"})
                    
                    if response.status_code == 200:
                        result = response.json()
                        query_type = result.get('query_type', 'SELECT')
                        
                        # Display query
                        st.markdown("#### 📝 Query:")
                        st.code(result.get('query', ''))
                        
                        if query_type == 'SELECT':
                            # Handle SELECT queries
                            st.success(f"Query executed successfully! Found {result.get('total_rows', 0)} rows")
                            
                            # Display results
                            data = result.get('data', [])
                            if data:
                                st.markdown("#### 📊 Results:")
                                st.dataframe(data, width='stretch')
                            else:
                                st.error("No results found")
                        elif query_type == 'SHOW':
                            # Handle SHOW/DESCRIBE queries
                            st.success(f"Query executed successfully! Found {result.get('total_rows', 0)} items")
                            
                            # Display results
                            data = result.get('data', [])
                            if data:
                                st.markdown("#### 📊 Results:")
                                st.dataframe(data, width='stretch')
                            else:
                                st.error("No results found")
                        else:
                            # Handle non-SELECT queries (INSERT, UPDATE, DELETE, etc.)
                            affected_rows = result.get('affected_rows', 0)
                            message = result.get('message', 'Query executed successfully')
                            st.success(f"✅ {message}")
                            
                            if affected_rows > 0:
                                st.info(f"📊 {affected_rows} rows were affected by this query")
                    else:
                        st.error(f"Query failed: {response.text}")
                        
                except Exception as e:
                    st.error(f"Error executing query: {str(e)}")
        else:
            st.warning("Please enter a SQL query")


if __name__ == "__main__":
    main()
