# Soccer Analysis, Prediction & Suggestion App — Phase Plan

A Streamlit-based soccer analysis and prediction platform using **Python, pandas, and NumPy**, with a professional **terminal/hacker-style UI** in comfortable dark colors.

## Cost Policy: Fully Free, No Subscriptions

This project must be **fully free to build, run, and deploy**. It must use only free and open-source software, permanently free API tiers, free public datasets, and free hosting.

**Zero-budget rules:**

- No paid subscriptions.
- No paid API plans.
- No paid data providers.
- No paid live-score add-ons.
- No paid cloud hosting.
- No paid databases.
- No paid monitoring or analytics services.
- No hidden usage charges.
- No services that require adding a payment card.
- No reliance on paid trials or features that become paid later.

If a service offers both free and paid tiers, use **only its permanently free tier**. If the free tier is insufficient, reduce scope, cache data locally, refresh less frequently, or use a free alternative. The app must never require the developer or user to enter payment details.

## Tech Stack

| Area | Technology | Cost |
|---|---|---|
| UI | Streamlit | Free, open source |
| Data processing | pandas, NumPy | Free, open source |
| Visualization | Plotly or Altair | Free, open source |
| Modeling | scikit-learn, Statsmodels | Free, open source |
| Storage | SQLite | Free, open source |
| Data formats | CSV, JSON, API responses | Free |
| Scheduling | APScheduler or cron | Free |
| Version control | Git + GitHub free tier | Free |
| Deployment | Streamlit Community Cloud | Free for public apps |
| Fixtures/results | football-data.org free tier | Free forever plan |
| Supplementary football data | API-Football free tier, Football-Data.co.uk CSVs, FBref, Understat, Transfermarkt | Free |
| Weather | Open-Meteo | Free |
| Maps/distance | OpenStreetMap/Nominatim | Free |

## UI Direction: Terminal Hacker Theme

Use a dark, terminal-inspired interface with a professional and comfortable palette:

- Background: `#0B0F14` or `#101418`
- Panel background: `#151B22`
- Primary text: `#D7E3EE`
- Muted text: `#7C8B99`
- Accent green: `#4ADE80`
- Secondary accent cyan: `#38BDF8`
- Warning amber: `#FBBF24`
- Risk red: `#F87171`
- Border/divider: `#22303B`

Design principles:

- Monospace fonts for metrics, tables, logs, and model output.
- Rounded panels with subtle borders rather than harsh neon effects.
- Clear hierarchy: match header, probability panel, key drivers, data quality, suggestion.
- Avoid excessive bright green text; use accent colors sparingly for readability.
- Include a terminal-style status bar showing data freshness, model version, and last update time.

---

## Phase 0 — Project Setup and Foundations

**Goal:** Establish a clean, scalable project structure and development workflow.

### Tasks

- Create a GitHub repository and folder structure.
- Set up a Python virtual environment.
- Install Streamlit, pandas, NumPy, requests, Plotly, scikit-learn, and SQLite dependencies.
- Create `.env.example` for free API keys and configuration.
- Add `requirements.txt`, `README.md`, and `.gitignore`.
- Define coding standards, folder conventions, and Git branching workflow.
- Create the Streamlit app skeleton with a terminal-style theme.
- Build reusable UI components:
  - Header/status bar
  - Metric card
  - Probability panel
  - Data-quality indicator
  - Model-explanation panel

### Suggested Structure

```text
soccer-prediction-app/
├── app/
│   ├── main.py
│   ├── theme.py
│   ├── components/
│   ├── pages/
│   └── utils/
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
├── src/
│   ├── ingestion/
│   ├── processing/
│   ├── features/
│   ├── models/
│   ├── prediction/
│   └── suggestions/
├── notebooks/
├── tests/
├── config/
├── requirements.txt
├── plan.md
└── README.md
```

### Deliverables

- Running empty Streamlit dashboard.
- Terminal-style theme applied.
- Project skeleton committed to GitHub.

---

## Phase 1 — Core Match and Team Data

**Goal:** Ingest foundational fixtures, results, standings, and basic team statistics.

### MVP League Coverage

Start with the following three leagues:

- English Premier League (EPL)
- Bundesliga
- Italian Serie A

Do not add more leagues until the app can reliably:
- Ingest fixtures and results
- Store historical matches
- Calculate team form
- Generate baseline predictions
- Stay within free API request limits

Additional leagues may be added later, prioritized by free data coverage:
- Bundesliga
- Ligue 1
- Primeira Liga
- Eredivisie
- Major League Soccer

### Data to Collect

- Fixtures, kickoff times, venues, competitions, and seasons.
- Historical results and scores.
- League tables and standings.
- Basic match statistics: goals, shots, possession, corners, cards, and fouls.
- Home/away records.
- Team form: last 5, 10, and 20 matches.

### Free Sources

Use only permanently free sources:

- football-data.org free tier
- Football-Data.co.uk CSV files
- openfootball
- FBref
- League official websites

Do not use paid football-data.org packages, paid live-score add-ons, or paid historical-data plans.

### Tasks

- Build API/CSV ingestion modules.
- Create standardized schemas for matches, teams, leagues, and seasons.
- Store raw data in `data/raw/`.
- Clean and normalize team names, league names, dates, and venues.
- Create processed CSV/SQLite tables.
- Build fixtures, results, standings, and team-profile pages.
- Add data-freshness indicators.
- Cache API responses locally to stay within free-tier limits.

### Deliverables

- Historical match database.
- Team and league dashboard.
- Fixture calendar with filters by league, date, and team.

---

## Phase 2 — Player Availability and Rotation Intelligence

**Goal:** Estimate player availability, likely starters, squad depth, and the performance impact of absences.

### Data to Collect

- Confirmed lineups and predicted XIs.
- Formations, captain, tactical roles, and bench strength.
- Injury type, injury date, expected return date, recurrence risk, and minutes restriction.
- Suspensions and yellow-card accumulation.
- Player minutes load over 7–14 days.
- Back-to-back match exposure.
- Recent substitution patterns.
- International call-ups, minutes played, return dates, and travel burden.
- Transfers, loans, departures, and squad changes.

### Free Sources

Use only permanently free sources:

- football-data.org free tier
- API-Football free tier
- Transfermarkt
- FBref
- Premier Injuries
- PhysioRoom
- Club websites
- National federation sites
- Wikipedia for supplemental historical data

Do not purchase API-Football paid tiers or any paid injury/lineup data service. Cache responses locally and refresh within the free request limits.

### Tasks

- Create player, squad, injury, suspension, lineup, and availability tables.
- Build a starter-probability model using:
  - Recent starts
  - Minutes played
  - Position and tactical role
  - Injury/suspension status
  - Rotation history
  - Fixture congestion
- Build a squad-depth score for each position group.
- Create an availability-impact score estimating how much a missing player affects attack, midfield, defense, and set pieces.
- Add international-duty and travel-fatigue indicators.
- Build pages for:
  - Team squad depth
  - Injury/suspension tracker
  - Predicted XI
  - Rotation risk
  - Availability impact

### Deliverables

- Player availability database.
- Predicted XI engine.
- Key-player absence impact score.
- Squad rotation and fatigue dashboard.

---

## Phase 3 — Event-Level Performance Data

**Goal:** Move beyond basic box-score statistics and measure underlying team quality.

### Data to Collect

- Shot location, body part, shot type, and shot outcome.
- Defensive pressure at shot time.
- Goalkeeper positioning where available.
- Chance origin: open play, counterattack, set piece, or penalty.
- Expected goals for and against.
- xG/xGA split by:
  - Game state
  - Opponent strength
  - Time period
  - Home/away
- Progressive passes, passes under pressure, PPDA, pressing intensity, build-up patterns, and defensive-line height.
- Set-piece detail: corners, free kicks, aerial duels, delivery quality, and key set-piece takers.
- Cards, fouls, penalties, and referee tendencies.

### Free Sources

Use only permanently free sources:

- FBref
- Understat
- Football-Data.co.uk
- Sofascore/FotMob for manually collected or supplementary data
- Open football datasets

Do not subscribe to paid event-data, shot-data, or advanced-analytics providers.

### Tasks

- Build ingestion pipelines for shot-level and match-level event data.
- Calculate rolling xG, xGA, shot quality, chance creation, and defensive metrics.
- Create team-style profiles:
  - High press vs. low block
  - Direct vs. possession-based
  - Counterattacking tendency
  - Set-piece strength/weakness
- Build referee and disciplinary profiles.
- Create matchup features, such as:
  - Pressing team vs. poor ball-progressor
  - Set-piece-strong team vs. weak aerial defender
  - High-line defense vs. fast counterattack
- Add visualizations for xG trend, shot maps, pressing intensity, and matchup strengths.

### Deliverables

- Event-level analytics database.
- Team style and matchup analysis pages.
- Rolling form and underlying-performance metrics.

---

## Phase 4 — Context and Environment Modeling

**Goal:** Add situational variables that affect totals, cards, corners, handicaps, and match outcomes.

### Data to Collect

- Weather forecast: temperature, humidity, wind speed, rain, and visibility.
- Pitch condition and surface type.
- Stadium location, altitude, pitch dimensions, and home/away performance splits.
- Travel distance and estimated travel time.
- Days since last match.
- Kickoff time.
- Fixture congestion from league, cup, and continental competitions.
- Motivation context:
  - Title race
  - Relegation battle
  - European qualification
  - Cup priority
  - Dead-rubber matches

### Free Sources

Use only permanently free sources:

- Open-Meteo for weather
- OpenStreetMap/Nominatim for stadium coordinates and distance
- OpenStreetMap-based routing or haversine distance calculations for travel estimates
- football-data.org free tier for fixtures and competitions
- UEFA.com and league sites for continental/cup schedules
- FBref for standings and performance context

Do **not** use Google Maps if it requires enabling billing or adding a payment card. Use OpenStreetMap/Nominatim and local distance calculations instead.

### Tasks

- Store stadium coordinates, altitude, surface, and venue metadata.
- Connect weather forecasts to stadium coordinates and kickoff time.
- Calculate travel distance, rest days, congestion, and time-zone impact.
- Create motivation and schedule-context flags.
- Quantify venue effects using historical home/away performance.
- Build a context-adjustment layer that modifies baseline team ratings.

### Deliverables

- Context database.
- Weather, travel, rest, and venue dashboards.
- Context-adjusted team strength ratings.

---

## Phase 5 — Prediction Engine

**Goal:** Produce calibrated, explainable soccer match predictions.

### Prediction Targets

- Match result: home win, draw, away win.
- Expected goals for each team.
- Most likely scorelines.
- Over/under goal probabilities.
- Both teams to score.
- Asian handicap estimates.
- Corners and cards, after sufficient data is available.

### Modeling Approach

Start simple, validate, then improve:

1. **Baseline model:** Poisson model using attack strength, defense strength, and home advantage.
2. **Improved model:** Dixon-Coles adjustment for low-scoring matches.
3. **Rating model:** Elo or power ratings updated after each match.
4. **Context model:** Adjust ratings for rest, travel, weather, motivation, and availability.
5. **Machine-learning layer:** Gradient boosting or regularized regression using engineered features.
6. **Ensemble:** Combine statistical and ML models with validation-based weights.

### Feature Groups

- Team attack and defense ratings.
- Recent xG and xGA.
- Home/away splits.
- Rest days and congestion.
- Travel and timezone impact.
- Weather and venue conditions.
- Key-player availability and squad depth.
- Predicted XI strength.
- Tactical matchup indicators.
- Referee and discipline tendencies.
- Motivation and competition context.

### Tasks

- Create a feature-engineering pipeline.
- Split data chronologically for training, validation, and testing.
- Train a baseline Poisson/Dixon-Coles model.
- Add Elo or power ratings.
- Add context and availability adjustments.
- Train an ML model only after a reliable baseline exists.
- Evaluate using log loss, Brier score, calibration curves, and historical backtests.
- Store model version, training date, feature list, and evaluation metrics.
- Generate an explanation for every prediction:
  - Team strength
  - Form
  - Availability impact
  - Context adjustments
  - Value signal

### Deliverables

- Prediction module.
- Match prediction page.
- Model performance dashboard.
- Prediction explanation panel.

---

## Phase 6 — Suggestions and Value Detection

**Goal:** Convert predictions into disciplined, transparent suggestions rather than blind tips.

### Core Logic

Compare model probability with implied probability from available odds:

\[
\text{Implied Probability} = \frac{1}{\text{Decimal Odds}}
\]

A potential value opportunity exists when:

\[
\text{Model Probability} \times \text{Decimal Odds} > 1
\]

Apply minimum edge and confidence filters before displaying a suggestion.

### Suggestion Types

- Match result
- Double chance
- Over/under goals
- Both teams to score
- Asian handicap
- Team totals
- Corners
- Cards
- Safer conservative selections
- Higher-risk value selections

### Tasks

- Build odds ingestion and normalization using free CSV/data sources.
- Calculate implied probability, model edge, expected value, and confidence.
- Add filters:
  - Minimum edge
  - Minimum model confidence
  - Data-quality threshold
  - League coverage
  - Market type
- Create a suggestion card showing:
  - Selection
  - Model probability
  - Market odds
  - Edge
  - Confidence
  - Main supporting factors
  - Risk warnings
- Add a responsible-use disclaimer.
- Track hypothetical suggestions and outcomes for evaluation.
- Never promise guaranteed profits.

### Deliverables

- Value-suggestion engine.
- Daily match suggestion dashboard.
- Suggestion history and performance tracker.
- Responsible-gambling notice.

---

## Phase 7 — Streamlit Dashboard and User Experience

**Goal:** Turn the backend into a polished, usable product.

### Pages

- Home / Today’s Matches
- Match Analysis
- Team Profiles
- Player Availability
- Injuries & Suspensions
- League Standings
- Predictions
- Suggestions
- Model Performance
- Data Sources & Coverage
- Settings

### Key UX Features

- League and date filters.
- Team search.
- Match comparison view.
- Probability bars for home/draw/away.
- Expected-goals comparison.
- Availability-impact summary.
- Weather, rest, travel, and motivation indicators.
- Model confidence and data-quality badges.
- Export prediction report as CSV or Markdown.
- Mobile-responsive layout.

### Deliverables

- Complete multi-page Streamlit application.
- Consistent terminal-style design system.
- User-ready dashboards and reports.

---

## Phase 8 — Testing, Validation, and Deployment

**Goal:** Ensure the app is reliable, reproducible, and production-ready without any cost.

### Tasks

- Write unit tests for data cleaning, feature engineering, and prediction functions.
- Add integration tests for ingestion pipelines.
- Validate predictions on unseen chronological data.
- Monitor model calibration and performance over time.
- Add logging and error handling.
- Deploy to **Streamlit Community Cloud** using its free public-app tier.
- Do not use paid VPS hosting, paid Render/Railway plans, or any host requiring a payment card.
- Docker is optional; it is not required for the free deployment path.
- Set up scheduled data refreshes within free API limits.
- Add backup and database-migration strategy using free tools.
- Create user documentation.

### Deliverables

- Tested and deployed application.
- Automated data-update workflow.
- Model monitoring dashboard.
- Deployment documentation.

---

## Phase 9 — Advanced Improvements

**Goal:** Increase predictive sophistication after the core product is stable, while remaining free.

### Potential Enhancements

- Live in-match prediction updates using only free data sources and their rate limits.
- Player-level expected goals and expected assists.
- Lineup simulation using Monte Carlo methods.
- Bayesian player and team ratings.
- Manager and tactical-change effects.
- Market-movement analysis using free odds data.
- Multi-model ensembles.
- Custom user models and weighting.
- Alerts for lineup announcements, injuries, weather changes, and odds movement.
- Historical simulation and backtesting tools.
- Optional user accounts and saved preferences using free authentication options.

---

## Recommended Build Order

1. Phase 0: Setup and UI foundation.
2. Phase 1: Fixtures, results, standings, and basic stats.
3. Phase 5.1: Basic Poisson prediction model.
4. Phase 2: Player availability and rotation.
5. Phase 3: Event-level and xG data.
6. Phase 4: Context and environment data.
7. Phase 5.2: Full prediction engine.
8. Phase 6: Suggestions and value detection.
9. Phase 7: Dashboard polish.
10. Phase 8: Testing and deployment.
11. Phase 9: Advanced features.

## Zero-Cost Success Criteria

- The complete app can be built, run, and deployed without any payment method.
- No feature depends on a paid subscription, trial, credit card, or hidden usage charge.
- All external data comes from permanently free APIs, public CSVs, or manually collected public information.
- API usage stays within permanent free-tier limits through caching and scheduled refreshes.
- Deployment uses Streamlit Community Cloud’s free public-app tier.
- If a source removes or restricts its free tier, replace it with another free source rather than upgrading to a paid plan.

## Success Criteria

- Accurate, calibrated match probabilities.
- Clear explanation of why each prediction was made.
- Reliable ingestion of lineups, injuries, fixtures, results, and context data.
- Professional terminal-style UI that remains readable and comfortable.
- Transparent suggestion logic with no guaranteed-profit claims.
- Reproducible data pipelines and model training workflow.
