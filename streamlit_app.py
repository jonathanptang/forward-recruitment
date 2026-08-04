import streamlit as st
import pickle
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Forward Recruitment Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-small {
        font-size: 12px;
        font-weight: bold;
    }
    .player-name-small {
        font-size: 14px;
    }
    .team-name-small {
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_data():
    try:
        with open('clutch_model_league_european_integrated.pkl', 'rb') as f:
            checkpoint = pickle.load(f)
        return checkpoint
    except FileNotFoundError:
        st.error("❌ Checkpoint file not found!")
        return None

checkpoint = load_data()
if checkpoint is None:
    st.stop()

qualified_forwards = checkpoint['qualified_forwards'].copy()
enriched_shots_all = checkpoint['enriched_shots_all'].copy()
match_lookup = checkpoint['match_lookup']

st.markdown("# ⚽ Forward Recruitment Analytics Dashboard")
st.markdown("**Pressure-Adjusted Finishing Analysis for the 2025/26 Season**")

with st.expander("Why This Matters", expanded=False):
    st.markdown("""
    Traditional forward recruitment relies on incomplete metrics. Goals and expected goals (xG) 
    are standard in the industry, but they treat all shots equally, ignoring a fundamental truth 
    about football: context matters.

    A goal in the 90th minute while trailing 1-0 is completely different from a goal in the 
    30th minute while already leading 3-0. The first could save a point or keep a team in a 
    knockout competition. The second is already won. Yet both count as "1 goal" on a player's 
    scoring record.

    This creates a blind spot: players who elevate when outcomes matter most, and conversely, 
    players who score consistently but disappear in decisive moments. Traditional metrics miss 
    both patterns.

    This dashboard measures forward finishing ability in CONTEXT. It answers two critical questions:

    1. **How good is this player's base finishing ability?**
    2. **How does that ability change when the team needs them most?**

    These two dimensions (baseline performance and clutch performance) are what separate good 
    strikers from great ones.
    """)

with st.expander("Consistent Finishing Metric", expanded=False):
    st.markdown("""
    The Consistent Finishing Metric measures how many percentage points better or worse a 
    player finishes compared to the quality of chances they receive, across ALL situations.

    **CALCULATION:**
    
    For every shot a player takes, we calculate: (Goal - xG)
    - If the player scored, it's 1 - xG (positive value)
    - If they missed, 0 - xG (negative value)
    
    Then we average these across the entire season.

    **INTERPRETATION:**

    - **+5.0%** = Player scores 5.0 percentage points better than xG predicts on average
      - If they take 100 shots worth 20 xG, they would actually score 25 goals instead of the predicted 20

    - **-2.0%** = Player scores 2.0 percentage points worse than xG predicts
      - Finishing below expectation

    - **0%** = Finishing exactly as xG predicts

    **WHY THIS MATTERS:**
    
    This metric is independent of pressure, luck, or situation. It shows your player's 
    consistent ability to convert chances over a full season. High values indicate genuine 
    finishing skill.
    """)

with st.expander("Clutch Resilience", expanded=False):
    st.markdown("""
    Clutch Resilience measures how much a player's finishing performance CHANGES in 
    high-pressure moments compared to their pressure-weighted average.

    **HIGH PRESSURE FINISHING:**
    
    High-pressure moments are the top 25% most important shots for that player. Importance 
    is determined by a Pressure Index that considers:
    - Score state (are they trailing, tied, or leading? and by how much?)
    - Time remaining (how much could this goal change the outcome?)
    - Win Probability change (based on historical match data, how likely is this goal going 
      to change the team's win probability percentage?)
    
    **CALCULATION:**
    
    First, we calculate a Pressure-Weighted Baseline:
    - Pressure-Weighted Baseline = weighted mean(Goals - xG) across all shots, 
      where each shot is weighted by its Pressure Index

    Then, we measure Clutch Resilience as:
    - Clutch Resilience = High Pressure Finishing (%) - Pressure-Weighted Baseline (%)

    **INTERPRETATION:**

    - **+5.0pp** = Player performs 5.0 percentage points BETTER in high-pressure moments 
      compared to their pressure-adjusted season average
      - If their pressure-weighted baseline is +4%, high-pressure finishing is +9%
      - These are "clutch performers" who elevate when stakes are highest

    - **-3.0pp** = Player performs 3.0 percentage points WORSE in high-pressure moments
      - Finishing declines in crucial moments
      - May underperform when team needs them most

    - **0pp** = Pressure-neutral
      - No change in performance based on pressure

    **WHY THIS MATTERS:**
    
    Identifies who delivers in decisive moments. Essential for teams fighting to turn the 
    needle in their favor in games when margins are so small.
    """)

with st.expander("How to Use This for Recruitment", expanded=False):
    st.markdown("""
    This dashboard reveals THREE dimensions:

    **1. BASE FINISHING ABILITY**
    - "Is this player naturally good at converting chances?"
    - Shown by: Consistent Finishing Metric (x-axis)

    **2. PERFORMANCE CONSISTENCY**
    - "Does this ability hold up when pressure increases?"
    - Shown by: Clutch Resilience (y-axis)
    - Positive = elevates under pressure
    - Negative = struggles in crucial moments

    **3. PLAYER PROFILING**
    - "What kind of player is this for my team's needs?"
    - Ex. Consistent clinical striker that doesn't disappear in big games
    - Ex. Young unpolished forward that isn't negatively affected by pressure

    **THE RECRUITMENT ADVANTAGE:**

    Instead of asking: "How many goals did he score?"
    
    You can now ask:
    - "Will he deliver when we need him most?"
    - "Does his performance hold up under pressure or decline?"
    
    This transforms strikers from one-dimensional data points into multidimensional profiles, 
    allowing recruitment teams to make decisions based on resilience, consistency, and context,
    not just goal totals.
    """)

st.divider()

st.sidebar.markdown("### 🔍 Filters")

leagues = ['All']
if 'league' in qualified_forwards.columns:
    league_list = sorted([x for x in qualified_forwards['league'].dropna().unique() if pd.notna(x)])
    if len(league_list) > 0:
        leagues += league_list

# Debug: show what we found
if len(leagues) == 1:
    st.sidebar.warning(f"Debug: League column found but no valid leagues. Columns: {qualified_forwards.columns.tolist()}")

teams = ['All']
if 'team' in qualified_forwards.columns:
    teams += sorted(qualified_forwards[qualified_forwards['team'] != 'Unknown']['team'].unique().tolist())

nationalities = ['All']
if 'nationality' in qualified_forwards.columns:
    nationalities += sorted(qualified_forwards['nationality'].dropna().unique().tolist())

selected_league = st.sidebar.selectbox("League", leagues, index=0)
selected_team = st.sidebar.selectbox("Team", teams, index=0)
selected_nationality = st.sidebar.selectbox("Nationality", nationalities, index=0)
min_shots = st.sidebar.slider("Minimum Shots", 20, 120, 20, step=5)
max_age = st.sidebar.slider("Maximum Age", 18, 40, 35, step=1)

filtered_data = qualified_forwards.copy()

if selected_league != 'All' and 'league' in filtered_data.columns:
    filtered_data = filtered_data[filtered_data['league'] == selected_league]
if selected_team != 'All':
    filtered_data = filtered_data[filtered_data['team'] == selected_team]
if selected_nationality != 'All':
    filtered_data = filtered_data[filtered_data['nationality'] == selected_nationality]

filtered_data = filtered_data[filtered_data['shot_count'] >= min_shots]
filtered_data = filtered_data[filtered_data['age'] <= max_age]

st.sidebar.metric("Filtered Players", len(filtered_data))

st.divider()

st.markdown("### Finishing Quality vs Clutch Resilience")

col1, col2 = st.columns([3, 1])

with col1:
    filtered_data_plot = filtered_data.copy()
    filtered_data_plot['consistent_finishing_pct'] = filtered_data_plot['consistent_finishing_metric'] * 100
    filtered_data_plot['clutch_resilience_pct'] = filtered_data_plot['clutch_resilience'] * 100
    
    fig = px.scatter(
        filtered_data_plot,
        x='consistent_finishing_pct',
        y='clutch_resilience_pct',
        custom_data=['player_name', 'team', 'nationality', 'age', 'consistent_finishing_pct', 'clutch_resilience_pct', 'goals_total', 'xg_total', 'shot_count'],
        color='shot_count',
        color_continuous_scale='Viridis',
        title="",
        labels={
            'consistent_finishing_pct': 'Consistent Finishing Metric (%)',
            'clutch_resilience_pct': 'Clutch Resilience (pp)',
        }
    )

    fig.update_traces(
        hovertemplate='<b>%{customdata[0]}</b><br>' +
                      'Team: %{customdata[1]}<br>' +
                      'Nationality: %{customdata[2]}<br>' +
                      'Age: %{customdata[3]:.0f}<br>' +
                      'Consistent Finishing Metric: %{customdata[4]:.2f}%<br>' +
                      'Clutch Resilience: %{customdata[5]:.2f}pp<br>' +
                      'Total Goals: %{customdata[6]:.0f}<br>' +
                      'Expected Goals: %{customdata[7]:.2f}<br>' +
                      'Shots: %{customdata[8]:.0f}<extra></extra>'
    )

    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_xaxes(range=[-20, 20])
    fig.update_yaxes(range=[-20, 20])

    fig.update_traces(marker=dict(size=8))
    fig.update_layout(
        height=600,
        hovermode='closest',
        font=dict(size=11),
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**Quadrants:**")
    st.markdown("""
    **Top-Right**
    
    High Finishing + High Clutch
    
    **Top-Left**
    
    Low Finishing + High Clutch
    
    **Bottom-Right**
    
    High Finishing - Low Clutch
    
    **Bottom-Left**
    
    Low Finishing - Low Clutch
    """)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Top Finishers")
    top_finishers = filtered_data.nlargest(10, 'consistent_finishing_metric')[
        ['player_name', 'team', 'consistent_finishing_metric', 'clutch_resilience', 'shot_count', 'goals_total']
    ].copy()
    top_finishers.columns = ['Player', 'Team', 'Finishing', 'Clutch', 'Shots', 'Goals']
    
    top_finishers['Finishing'] = top_finishers['Finishing'].apply(
        lambda x: f"{x*100:+.2f}% ({x:+.4f})"
    )
    top_finishers['Clutch'] = top_finishers['Clutch'].apply(
        lambda x: f"{x*100:+.2f}pp ({x:+.4f})"
    )
    
    st.dataframe(top_finishers, use_container_width=True, hide_index=True)

with col2:
    st.markdown("### Top Clutch Performers")
    top_clutch = filtered_data.nlargest(10, 'clutch_resilience')[
        ['player_name', 'team', 'consistent_finishing_metric', 'clutch_resilience', 'shot_count', 'goals_total']
    ].copy()
    top_clutch.columns = ['Player', 'Team', 'Finishing', 'Clutch', 'Shots', 'Goals']
    
    top_clutch['Finishing'] = top_clutch['Finishing'].apply(
        lambda x: f"{x*100:+.2f}% ({x:+.4f})"
    )
    top_clutch['Clutch'] = top_clutch['Clutch'].apply(
        lambda x: f"{x*100:+.2f}pp ({x:+.4f})"
    )
    
    st.dataframe(top_clutch, use_container_width=True, hide_index=True)

st.divider()

st.markdown("### 🔍 Player Details")

player_names = sorted(filtered_data['player_name'].unique())
selected_player_name = st.selectbox(
    "Select Player (Start typing to search)",
    player_names,
    index=0
)

player_data = filtered_data[filtered_data['player_name'] == selected_player_name].iloc[0]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<p class='metric-small'>Player Name</p><p class='player-name-small'>{player_data['player_name']}</p>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<p class='metric-small'>Team</p><p class='team-name-small'>{player_data['team']}</p>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<p class='metric-small'>Nationality</p><p class='player-name-small'>{player_data['nationality']}</p>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<p class='metric-small'>Age</p><p class='player-name-small'>{int(player_data['age'])}</p>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    finishing_value = player_data['consistent_finishing_metric']
    st.metric(
        "Consistent Finishing Metric",
        f"{finishing_value*100:+.2f}%",
        f"({finishing_value:+.4f})",
        delta_color="off"
    )

with col2:
    clutch_value = player_data['clutch_resilience']
    st.metric(
        "Clutch Resilience",
        f"{clutch_value*100:+.2f}pp",
        f"({clutch_value:+.4f})",
        delta_color="off"
    )

with col3:
    st.metric("Total Shots", int(player_data['shot_count']))

with col4:
    st.metric("Goals Scored", int(player_data['goals_total']))

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Expected Goals (xG)", f"{player_data['xg_total']:.2f}")

with col2:
    goals_vs_xg = player_data['goals_total'] - player_data['xg_total']
    st.metric("Goals vs xG", f"{goals_vs_xg:+.2f}")

with col3:
    st.metric("High Pressure Finishing", f"{player_data['high_pressure_finishing_pct']:+.2f}%")

st.divider()

st.markdown("### Comparison Chart")

col1, col2 = st.columns(2)

with col1:
    player1_name = st.selectbox("Player 1 (Start typing to search)", player_names, key="player1", index=0)

with col2:
    player2_name = st.selectbox("Player 2 (Start typing to search)", player_names, key="player2", index=1 if len(player_names) > 1 else 0)

if player1_name and player2_name and player1_name != player2_name:
    p1 = filtered_data[filtered_data['player_name'] == player1_name].iloc[0]
    p2 = filtered_data[filtered_data['player_name'] == player2_name].iloc[0]
    
    comparison_data = pd.DataFrame({
        player1_name: [
            f"{p1['consistent_finishing_metric']*100:+.2f}% ({p1['consistent_finishing_metric']:+.4f})",
            f"{p1['clutch_resilience']*100:+.2f}pp ({p1['clutch_resilience']:+.4f})",
            f"{int(p1['shot_count'])}",
            f"{int(p1['goals_total'])}",
            f"{p1['xg_total']:.2f}",
            f"{int(p1['age'])}",
            p1['team'],
            p1['nationality'],
        ],
        player2_name: [
            f"{p2['consistent_finishing_metric']*100:+.2f}% ({p2['consistent_finishing_metric']:+.4f})",
            f"{p2['clutch_resilience']*100:+.2f}pp ({p2['clutch_resilience']:+.4f})",
            f"{int(p2['shot_count'])}",
            f"{int(p2['goals_total'])}",
            f"{p2['xg_total']:.2f}",
            f"{int(p2['age'])}",
            p2['team'],
            p2['nationality'],
        ]
    }, index=[
        'Consistent Finishing Metric',
        'Clutch Resilience',
        'Shots',
        'Goals',
        'xG',
        'Age',
        'Team',
        'Nationality'
    ])
    
    st.dataframe(comparison_data, use_container_width=True)
    
else:
    st.info("Select two different players to compare.")

st.divider()

st.markdown("### Top Clutch Moments of the Season")

goals = enriched_shots_all[enriched_shots_all['is_goal'] == 1].copy()
goals_sorted = goals.nlargest(15, 'pressure_index')

if len(goals_sorted) > 0:
    clutch_moments_data = []
    
    for idx, goal in goals_sorted.iterrows():
        match_id = goal['match_id']
        
        if match_id in match_lookup:
            match_info = match_lookup[match_id]
            home_team = match_info['home_team']
            away_team = match_info['away_team']
            home_team_id = match_info['home_team_id']
            away_team_id = match_info['away_team_id']
            
            player_team_id = goal['team_id']
            if player_team_id == home_team_id:
                player_team = home_team
                opponent = away_team
            else:
                player_team = away_team
                opponent = home_team
            
            matchup = f"{player_team} vs {opponent}"
        else:
            matchup = "Unknown"
            player_team = "Unknown"
        
        clutch_moments_data.append({
            'Player': goal['player_name'],
            'Team': player_team,
            'Matchup': matchup,
            'Competition': goal['competition_name'],
            'Match Situation': f"{'Trailing' if goal['goal_difference_at_shot'] < 0 else 'Tied' if goal['goal_difference_at_shot'] == 0 else 'Leading'} {abs(int(goal['goal_difference_at_shot']))}",
            'Minute': int(goal['minute']),
            'xG': round(goal['xg'], 3),
            'Pressure Index': round(goal['pressure_index'], 3),
        })
    
    clutch_moments = pd.DataFrame(clutch_moments_data)
    st.dataframe(clutch_moments, use_container_width=True, hide_index=True)
else:
    st.info("No goals found in current filters.")

st.divider()

st.markdown("""
---
**About This Dashboard:**
- **Data Source:** Top 5 European Leagues (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)
- **Time Period:** 2025/26 Season
- **Methodology:** Pressure-adjusted finishing analysis

**For detailed methodology, visit the Methodology page.** →
""")
