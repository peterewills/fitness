"""
Eating strategy simulator.

Compares hypothetical eating strategies against actual calorie intake,
using historical cycling data from Strava.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
START_DATE = "2025-10-09"
END_DATE = "2026-03-01"

# Strategy parameters
BASE_CALORIES = 2900
CYCLING_MULTIPLIER = 0.70


def load_cycling_data() -> pd.DataFrame:
    """Load and aggregate daily cycling calories from Strava."""
    strava_file = sorted(DATA_DIR.glob("strava/activities_*.csv"))[-1]
    strava_df = pd.read_csv(strava_file)
    strava_df["Date"] = pd.to_datetime(
        strava_df["Activity Date"], format="%b %d, %Y, %I:%M:%S %p"
    )

    cycling_df = strava_df[
        strava_df["Activity Type"].isin(["Ride", "Virtual Ride", "VirtualRide"])
    ].copy()
    cycling_df = cycling_df[cycling_df["Date"] >= START_DATE]
    cycling_df["Cycling_Calories"] = pd.to_numeric(
        cycling_df["Calories"], errors="coerce"
    ).fillna(0)

    cycling_df["Day"] = cycling_df["Date"].dt.date
    daily_cycling = cycling_df.groupby("Day")["Cycling_Calories"].sum().reset_index()
    daily_cycling.columns = ["Date", "Cycling_Calories"]
    daily_cycling["Date"] = pd.to_datetime(daily_cycling["Date"])

    return daily_cycling


def load_nutrition_data() -> pd.DataFrame:
    """Load and aggregate daily actual calories from MyFitnessPal."""
    nutrition_file = sorted(DATA_DIR.glob("my-fitness-pal/nutrition_*.csv"))[-1]
    nutrition_df = pd.read_csv(nutrition_file)
    nutrition_df["Date"] = pd.to_datetime(nutrition_df["Date"])
    nutrition_df = nutrition_df[nutrition_df["Date"] >= START_DATE]

    daily_nutrition = nutrition_df.groupby("Date")["Calories"].sum().reset_index()
    daily_nutrition.columns = ["Date", "Actual_Calories"]

    return daily_nutrition


def build_daily_dataframe(
    daily_cycling: pd.DataFrame,
    daily_nutrition: pd.DataFrame,
) -> pd.DataFrame:
    """Build complete daily dataframe with cycling, strategy, and actual calories."""
    date_range = pd.date_range(start=START_DATE, end=END_DATE, freq="D")
    df = pd.DataFrame({"Date": date_range})

    df = df.merge(daily_cycling, on="Date", how="left")
    df = df.merge(daily_nutrition, on="Date", how="left")
    df["Cycling_Calories"] = df["Cycling_Calories"].fillna(0)

    df["Hypothetical_Eating"] = BASE_CALORIES + CYCLING_MULTIPLIER * df["Cycling_Calories"]
    df["Hypothetical_Net"] = df["Hypothetical_Eating"] - df["Cycling_Calories"]
    df["Actual_Net"] = df["Actual_Calories"] - df["Cycling_Calories"]
    df["Diff"] = df["Actual_Calories"] - df["Hypothetical_Eating"]

    return df


def compute_weekly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate daily data to weekly averages."""
    df = df.copy()
    df["Week"] = df["Date"].dt.to_period("W-SUN")

    weekly = df.groupby("Week").agg({
        "Cycling_Calories": "mean",
        "Hypothetical_Eating": "mean",
        "Actual_Calories": "mean",
        "Diff": "mean",
        "Hypothetical_Net": "mean",
        "Actual_Net": "mean",
    }).round(0)

    return weekly


def print_weekly_summary(weekly: pd.DataFrame) -> None:
    """Print formatted weekly summary table."""
    print(f"\nStrategy: {BASE_CALORIES} + {int(CYCLING_MULTIPLIER*100)}% of cycling calories\n")

    # Header
    print(
        f"| {'Week':<21} "
        f"| {'Cycling':>8} "
        f"| {'Hyp Eat':>8} "
        f"| {'Act Eat':>8} "
        f"| {'Diff':>8} "
        f"| {'Hyp Net':>8} "
        f"| {'Act Net':>8} |"
    )
    print(f"|{'-'*23}|{'-'*10}|{'-'*10}|{'-'*10}|{'-'*10}|{'-'*10}|{'-'*10}|")

    for week, row in weekly.iterrows():
        actual_eating = f"{row['Actual_Calories']:.0f}" if pd.notna(row["Actual_Calories"]) else "—"
        actual_net = f"{row['Actual_Net']:.0f}" if pd.notna(row["Actual_Net"]) else "—"
        diff = f"{row['Diff']:+.0f}" if pd.notna(row["Diff"]) else "—"
        print(
            f"| {str(week):<21} "
            f"| {row['Cycling_Calories']:>8.0f} "
            f"| {row['Hypothetical_Eating']:>8.0f} "
            f"| {actual_eating:>8} "
            f"| {diff:>8} "
            f"| {row['Hypothetical_Net']:>8.0f} "
            f"| {actual_net:>8} |"
        )

    print(f"|{'-'*23}|{'-'*10}|{'-'*10}|{'-'*10}|{'-'*10}|{'-'*10}|{'-'*10}|")
    print(
        f"| {'**AVERAGE**':<21} "
        f"| {weekly['Cycling_Calories'].mean():>8.0f} "
        f"| {weekly['Hypothetical_Eating'].mean():>8.0f} "
        f"| {weekly['Actual_Calories'].mean():>8.0f} "
        f"| {weekly['Diff'].mean():>+8.0f} "
        f"| {weekly['Hypothetical_Net'].mean():>8.0f} "
        f"| {weekly['Actual_Net'].mean():>8.0f} |"
    )


def main():
    daily_cycling = load_cycling_data()
    daily_nutrition = load_nutrition_data()
    df = build_daily_dataframe(daily_cycling, daily_nutrition)
    weekly = compute_weekly_summary(df)
    print_weekly_summary(weekly)

    # Save daily CSV
    output_file = DATA_DIR / "strategy_output.csv"
    output_df = df[[
        "Date",
        "Cycling_Calories",
        "Hypothetical_Eating",
        "Actual_Calories",
        "Diff",
        "Hypothetical_Net",
        "Actual_Net",
    ]].copy()
    output_df.columns = [
        "Date",
        "Cycling Calories",
        "Hypothetical Eating",
        "Actual Eating",
        "Diff",
        "Hypothetical Net",
        "Actual Net",
    ]
    output_df["Date"] = output_df["Date"].dt.strftime("%Y-%m-%d")
    output_df = output_df.round(0)
    output_df.to_csv(output_file, index=False)
    print(f"\nSaved daily data to {output_file}")


if __name__ == "__main__":
    main()
