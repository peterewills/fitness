# Fitness Analysis

Personal fitness tracking and analysis notebooks.

## Notebooks

### `progressive_overload.ipynb`
Analyzes workout data from the Strong app to track progressive overload. Compares each exercise session to the previous session, visualizing whether weight/reps progressed, regressed, or stayed neutral.

### `weight_and_nutrition_analysis.ipynb`
Tracks weight measurements and nutrition data. Shows weekly averages for weight and calorie intake, calculates implied energy expenditure from weight changes.

## Data

Data is organized by source with timestamped filenames:

```
data/
  my-fitness-pal/
    measurement_YYYYMMDD_HHMM.csv
    nutrition_YYYYMMDD_HHMM.csv
  strava/
    activities_YYYYMMDD_HHMM.csv
  strong/
    workouts_YYYYMMDD_HHMM.csv
```

Source data comes from:
- **MyFitnessPal**: `File-Export-*` folders in Downloads
- **Strava**: `export_*` folders in Downloads (full data export, only `activities.csv` is used)
- **Strong**: `strong_workouts.csv` in Downloads

The notebooks auto-discover the latest export folders from `~/Downloads` and copy them to `data/`.
