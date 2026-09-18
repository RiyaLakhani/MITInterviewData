import os
import argparse
import pandas as pd
from scipy.stats import ttest_rel, f_oneway


def read_score_csv(csv_path):
    df = pd.read_csv(csv_path)

    df["source_file"] = os.path.basename(csv_path)

    # Rename your actual CSV columns into the names the analysis expects
    if "participant_id" in df.columns:
        df = df.rename(columns={"participant_id": "participant"})

    if "assumed_gender" in df.columns:
        df = df.rename(columns={"assumed_gender": "gender"})

    # Your CSV already has condition, but we need prompt_type too
    # condition values are probably: non_gendered, gendered
    if "prompt_type" not in df.columns:
        if "condition" in df.columns:
            df["prompt_type"] = df["condition"]

    # Now create the combined condition used by the pivot/t-tests:
    # gendered_male, gendered_female, non_gendered_none
    df["condition"] = df["prompt_type"] + "_" + df["gender"]

    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["score"])

    return df


def run_analysis_for_file(df, source_file):
    test_results = []

    print("\n====================================")
    print(f"FILE: {source_file}")
    print("====================================")

    print("\nDATAFRAME:")
    print(df[["participant", "prompt_type", "gender", "score", "condition"]].head())

    avg_scores = (
        df.groupby("condition")["score"]
          .mean()
          .reset_index()
    )

    avg_scores["source_file"] = source_file

    print("\nAVERAGE SCORES:")
    print(avg_scores[["condition", "score"]])

    pivot = df.pivot_table(
        index="participant",
        columns="condition",
        values="score",
        aggfunc="mean"
    )

    print("\nPIVOT TABLE:")
    print(pivot.head())

    pivot_for_csv = pivot.reset_index()
    pivot_for_csv["source_file"] = source_file

    if "gendered_male" in pivot.columns and "gendered_female" in pivot.columns:
        pair_df = pivot[["gendered_male", "gendered_female"]].dropna()

        t_stat, p_value = ttest_rel(
            pair_df["gendered_male"],
            pair_df["gendered_female"]
        )

        print("\nPAIRED T-TEST: male vs female")
        print(f"t = {t_stat}")
        print(f"p = {p_value}")

        test_results.append({
            "source_file": source_file,
            "test": "male vs female",
            "condition_1": "gendered_male",
            "condition_2": "gendered_female",
            "t_statistic": t_stat,
            "p_value": p_value,
            "n": len(pair_df)
        })

    if "gendered_male" in pivot.columns and "non_gendered_none" in pivot.columns:
        pair_df = pivot[["gendered_male", "non_gendered_none"]].dropna()

        t_stat, p_value = ttest_rel(
            pair_df["gendered_male"],
            pair_df["non_gendered_none"]
        )

        print("\nPAIRED T-TEST: male vs non-gendered")
        print(f"t = {t_stat}")
        print(f"p = {p_value}")

        test_results.append({
            "source_file": source_file,
            "test": "male vs non-gendered",
            "condition_1": "gendered_male",
            "condition_2": "non_gendered_none",
            "t_statistic": t_stat,
            "p_value": p_value,
            "n": len(pair_df)
        })

    if "gendered_female" in pivot.columns and "non_gendered_none" in pivot.columns:
        pair_df = pivot[["gendered_female", "non_gendered_none"]].dropna()

        t_stat, p_value = ttest_rel(
            pair_df["gendered_female"],
            pair_df["non_gendered_none"]
        )

        print("\nPAIRED T-TEST: female vs non-gendered")
        print(f"t = {t_stat}")
        print(f"p = {p_value}")

        test_results.append({
            "source_file": source_file,
            "test": "female vs non-gendered",
            "condition_1": "gendered_female",
            "condition_2": "non_gendered_none",
            "t_statistic": t_stat,
            "p_value": p_value,
            "n": len(pair_df)
        })

    needed_conditions = [
        "gendered_female",
        "gendered_male",
        "non_gendered_none"
    ]

    if all(condition in pivot.columns for condition in needed_conditions):
        anova_df = pivot[needed_conditions].dropna()

        f_stat, p_value = f_oneway(
            anova_df["gendered_female"],
            anova_df["gendered_male"],
            anova_df["non_gendered_none"]
        )

        print("\nANOVA:")
        print(f"F = {f_stat}")
        print(f"p = {p_value}")

        test_results.append({
            "source_file": source_file,
            "test": "ANOVA",
            "condition_1": "gendered_female",
            "condition_2": "gendered_male",
            "condition_3": "non_gendered_none",
            "f_statistic": f_stat,
            "p_value": p_value,
            "n": len(anova_df)
        })

    return avg_scores, pivot_for_csv, pd.DataFrame(test_results)


def main():
    parser = argparse.ArgumentParser(
        description="Run score analysis on multiple CSV files."
    )

    parser.add_argument(
        "csv_files",
        nargs="+",
        help="One or more CSV files to process"
    )

    parser.add_argument(
        "--details_output",
        default="all_extracted_scores.csv"
    )

    parser.add_argument(
        "--averages_output",
        default="all_average_scores.csv"
    )

    parser.add_argument(
        "--pivot_output",
        default="all_pivot_tables.csv"
    )

    parser.add_argument(
        "--tests_output",
        default="all_tests.csv"
    )

    args = parser.parse_args()

    all_rows = []
    all_averages = []
    all_pivots = []
    all_tests = []

    for csv_file in args.csv_files:
        source_file = os.path.basename(csv_file)

        df = read_score_csv(csv_file)

        if df.empty:
            print(f"No valid scores found in {source_file}")
            continue

        avg_scores, pivot, test_results = run_analysis_for_file(df, source_file)

        all_rows.append(df)
        all_averages.append(avg_scores)
        all_pivots.append(pivot)
        all_tests.append(test_results)

    if not all_rows:
        print("No scores were found in any files.")
        return

    final_df = pd.concat(all_rows, ignore_index=True)
    final_averages = pd.concat(all_averages, ignore_index=True)
    final_pivots = pd.concat(all_pivots, ignore_index=True)
    final_tests = pd.concat(all_tests, ignore_index=True)

    final_df.to_csv(args.details_output, index=False)
    final_averages.to_csv(args.averages_output, index=False)
    final_pivots.to_csv(args.pivot_output, index=False)
    final_tests.to_csv(args.tests_output, index=False)

    print("\n====================================")
    print("SAVED OUTPUT FILES")
    print("====================================")
    print(f"Detailed dataframe saved to: {args.details_output}")
    print(f"Average scores saved to: {args.averages_output}")
    print(f"Pivot tables saved to: {args.pivot_output}")
    print(f"T-tests and ANOVA saved to: {args.tests_output}")


if __name__ == "__main__":
    main()