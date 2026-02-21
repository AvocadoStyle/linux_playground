"""
XLSX Test Report Analyzer - Uses local LLM (Ollama + Gemma2) to analyze
hardware test reports, spot failures, identify patterns, and generate
a feedback report.

Usage:
    poetry run python linux_playground/utils/tools/analyze_test_report.py <xlsx_file>
    poetry run python linux_playground/utils/tools/analyze_test_report.py  # uses default file
"""
import datetime
import sys
import os
from pathlib import Path

import pandas as pd
import ollama as ollama_client


MODEL = "gemma2:9b"
TOOLS_DIR = Path(__file__).parent


def load_xlsx(filepath: str) -> dict[str, pd.DataFrame]:
    """Load all sheets from the XLSX file."""
    print(f"  Loading: {filepath}")
    sheets = pd.read_excel(filepath, sheet_name=None)
    for name, df in sheets.items():
        print(f"  Sheet '{name}': {len(df)} rows x {len(df.columns)} cols")
    return sheets


def find_test_sheet(sheets: dict[str, pd.DataFrame]) -> tuple[str, pd.DataFrame]:
    """Find the main test data sheet (the one with 'Result' column)."""
    for name, df in sheets.items():
        if "Result" in df.columns and "FailErrCode" in df.columns:
            return name, df
    raise ValueError("No test data sheet found (expected 'Result' and 'FailErrCode' columns)")


def extract_summary(sheets: dict[str, pd.DataFrame]) -> str:
    """Extract info from Summary sheet if it exists."""
    for name, df in sheets.items():
        if name.lower() == "summary":
            return df.to_string(index=False)
    return "No summary sheet found"


def build_failure_analysis(df: pd.DataFrame) -> str:
    """Build a comprehensive text summary of failures for the LLM."""
    total = len(df)
    passes = len(df[df["Result"] == "Pass"])
    warnings = len(df[df["Result"] == "Warning"])
    fails_df = df[df["Result"] == "Fail"]
    fails = len(fails_df)

    lines = []
    lines.append("=" * 60)
    lines.append("TEST REPORT DATA SUMMARY")
    lines.append("=" * 60)

    # Overall stats
    lines.append(f"\n## Overall Results")
    lines.append(f"Total tests: {total}")
    lines.append(f"Pass: {passes} ({100*passes/total:.1f}%)")
    lines.append(f"Warning: {warnings} ({100*warnings/total:.1f}%)")
    lines.append(f"Fail: {fails} ({100*fails/total:.1f}%)")

    if fails == 0:
        lines.append("\nNo failures detected - all tests passed!")
        return "\n".join(lines)

    # Failure error code distribution
    lines.append(f"\n## Failure Types (FailErrCode)")
    for code, count in fails_df["FailErrCode"].value_counts().items():
        lines.append(f"  {code}: {count} occurrences ({100*count/fails:.1f}% of failures)")

    # Failures by power supply voltage
    lines.append(f"\n## Failures by Power Supply Voltage (Vps)")
    vps_fail = fails_df.groupby("Vps(WP)")["FailErrCode"].value_counts()
    for (vps, code), count in vps_fail.items():
        total_at_vps = len(df[df["Vps(WP)"] == vps])
        lines.append(f"  Vps={vps}V: {code} x{count} (out of {total_at_vps} tests at this voltage)")

    # Failures by input voltage
    lines.append(f"\n## Failures by Input Voltage (Vin)")
    vin_fail = fails_df.groupby("Vin(WP)")["FailErrCode"].value_counts()
    for (vin, code), count in vin_fail.items():
        lines.append(f"  Vin={vin}V: {code} x{count}")

    # Failures by output current
    lines.append(f"\n## Failures by Output Current (Iout)")
    iout_fail = fails_df.groupby("Iout(WP)")["FailErrCode"].value_counts()
    for (iout, code), count in iout_fail.items():
        lines.append(f"  Iout={iout}A: {code} x{count}")

    # Peak-to-peak voltage analysis for HIGH_OUTPUT_PP failures
    hopp = fails_df[fails_df["FailErrCode"] == "HIGH_OUTPUT_PP"]
    if len(hopp) > 0:
        lines.append(f"\n## HIGH_OUTPUT_PP Detail (Vout Peak-to-Peak)")
        lines.append(f"  Count: {len(hopp)}")
        lines.append(f"  Vout(PeakToPeak) range: {hopp['Vout(PeakToPeak)'].min():.3f}V - {hopp['Vout(PeakToPeak)'].max():.3f}V")
        lines.append(f"  Vout(PeakToPeak) mean: {hopp['Vout(PeakToPeak)'].mean():.3f}V")
        lines.append(f"  Vout(Meas) range: {hopp['Vout(Meas)'].min():.2f}V - {hopp['Vout(Meas)'].max():.2f}V")
        lines.append(f"  Vps(WP) range: {hopp['Vps(WP)'].min():.0f}V - {hopp['Vps(WP)'].max():.0f}V")
        lines.append(f"  Vin(WP) range: {hopp['Vin(WP)'].min():.0f}V - {hopp['Vin(WP)'].max():.0f}V")
        lines.append(f"  Iout(WP) range: {hopp['Iout(WP)'].min():.1f}A - {hopp['Iout(WP)'].max():.1f}A")

    # Peak-to-peak voltage analysis for HIGH_INPUT_PP failures
    hipp = fails_df[fails_df["FailErrCode"] == "HIGH_INPUT_PP"]
    if len(hipp) > 0:
        lines.append(f"\n## HIGH_INPUT_PP Detail (Vin Peak-to-Peak)")
        lines.append(f"  Count: {len(hipp)}")
        lines.append(f"  Vin(PeakToPeak) range: {hipp['Vin(PeakToPeak)'].min():.3f}V - {hipp['Vin(PeakToPeak)'].max():.3f}V")
        lines.append(f"  Vin(PeakToPeak) mean: {hipp['Vin(PeakToPeak)'].mean():.3f}V")
        lines.append(f"  Vps(WP) range: {hipp['Vps(WP)'].min():.0f}V - {hipp['Vps(WP)'].max():.0f}V")
        lines.append(f"  Vin(WP) range: {hipp['Vin(WP)'].min():.0f}V - {hipp['Vin(WP)'].max():.0f}V")
        lines.append(f"  Iout(WP) range: {hipp['Iout(WP)'].min():.1f}A - {hipp['Iout(WP)'].max():.1f}A")

    # Delta input error analysis
    die = fails_df[fails_df["FailErrCode"] == "DELTA_INPUT_ERROR"]
    if len(die) > 0:
        lines.append(f"\n## DELTA_INPUT_ERROR Detail")
        lines.append(f"  Count: {len(die)}")
        lines.append(f"  DeltaOPTVin range: {die['DeltaOPTVin'].min():.3f} - {die['DeltaOPTVin'].max():.3f}")
        lines.append(f"  DeltaOPTVin mean: {die['DeltaOPTVin'].mean():.3f}")
        lines.append(f"  Vps(WP) range: {die['Vps(WP)'].min():.0f}V - {die['Vps(WP)'].max():.0f}V")
        lines.append(f"  Vin(WP) range: {die['Vin(WP)'].min():.0f}V - {die['Vin(WP)'].max():.0f}V")

    # Sample failure reasons (unique)
    lines.append(f"\n## Sample Failure Messages")
    for reason in fails_df["FailReason"].dropna().unique()[:10]:
        lines.append(f"  - {reason}")

    # Anomaly detection: compare pass vs fail distributions
    lines.append(f"\n## Pass vs Fail Distribution Comparison")
    pass_df = df[df["Result"] == "Pass"]
    for col in ["Vout(Meas)", "Vin(PeakToPeak)", "Vout(PeakToPeak)", "DeltaOPTVin"]:
        if col in df.columns:
            p_mean = pass_df[col].mean()
            p_std = pass_df[col].std()
            f_mean = fails_df[col].mean()
            f_std = fails_df[col].std()
            lines.append(f"  {col}: Pass(mean={p_mean:.3f}, std={p_std:.3f}) vs Fail(mean={f_mean:.3f}, std={f_std:.3f})")

    # Efficiency comparison
    lines.append(f"\n## Efficiency Comparison (Pout/Pin)")
    for label, subset in [("Pass", pass_df), ("Fail", fails_df)]:
        valid = subset[(subset["Pin(Meas)"] > 0) & (subset["Pout(Meas)"].notna())]
        if len(valid) > 0:
            eff = (valid["Pout(Meas)"] / valid["Pin(Meas)"] * 100)
            lines.append(f"  {label}: mean={eff.mean():.1f}%, min={eff.min():.1f}%, max={eff.max():.1f}%")

    return "\n".join(lines)


def ask_llm(data_summary: str, summary_sheet: str) -> str:
    """Send the analysis to the LLM and get a feedback report."""
    prompt = f"""You are a hardware test report analyst for power converter products.
Analyze the following test data from a GEN4 S600A power converter verification test.

SUMMARY SHEET:
{summary_sheet}

DETAILED ANALYSIS:
{data_summary}

Based on this data, provide a comprehensive feedback report covering:

1. **Executive Summary**: Brief overview of the test results and overall health.

2. **Failure Analysis**: For each failure type (HIGH_OUTPUT_PP, HIGH_INPUT_PP, DELTA_INPUT_ERROR):
   - What is this failure and what does it indicate?
   - Under which operating conditions does it occur most?
   - What are the likely root causes?

3. **Pattern Recognition**:
   - Are failures clustered at specific voltage/current operating points?
   - Is there a trend (e.g., failures increase with voltage)?
   - Are certain Vps/Vin/Iout combinations particularly problematic?

4. **Anomaly Detection**:
   - Any unusual patterns in the data?
   - Differences between pass and fail distributions that stand out?

5. **Recommendations**:
   - Prioritized list of areas to investigate.
   - Suggested design or test improvements.

Keep the report professional, concise, and actionable."""

    print(f"\n  Sending to {MODEL} for analysis (this may take a while on 8GB RAM)...")
    print(f"  Prompt size: ~{len(prompt)} chars")

    response = ollama_client.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]


def main():
    # Determine XLSX file
    if len(sys.argv) > 1:
        xlsx_path = sys.argv[1]
    else:
        # Look for XLSX files in the tools directory
        xlsx_files = list(TOOLS_DIR.glob("reports/*.xlsx"))
        if not xlsx_files:
            print("ERROR: No XLSX file found in tools directory.")
            print(f"Place your test report in: {TOOLS_DIR}")
            print("Or pass the path as argument: python analyze_test_report.py <file.xlsx>")
            sys.exit(1)
        xlsx_path = str(xlsx_files[0])
        if len(xlsx_files) > 1:
            print(f"  Multiple XLSX files found, using: {xlsx_files[0].name}")

    print("=" * 60)
    print("  XLSX Test Report Analyzer")
    print(f"  Model: {MODEL}")
    print("=" * 60)

    # Step 1: Load the file
    print("\n[1/4] Loading XLSX file...")
    if not os.path.isfile(xlsx_path):
        print(f"  ERROR: File not found: {xlsx_path}")
        sys.exit(1)
    sheets = load_xlsx(xlsx_path)

    # Step 2: Extract data
    print("\n[2/4] Extracting test data...")
    sheet_name, df = find_test_sheet(sheets)
    print(f"  Using sheet: '{sheet_name}'")
    summary_text = extract_summary(sheets)

    # Step 3: Build failure analysis
    print("\n[3/4] Analyzing failure patterns...")
    data_summary = build_failure_analysis(df)
    print(data_summary)

    # Step 4: LLM Analysis
    print("\n[4/4] Generating AI feedback report...")
    time_before = datetime.datetime.now()
    report = ask_llm(data_summary, summary_text)
    time_after = datetime.datetime.now()
    print(f"  Analysis completed in {(time_after - time_before).total_seconds():.2f} seconds")

    # Output
    print("\n" + "=" * 60)
    print("  AI FEEDBACK REPORT")
    print("=" * 60)
    print(report)
    print("=" * 60)

    # Save report to file
    report_filename = Path(xlsx_path).stem + "_analysis.txt"
    report_path = TOOLS_DIR / report_filename
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("XLSX TEST REPORT ANALYSIS\n")
        f.write(f"Source: {Path(xlsx_path).name}\n")
        f.write(f"Model: {MODEL}\n")
        f.write("=" * 60 + "\n\n")
        f.write("DATA SUMMARY\n")
        f.write(data_summary + "\n\n")
        f.write("AI FEEDBACK REPORT\n")
        f.write("=" * 60 + "\n")
        f.write(report + "\n")

    print(f"\n  Report saved to: {report_path}")


if __name__ == "__main__":
    main()
