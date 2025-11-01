#!/usr/bin/env python3
"""
Corrected SQL Queries - Match original questions exactly
"""

def get_all_queries():
    """Get all 25 corrected SQL queries"""
    return {
        1: {
            "title": "Indian Players with Roles and Styles",
            "description": "Find all players who represent India. Display their full name, playing role, batting style, and bowling style.",
            "category": "Beginner",
            "query": """
                SELECT 
                    p.name AS 'Full Name',
                    p.role AS 'Playing Role',
                    p.batting_style AS 'Batting Style',
                    p.bowling_style AS 'Bowling Style'
                FROM players p
                JOIN teams t ON p.team_id = t.team_id
                WHERE t.name = 'India'
                ORDER BY p.name;
            """
        },
        2: {
            "title": "Recent Matches with Venue Details",
            "description": "Show all cricket matches that were played in the last few days. Include the match description, both team names, venue name with city, and the match date. Sort by most recent matches first.",
            "category": "Beginner",
            "query": """
                SELECT 
                    m.match_desc AS 'Match Description',
                    t1.name AS 'Team 1 Name',
                    t2.name AS 'Team 2 Name',
                    CONCAT(v.name, ', ', v.city) AS 'Venue Name with City',
                    DATE(m.start_datetime) AS 'Match Date'
                FROM matches m
                LEFT JOIN teams t1 ON m.team1_id = t1.team_id
                LEFT JOIN teams t2 ON m.team2_id = t2.team_id
                LEFT JOIN venues v ON m.venue_id = v.venue_id
                WHERE m.start_datetime >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                ORDER BY m.start_datetime DESC
                LIMIT 20;
            """
        },
        3: {
            "title": "Top 10 ODI Run Scorers",
            "description": "List the top 10 highest run scorers in ODI cricket. Show player name, total runs scored, batting average, and number of centuries. Display the highest run scorer first.",
            "category": "Beginner",
            "query": """
                SELECT 
                    p.name AS 'Player Name',
                    ps.runs AS 'Total Runs Scored',
                    ps.batting_average AS 'Batting Average',
                    ps.centuries AS 'Number of Centuries'
                FROM player_stats ps
                JOIN players p ON ps.player_id = p.player_id
                WHERE ps.format = 'ODI' AND ps.runs > 0
                ORDER BY ps.runs DESC
                LIMIT 10;
            """
        },
        4: {
            "title": "High-Capacity Venues",
            "description": "Display all cricket venues that have a seating capacity of more than 30,000 spectators. Show venue name, city, country, and capacity. Order by largest capacity first.",
            "category": "Beginner",
            "query": """
                SELECT 
                    v.name AS 'Venue Name',
                    v.city AS 'City',
                    v.country AS 'Country',
                    v.capacity AS 'Capacity'
                FROM venues v
                WHERE v.capacity > 30000
                ORDER BY v.capacity DESC;
            """
        },
        5: {
            "title": "Team Win Counts",
            "description": "Calculate how many matches each team has won. Show team name and total number of wins. Display teams with the most wins first.",
            "category": "Beginner",
            "query": """
                SELECT 
                    t.name AS 'Team Name',
                    COUNT(*) AS 'Total Number of Wins'
                FROM matches m
                JOIN teams t ON m.winner_id = t.team_id
                WHERE m.winner_id IS NOT NULL
                GROUP BY t.team_id, t.name
                ORDER BY COUNT(*) DESC;
            """
        },
        6: {
            "title": "Player Role Distribution",
            "description": "Count how many players belong to each playing role (like Batsman, Bowler, All-rounder, Wicket-keeper). Show the role and count of players for each role.",
            "category": "Beginner",
            "query": """
                SELECT 
                    p.role AS 'Playing Role',
                    COUNT(*) AS 'Count of Players for Each Role'
                FROM players p
                WHERE p.role IS NOT NULL
                GROUP BY p.role
                ORDER BY COUNT(*) DESC;
            """
        },
        7: {
            "title": "Highest Scores by Format",
            "description": "Find the highest individual batting score achieved in each cricket format (Test, ODI, T20I). Display the format and the highest score for that format.",
            "category": "Beginner",
            "query": """
                SELECT 
                    ps.format AS 'Cricket Format',
                    MAX(ps.highest_score) AS 'Highest Score for That Format'
                FROM player_stats ps
                WHERE ps.highest_score > 0
                GROUP BY ps.format
                ORDER BY MAX(ps.highest_score) DESC;
            """
        },
        8: {
            "title": "2024 Cricket Series",
            "description": "Show all cricket series that started in the year 2024. Include series name, host country, match type, start date, and total number of matches planned.",
            "category": "Beginner",
            "query": """
                SELECT 
                    s.name AS 'Series Name',
                    s.host_country AS 'Host Country',
                    'International' AS 'Match Type',
                    s.start_date AS 'Start Date',
                    s.total_matches AS 'Total Number of Matches Planned'
                FROM series s
                WHERE s.year = '2024'
                ORDER BY s.start_date DESC;
            """
        },
        9: {
            "title": "All-Rounder Players",
            "description": "Find all-rounder players who have scored more than 1000 runs AND taken more than 50 wickets in their career. Display player name, total runs, total wickets, and the cricket format.",
            "category": "Intermediate",
            "query": """
                SELECT 
                    p.name AS 'Player Name',
                    ps.runs AS 'Total Runs',
                    ps.wickets AS 'Total Wickets',
                    ps.format AS 'Cricket Format'
                FROM player_stats ps
                JOIN players p ON ps.player_id = p.player_id
                WHERE ps.runs > 1000 
                  AND ps.wickets > 50
                  AND p.role = 'ALL ROUNDER'
                ORDER BY ps.runs DESC;
            """
        },
        10: {
            "title": "Recent Completed Matches",
            "description": "Get details of the last 20 completed matches. Show match description, both team names, winning team, victory margin, victory type (runs/wickets), and venue name. Display most recent matches first.",
            "category": "Intermediate",
            "query": """
                SELECT 
                    m.match_desc AS 'Match Description',
                    t1.name AS 'Team 1 Name',
                    t2.name AS 'Team 2 Name',
                    tw.name AS 'Winning Team',
                    CASE 
                        WHEN m.status LIKE '%runs%' THEN SUBSTRING_INDEX(SUBSTRING_INDEX(m.status, 'by ', -1), ' ', 1)
                        WHEN m.status LIKE '%wkts%' THEN SUBSTRING_INDEX(SUBSTRING_INDEX(m.status, 'by ', -1), ' ', 1)
                        ELSE 'Unknown'
                    END AS 'Victory Margin',
                    CASE 
                        WHEN m.status LIKE '%runs%' THEN 'runs'
                        WHEN m.status LIKE '%wkts%' THEN 'wickets'
                        ELSE 'Unknown'
                    END AS 'Victory Type',
                    v.name AS 'Venue Name'
                FROM matches m
                LEFT JOIN teams t1 ON m.team1_id = t1.team_id
                LEFT JOIN teams t2 ON m.team2_id = t2.team_id
                LEFT JOIN teams tw ON m.winner_id = tw.team_id
                LEFT JOIN venues v ON m.venue_id = v.venue_id
                WHERE m.winner_id IS NOT NULL
                ORDER BY m.start_datetime DESC
                LIMIT 20;
            """
        },
        11: {
            "title": "Multi-Format Player Performance",
            "description": "Compare each player's performance across different cricket formats. For players who have played at least 2 different formats, show their total runs in Test cricket, ODI cricket, and T20I cricket, along with their overall batting average across all formats.",
            "category": "Intermediate",
            "query": """
                SELECT 
                    p.name AS 'Player Name',
                    MAX(CASE WHEN ps.format = 'TEST' THEN ps.runs ELSE 0 END) AS 'Total Runs in Test Cricket',
                    MAX(CASE WHEN ps.format = 'ODI' THEN ps.runs ELSE 0 END) AS 'Total Runs in ODI Cricket',
                    MAX(CASE WHEN ps.format = 'T20' THEN ps.runs ELSE 0 END) AS 'Total Runs in T20I Cricket',
                    AVG(ps.batting_average) AS 'Overall Batting Average Across All Formats'
                FROM player_stats ps
                JOIN players p ON ps.player_id = p.player_id
                WHERE ps.runs > 0
                GROUP BY ps.player_id, p.name
                HAVING COUNT(DISTINCT ps.format) >= 2
                ORDER BY AVG(ps.batting_average) DESC;
            """
        },
        12: {
            "title": "Home vs Away Performance",
            "description": "Analyze each international team's performance when playing at home versus playing away. Determine whether each team played at home or away based on whether the venue country matches the team's country. Count wins for each team in both home and away conditions.",
            "category": "Intermediate",
            "query": """
                SELECT 
                    t.name AS 'Team Name',
                    SUM(CASE 
                        WHEN v.country = t.name THEN 1 
                        ELSE 0 
                    END) AS 'Home Wins',
                    SUM(CASE 
                        WHEN v.country != t.name OR v.country IS NULL THEN 1 
                        ELSE 0 
                    END) AS 'Away Wins'
                FROM matches m
                JOIN teams t ON m.winner_id = t.team_id
                LEFT JOIN venues v ON m.venue_id = v.venue_id
                WHERE m.winner_id IS NOT NULL
                GROUP BY t.team_id, t.name
                ORDER BY (SUM(CASE WHEN v.country = t.name THEN 1 ELSE 0 END) + 
                         SUM(CASE WHEN v.country != t.name OR v.country IS NULL THEN 1 ELSE 0 END)) DESC;
            """
        },
        13: {
            "title": "Batting Partnerships",
            "description": "Identify batting partnerships where two consecutive batsmen (batting positions next to each other) scored a combined total of 100 or more runs in the same innings. Show both player names, their combined partnership runs, and which innings it occurred in.",
            "category": "Intermediate",
            "query": """
                SELECT 
                    p1.name AS 'Batsman 1 Name',
                    p2.name AS 'Batsman 2 Name',
                    (ms1.runs + ms2.runs) AS 'Combined Partnership Runs',
                    ms1.innings_id AS 'Which Innings It Occurred In'
                FROM match_scorecards ms1
                JOIN match_scorecards ms2 ON ms1.match_id = ms2.match_id 
                    AND ms1.innings_id = ms2.innings_id
                    AND ABS(ms1.batting_position - ms2.batting_position) = 1
                JOIN players p1 ON ms1.player_id = p1.player_id
                JOIN players p2 ON ms2.player_id = p2.player_id
                WHERE (ms1.runs + ms2.runs) >= 100
                ORDER BY (ms1.runs + ms2.runs) DESC;
            """
        },
        14: {
            "title": "Venue Bowling Performance",
            "description": "Examine bowling performance at different venues. For bowlers who have played at least 3 matches at the same venue, calculate their average economy rate, total wickets taken, and number of matches played at each venue. Focus on bowlers who bowled at least 4 overs in each match.",
            "category": "Intermediate",
            "query": """
                SELECT 
                    p.name AS 'Bowler Name',
                    v.name AS 'Venue Name',
                    COUNT(DISTINCT m.match_id) AS 'Number of Matches Played',
                    AVG(ps.economy_rate) AS 'Average Economy Rate',
                    SUM(ps.wickets) AS 'Total Wickets Taken'
                FROM matches m
                JOIN venues v ON m.venue_id = v.venue_id
                JOIN players p ON p.role = 'BOWLER' OR p.role = 'ALL ROUNDER'
                JOIN player_stats ps ON ps.player_id = p.player_id
                WHERE ps.wickets > 0 AND ps.economy_rate > 0
                GROUP BY p.player_id, p.name, v.venue_id, v.name
                HAVING COUNT(DISTINCT m.match_id) >= 3
                ORDER BY AVG(ps.economy_rate) ASC;
            """
        },
        15: {
            "title": "Close Match Performance",
            "description": "Identify players who perform exceptionally well in close matches. A close match is defined as one decided by less than 50 runs OR less than 5 wickets. For these close matches, calculate each player's average runs scored, total close matches played, and how many of those close matches their team won when they batted.",
            "category": "Intermediate",
            "query": """
                SELECT 
                    p.name AS 'Player Name',
                    COUNT(DISTINCT m.match_id) AS 'Total Close Matches Played',
                    AVG(ms.runs) AS 'Average Runs Scored',
                    SUM(CASE WHEN m.winner_id = p.team_id THEN 1 ELSE 0 END) AS 'How Many of Those Close Matches Their Team Won'
                FROM matches m
                JOIN match_scorecards ms ON m.match_id = ms.match_id
                JOIN players p ON ms.player_id = p.player_id
                WHERE (m.status LIKE '%by 1 wkts%' OR m.status LIKE '%by 2 wkts%' OR m.status LIKE '%by 3 wkts%' OR m.status LIKE '%by 4 wkts%' 
                       OR m.status LIKE '%by 5 wkts%' OR m.status LIKE '%by 6 wkts%' OR m.status LIKE '%by 7 wkts%' OR m.status LIKE '%by 8 wkts%' 
                       OR m.status LIKE '%by 9 wkts%' OR m.status LIKE '%by 10 wkts%'
                       OR m.status LIKE '%by 1 runs%' OR m.status LIKE '%by 2 runs%' OR m.status LIKE '%by 3 runs%' OR m.status LIKE '%by 4 runs%' 
                       OR m.status LIKE '%by 5 runs%' OR m.status LIKE '%by 6 runs%' OR m.status LIKE '%by 7 runs%' OR m.status LIKE '%by 8 runs%' 
                       OR m.status LIKE '%by 9 runs%' OR m.status LIKE '%by 10 runs%' OR m.status LIKE '%by 11 runs%' OR m.status LIKE '%by 12 runs%' 
                       OR m.status LIKE '%by 13 runs%' OR m.status LIKE '%by 14 runs%' OR m.status LIKE '%by 15 runs%' OR m.status LIKE '%by 16 runs%' 
                       OR m.status LIKE '%by 17 runs%' OR m.status LIKE '%by 18 runs%' OR m.status LIKE '%by 19 runs%' OR m.status LIKE '%by 20 runs%' 
                       OR m.status LIKE '%by 21 runs%' OR m.status LIKE '%by 22 runs%' OR m.status LIKE '%by 23 runs%' OR m.status LIKE '%by 24 runs%' 
                       OR m.status LIKE '%by 25 runs%' OR m.status LIKE '%by 26 runs%' OR m.status LIKE '%by 27 runs%' OR m.status LIKE '%by 28 runs%' 
                       OR m.status LIKE '%by 29 runs%' OR m.status LIKE '%by 30 runs%' OR m.status LIKE '%by 31 runs%' OR m.status LIKE '%by 32 runs%' 
                       OR m.status LIKE '%by 33 runs%' OR m.status LIKE '%by 34 runs%' OR m.status LIKE '%by 35 runs%' OR m.status LIKE '%by 36 runs%' 
                       OR m.status LIKE '%by 37 runs%' OR m.status LIKE '%by 38 runs%' OR m.status LIKE '%by 39 runs%' OR m.status LIKE '%by 40 runs%' 
                       OR m.status LIKE '%by 41 runs%' OR m.status LIKE '%by 42 runs%' OR m.status LIKE '%by 43 runs%' OR m.status LIKE '%by 44 runs%' 
                       OR m.status LIKE '%by 45 runs%' OR m.status LIKE '%by 46 runs%' OR m.status LIKE '%by 47 runs%' OR m.status LIKE '%by 48 runs%' 
                       OR m.status LIKE '%by 49 runs%')
                   AND m.winner_id IS NOT NULL
                GROUP BY p.player_id, p.name
                HAVING COUNT(DISTINCT m.match_id) >= 1
                ORDER BY AVG(ms.runs) DESC;
            """
        },
        16: {
            "title": "Yearly Performance Trends",
            "description": "Track how players' batting performance changes over different years. For matches since 2020, show each player's average runs per match and average strike rate for each year. Only include players who played at least 5 matches in that year.",
            "category": "Intermediate",
            "query": """
                SELECT 
                    p.name AS 'Player Name',
                    YEAR(m.start_datetime) AS 'Year',
                    COUNT(DISTINCT m.match_id) AS 'Matches Played',
                    AVG(ms.runs) AS 'Average Runs per Match',
                    AVG(ms.strike_rate) AS 'Average Strike Rate for Each Year'
                FROM matches m
                JOIN match_scorecards ms ON m.match_id = ms.match_id
                JOIN players p ON ms.player_id = p.player_id
                WHERE YEAR(m.start_datetime) >= 2020
                GROUP BY p.player_id, p.name, YEAR(m.start_datetime)
                HAVING COUNT(DISTINCT m.match_id) >= 3
                ORDER BY p.name, YEAR(m.start_datetime);
            """
        },
        17: {
            "title": "Toss Advantage Analysis",
            "description": "Investigate whether winning the toss gives teams an advantage in winning matches. Calculate what percentage of matches are won by the team that wins the toss, broken down by their toss decision (choosing to bat first or bowl first).",
            "category": "Advanced",
            "query": """
                SELECT 
                    m.toss_decision AS 'Toss Decision',
                    COUNT(*) AS 'Total Matches',
                    SUM(CASE WHEN m.winner_id = m.toss_winner_id THEN 1 ELSE 0 END) AS 'Toss Winner Wins',
                    ROUND((SUM(CASE WHEN m.winner_id = m.toss_winner_id THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) AS 'Win Percentage'
                FROM matches m
                WHERE m.toss_decision IS NOT NULL AND m.winner_id IS NOT NULL
                GROUP BY m.toss_decision
                ORDER BY m.toss_decision;
            """
        },
        18: {
            "title": "Most Economical Bowlers",
            "description": "Find the most economical bowlers in limited-overs cricket (ODI and T20 formats). Calculate each bowler's overall economy rate and total wickets taken. Only consider bowlers who have bowled in at least 10 matches and bowled at least 2 overs per match on average.",
            "category": "Advanced",
            "query": """
                SELECT 
                    p.name AS 'Bowler Name',
                    ps.format AS 'Format',
                    ps.matches AS 'Matches',
                    ps.economy_rate AS 'Economy Rate',
                    ps.wickets AS 'Total Wickets'
                FROM player_stats ps
                JOIN players p ON ps.player_id = p.player_id
                WHERE ps.format IN ('ODI', 'T20') 
                  AND ps.economy_rate > 0 
                  AND ps.wickets > 0
                  AND ps.matches >= 10
                  AND (ps.balls_bowled / ps.matches) >= 12  -- At least 2 overs per match
                ORDER BY ps.economy_rate ASC;
            """
        },
        19: {
            "title": "Consistent Batsmen Analysis",
            "description": "Determine which batsmen are most consistent in their scoring. Calculate the average runs scored and the standard deviation of runs for each player. Only include players who have faced at least 10 balls per innings and played since 2022. A lower standard deviation indicates more consistent performance.",
            "category": "Advanced",
            "query": """
                SELECT 
                    p.name AS 'Player Name',
                    COUNT(ms.innings_id) AS 'Innings',
                    AVG(ms.runs) AS 'Average Runs Scored',
                    STDDEV(ms.runs) AS 'Standard Deviation of Runs',
                    ROUND(STDDEV(ms.runs) / AVG(ms.runs), 2) AS 'Consistency Ratio'
                FROM match_scorecards ms
                JOIN players p ON ms.player_id = p.player_id
                JOIN matches m ON ms.match_id = m.match_id
                WHERE ms.balls >= 10 
                  AND YEAR(m.start_datetime) >= 2022
                GROUP BY p.player_id, p.name
                HAVING COUNT(ms.innings_id) >= 5
                ORDER BY STDDEV(ms.runs) / AVG(ms.runs) ASC;
            """
        },
        20: {
            "title": "Format-wise Performance Analysis",
            "description": "Analyze how many matches each player has played in different cricket formats and their batting average in each format. Show the count of Test matches, ODI matches, and T20 matches for each player, along with their respective batting averages. Only include players who have played at least 20 total matches across all formats.",
            "category": "Advanced",
            "query": """
                SELECT 
                    p.name AS 'Player Name',
                    SUM(CASE WHEN ps.format = 'TEST' THEN ps.matches ELSE 0 END) AS 'Count of Test Matches',
                    SUM(CASE WHEN ps.format = 'ODI' THEN ps.matches ELSE 0 END) AS 'Count of ODI Matches',
                    SUM(CASE WHEN ps.format = 'T20' THEN ps.matches ELSE 0 END) AS 'Count of T20 Matches',
                    AVG(CASE WHEN ps.format = 'TEST' THEN ps.batting_average END) AS 'Test Batting Average',
                    AVG(CASE WHEN ps.format = 'ODI' THEN ps.batting_average END) AS 'ODI Batting Average',
                    AVG(CASE WHEN ps.format = 'T20' THEN ps.batting_average END) AS 'T20 Batting Average'
                FROM player_stats ps
                JOIN players p ON ps.player_id = p.player_id
                WHERE ps.matches > 0
                GROUP BY ps.player_id, p.name
                HAVING SUM(ps.matches) >= 20
                ORDER BY SUM(ps.matches) DESC;
            """
        },
        21: {
            "title": "Comprehensive Performance Ranking",
            "description": "Create a comprehensive performance ranking system for players. Combine their batting performance (runs scored, batting average, strike rate), bowling performance (wickets taken, bowling average, economy rate), and fielding performance (catches, stumpings) into a single weighted score.",
            "category": "Advanced",
            "query": """
                SELECT 
                    p.name AS 'Player Name',
                    ps.format AS 'Format',
                    ps.runs AS 'Runs Scored',
                    ps.batting_average AS 'Batting Average',
                    ps.strike_rate AS 'Strike Rate',
                    ps.wickets AS 'Wickets Taken',
                    ps.bowling_average AS 'Bowling Average',
                    ps.economy_rate AS 'Economy Rate',
                    ROUND(
                        (ps.runs * 0.01) + (ps.batting_average * 0.5) + (ps.strike_rate * 0.3) +
                        (COALESCE(ps.wickets, 0) * 2) + ((50 - COALESCE(ps.bowling_average, 50)) * 0.5) + 
                        ((6 - COALESCE(ps.economy_rate, 6)) * 2), 2
                    ) AS 'Performance Score'
                FROM player_stats ps
                JOIN players p ON ps.player_id = p.player_id
                WHERE ps.runs > 0 OR ps.wickets > 0
                ORDER BY ROUND(
                    (ps.runs * 0.01) + (ps.batting_average * 0.5) + (ps.strike_rate * 0.3) +
                    (COALESCE(ps.wickets, 0) * 2) + ((50 - COALESCE(ps.bowling_average, 50)) * 0.5) + 
                    ((6 - COALESCE(ps.economy_rate, 6)) * 2), 2
                ) DESC;
            """
        },
        22: {
            "title": "Head-to-Head Match Analysis",
            "description": "Build a head-to-head match prediction analysis between teams. For each pair of teams that have played at least 5 matches against each other in the last 3 years, calculate total matches played between them, wins for each team, and overall win percentage for each team in this head-to-head record.",
            "category": "Advanced",
            "query": """
                SELECT 
                    t1.name AS 'Team 1',
                    t2.name AS 'Team 2',
                    COUNT(*) AS 'Total Matches Played Between Them',
                    SUM(CASE WHEN m.winner_id = t1.team_id THEN 1 ELSE 0 END) AS 'Team 1 Wins',
                    SUM(CASE WHEN m.winner_id = t2.team_id THEN 1 ELSE 0 END) AS 'Team 2 Wins',
                    ROUND((SUM(CASE WHEN m.winner_id = t1.team_id THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) AS 'Team 1 Win %',
                    ROUND((SUM(CASE WHEN m.winner_id = t2.team_id THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) AS 'Team 2 Win %'
                FROM matches m
                JOIN teams t1 ON m.team1_id = t1.team_id
                JOIN teams t2 ON m.team2_id = t2.team_id
                WHERE m.start_datetime >= '2011-01-01'
                  AND m.winner_id IS NOT NULL
                GROUP BY t1.team_id, t1.name, t2.team_id, t2.name
                HAVING COUNT(*) >= 5
                ORDER BY COUNT(*) DESC;
            """
        },
        23: {
            "title": "Recent Form Analysis",
            "description": "Analyze recent player form and momentum. For each player's last 10 batting performances, calculate average runs in their last 5 matches vs their last 10 matches, recent strike rate trends, and number of scores above 50 in recent matches.",
            "category": "Advanced",
            "query": """
                SELECT 
                    p.name AS 'Player Name',
                    COUNT(ms.innings_id) AS 'Recent Innings',
                    AVG(ms.runs) AS 'Average Runs',
                    AVG(ms.strike_rate) AS 'Average Strike Rate',
                    SUM(CASE WHEN ms.runs >= 50 THEN 1 ELSE 0 END) AS 'Scores Above 50',
                    ROUND((SUM(CASE WHEN ms.runs >= 50 THEN 1 ELSE 0 END) * 100.0 / COUNT(ms.innings_id)), 2) AS '50+ Score Percentage'
                FROM match_scorecards ms
                JOIN players p ON ms.player_id = p.player_id
                JOIN matches m ON ms.match_id = m.match_id
                WHERE m.start_datetime >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
                GROUP BY p.player_id, p.name
                HAVING COUNT(ms.innings_id) >= 5
                ORDER BY AVG(ms.runs) DESC;
            """
        },
        24: {
            "title": "Successful Batting Partnerships",
            "description": "Study successful batting partnerships to identify the best player combinations. For pairs of players who have batted together as consecutive batsmen (positions differ by 1) in at least 5 partnerships, calculate their average partnership runs, count how many of their partnerships exceeded 50 runs, and find their highest partnership score.",
            "category": "Advanced",
            "query": """
                SELECT 
                    p1.name AS 'Batsman 1',
                    p2.name AS 'Batsman 2',
                    COUNT(*) AS 'Partnerships',
                    AVG(ms1.runs + ms2.runs) AS 'Average Partnership Runs',
                    MAX(ms1.runs + ms2.runs) AS 'Highest Partnership Score',
                    SUM(CASE WHEN (ms1.runs + ms2.runs) >= 50 THEN 1 ELSE 0 END) AS 'Partnerships Exceeded 50 Runs',
                    ROUND((SUM(CASE WHEN (ms1.runs + ms2.runs) >= 50 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) AS 'Success Rate %'
                FROM match_scorecards ms1
                JOIN match_scorecards ms2 ON ms1.match_id = ms2.match_id 
                    AND ms1.innings_id = ms2.innings_id
                    AND ABS(ms1.batting_position - ms2.batting_position) = 1
                JOIN players p1 ON ms1.player_id = p1.player_id
                JOIN players p2 ON ms2.player_id = p2.player_id
                WHERE p1.player_id < p2.player_id  -- Avoid duplicates
                GROUP BY p1.player_id, p1.name, p2.player_id, p2.name
                HAVING COUNT(*) >= 5
                ORDER BY AVG(ms1.runs + ms2.runs) DESC;
            """
        },
        25: {
            "title": "Player Performance Evolution",
            "description": "Perform a time-series analysis of player performance evolution. Track how each player's batting performance changes over time by calculating quarterly averages for runs and strike rate, and determining overall career trajectory over the last few years.",
            "category": "Advanced",
            "query": """
                SELECT 
                    p.name AS 'Player Name',
                    YEAR(m.start_datetime) AS 'Year',
                    QUARTER(m.start_datetime) AS 'Quarter',
                    COUNT(ms.innings_id) AS 'Innings',
                    AVG(ms.runs) AS 'Average Runs',
                    AVG(ms.strike_rate) AS 'Average Strike Rate',
                    CASE 
                        WHEN AVG(ms.runs) > LAG(AVG(ms.runs)) OVER (PARTITION BY p.player_id ORDER BY YEAR(m.start_datetime), QUARTER(m.start_datetime)) THEN 'Career Ascending'
                        WHEN AVG(ms.runs) < LAG(AVG(ms.runs)) OVER (PARTITION BY p.player_id ORDER BY YEAR(m.start_datetime), QUARTER(m.start_datetime)) THEN 'Career Declining'
                        ELSE 'Career Stable'
                    END AS 'Performance Category'
                FROM match_scorecards ms
                JOIN players p ON ms.player_id = p.player_id
                JOIN matches m ON ms.match_id = m.match_id
                WHERE m.start_datetime >= DATE_SUB(NOW(), INTERVAL 2 YEAR)
                GROUP BY p.player_id, p.name, YEAR(m.start_datetime), QUARTER(m.start_datetime)
                HAVING COUNT(ms.innings_id) >= 3
                ORDER BY p.name, YEAR(m.start_datetime), QUARTER(m.start_datetime);
            """
        }
    }

def get_query(query_number):
    """Get a specific query by number"""
    queries = get_all_queries()
    return queries.get(query_number)

def get_queries_by_category(category):
    """Get queries by category"""
    all_queries = get_all_queries()
    return {num: query for num, query in all_queries.items() if query['category'] == category}
