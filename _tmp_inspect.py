import pandas as pd

XLSX = "linux_playground/utils/tools/GEN4_S600A_Ver_0.1077.1_2026-01-22_21-29-56.xlsx"
df = pd.read_excel(XLSX, sheet_name="test_v_in_cl_ss_op_2174")

has_time = df["Start Time"].notna()
print(f"Rows with Start Time: {has_time.sum()} / {len(df)}")
if has_time.any():
    print("Sample timestamps:")
    print(df.loc[has_time, ["Start Time", "End Time", "Duration"]].head(5).to_string())

# Check Vps values used
print("\nVps(WP) unique values:", sorted(df["Vps(WP)"].unique()))
print("Vin(WP) unique values:", sorted(df["Vin(WP)"].unique()))
print("Iout(WP) unique values:", sorted(df["Iout(WP)"].unique()))

# Failure patterns
fails = df[df["Result"] == "Fail"]
print("\nFails grouped by Vps(WP):")
print(fails.groupby("Vps(WP)")["FailErrCode"].value_counts().to_string())
print("\nFails grouped by Vin(WP):")
print(fails.groupby("Vin(WP)")["FailErrCode"].value_counts().to_string())

# Check warnings
warnings = df[df["Result"] == "Warning"]
print(f"\nWarning FailErrCodes: {warnings['FailErrCode'].value_counts().to_string() if warnings['FailErrCode'].notna().any() else 'none'}")
print(f"Warning FailReasons: {warnings['FailReason'].value_counts().head(5).to_string() if warnings['FailReason'].notna().any() else 'none'}")
