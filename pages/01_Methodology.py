import streamlit as st
import pandas as pd
import pickle

st.set_page_config(
    page_title="Methodology",
    page_icon="⚽",
    layout="wide"
)

st.markdown("# Methodology & Deep Dive")
st.markdown("**Complete technical explanation of my pressure-adjusted finishing analysis**")

st.divider()

# ===== SECTION 1: PRESSURE INDEX =====
with st.expander("Pressure Index Calculation", expanded=False):
    st.markdown("""
    The Pressure Index quantifies how much a goal in a specific moment would change a team's 
    win probability. It's the foundation of our "pressure" measurement.

    ## COMPONENTS:

    ### 1. Score State (Goal Difference)
    How many goals ahead or behind is the team?
    - Trailing by 3 or more
    - Trailing by 2
    - Trailing by 1
    - Tied (0-0)
    - Leading by 1
    - Leading by 2
    - Leading by 3 or more

    ### 2. Time Remaining
    How many minutes until the final whistle?
    - Ranges from 0 to 90 minutes
    - More time = less pressure (can still change the game)
    - Less time = more pressure (fewer opportunities)

    ### 3. Win Probability Model
    Based on historical match data, what's the probability of:
    - Winning the match
    - Drawing the match
    - Losing the match
    
    This is calculated for every combination of score state and time remaining.

    ## CALCULATION:
    
    **Pressure Index = [Win Probability AFTER Goal] - [Win Probability BEFORE Goal]**
    
    **Example:** (not based on actual percentages)
    
    If a team is trailing 1-0 with 20 minutes left:
    - Before goal: 20% win probability
    - After goal (if they score): 50% win probability
    - Pressure Index = 50% - 20% = +30pp
    
    This high pressure index shows that scoring would dramatically improve their chances.

    ## COMPETITION MULTIPLIER:

    Different stages of the year have different pressure levels:
    - League play: 1.0x (baseline)
    - League run-in (final 10 games of the season): 1.2x
    """)

st.divider()

# ===== SECTION 2: STATISTICAL METHODOLOGY =====
with st.expander("Statistical Methodology", expanded=False):
    st.markdown("""
    ## SAMPLE SIZE & RELIABILITY:

    ### Minimum Shots Threshold: 20
    
    Why 20 shots?
    - 20 shots ~= 750-1000 minutes for a forward (based on historical averages)
    - Provides tighter confidence intervals
    - Distinguishes genuine skill from random variance
    - Below 20 shots: results are unreliable and excluded

    ## PRESSURE INDEX DISTRIBUTION:

    Shots are not evenly distributed across pressure levels. Most shots occur in:
    - Early game (lower pressure)
    - When teams are tied or leading (lower pressure)
    
    Clutch moments (high pressure) are naturally rarer. We use the TOP 25% of each 
    player's shots by pressure index to isolate these moments.

    ## UNWEIGHTED vs PRESSURE-WEIGHTED:

    - **Consistent Finishing Metric: Unweighted** (each shot counts equally)
      - Pure shot-to-xG analysis
      - Shows baseline finishing ability independent of context
    
    - **Pressure-Weighted Baseline: Weighted by pressure index**
      - Accounts for players who naturally take more/fewer high-pressure shots
      - Essential for fair clutch resilience comparison

    ## VARIANCE IN SMALL SAMPLES:

    A player with 25 shots might show +20% high-pressure finishing, but with only
    6 high-pressure shots (top 25%), this could be luck, not skill. Use shot count
    as a confidence indicator when evaluating individuals.

    ## DATA DEDUPLICATION:

    Raw data contained 12,181 shots. After removing exact duplicates (same player,
    match, minute), we retained 11,832 unique shots—99.7% of data.
    """)

st.divider()

# ===== SECTION 3: DATA SOURCES =====
with st.expander("Data Sources", expanded=False):
    st.markdown("""
    ## DATA COLLECTION:

    - **API:** theStatsAPI (https://api.thestatsapi.com)
    - **Method:** Real-time match data collection for 2025/26 season
    - Data was collected at both a player and match level to include all of the necessary statistics.
    
    ## LEAGUES COVERED:

    - Premier League (England)
    - La Liga (Spain)
    - Serie A (Italy)
    - Bundesliga (Germany)
    - Ligue 1 (France)
    
    Total: 5 top-tier European leagues

    ## COMPETITIONS INCLUDED:

    - Domestic league matches
    
    Time period: Full 2025/26 season

    ## SAMPLE SIZE:

    - Total forwards analyzed: 354 (position = "F")
    - Qualified forwards (20+ shots): 224
    - Total shots collected: 11,832 (deduplicated)
    - Unique matches: 5,489+

    ## EXPECTED GOALS (xG):

    xG represents the probability that a shot results in a goal, based on:
    - Shot location
    - Shot angle
    - Defensive pressure
    - Expected shooting accuracy from that position
    
    xG provides context for finishing quality. A goal from a 0.05 xG shot is more
    impressive than a goal from a 0.80 xG shot. xG for each shot was provided by our data source.

    ## PLAYER INFORMATION:

    - Name, nationality, age, club
    - Current team (for the 2025/26 season)
    - Playing position
    
    ## DATA UPDATES:

    This dashboard reflects completed matches only. Data is as current as the 
    2025/26 season data available from theStatsAPI.
    """)

st.divider()

# ===== SECTION 4: ASSUMPTIONS & LIMITATIONS =====
with st.expander("Assumptions & Limitations", expanded=False):
    st.markdown("""
    ## WHAT WE MEASURE:

    ✅ Shot-level finishing ability (how well players convert chances)
    ✅ Pressure resilience (performance change in high-pressure moments)
    ✅ Context-adjusted performance (accounting for game situation)

    ## WHAT WE DON'T MEASURE:

    ❌ Off-the-ball movement or positioning
    ❌ Defensive contributions
    ❌ Passing ability or playmaking
    ❌ Physical attributes (speed, strength, etc.)
    ❌ Team quality or tactics
    
    This tool is strictly about finishing ability in context.

    ## KEY ASSUMPTIONS:

    ### 1. xG Model is Accurate
    We assume the xG values provided by theStatsAPI accurately reflect shot quality.
    Variations in xG calculation could affect results.
    
    ### 2. Pressure Index Reflects Reality
    We assume goal impact on win probability matches historical patterns.
    Unusual circumstances (red cards, injuries) aren't accounted for.
    
    ### 3. Sample is Representative
    Players with 20+ shots represent stable performance. Very small samples
    (20-25 shots) may have higher variance.
    
    ### 4. Competition Multipliers are Fixed
    All CL knockouts weighted 1.4x, all group stages 1.2x. Real importance
    varies (e.g., deciding match vs already qualified for knockouts).

    ## LIMITATIONS:

    ### 1. Small Sample Variance
    A player with exactly 20 shots (minimum) has a wide confidence interval.
    Results stabilize with more total shots.
    
    ### 2. Mid-Season Players
    Forwards who joined mid-season from outside the analyzed leagues have limited data and may not be comparable
    to season-long players.
    
    ### 3. Injury/Suspension Effects
    If a player was injured for part of the season, their metrics reflect only
    the matches they played.
    
    ### 4. Team Context
    A striker on a low-xG team will naturally have lower shot volume.
    Raw metrics don't adjust for team quality.
    
    ### 5. Position Classification
    Some players classified as "F" might play across multiple forward positions.
    This could slightly affect interpretation.

    ### 6. Data Source Accuracy
    ⚠️ **Important Note:** Some player data may be slightly inaccurate due to limitations 
    in the data source (theStatsAPI), not due to any issues with this project's processes 
    or calculations. All metrics are calculated correctly based on the data provided by the API.
    
    **Known Issues:**
    - Erling Haaland shows 24 Premier League goals in the database, but he actually scored 
      27 in the 2025/26 season. This is a data collection issue with the API, not a 
      calculation error in this dashboard.

    ## EDGE CASES:

    ### Penalty Takers
    Penalties have high xG (0.79) but different psychology.
    Some clutch resilience may reflect penalty-taking ability.
    
    ### Formation Changes
    A team's formation shift mid-season affects shot quality
    and opportunity availability.
    
    ### Competition Level
    Group stage European matches may be lower quality than
    knockout stages, affecting xG and finishing metrics.

    ## BEST PRACTICES FOR USING THIS DATA:

    1. Always check shot count (higher = more reliable)
    2. Combine with other data sources (video, team context, physical attributes)
    3. Use this for identifying candidates, not final recruitment decisions
    4. Remember: Context matters (team quality, position, age, etc.)
    """)

st.divider()

st.markdown("""
---
**Questions about the methodology?** This dashboard uses this framework to provide
context-adjusted finishing analysis. Return to the main Dashboard to explore individual players.
""")
---

**Whole site created by Jonathan Tang**

📧 Email: jonathan.ptang7@gmail.com  
💼 LinkedIn: www.linkedin.com/in/jonathantang04
""")
