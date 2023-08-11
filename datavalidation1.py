import streamlit as st
import pandas as pd
import re
import time

def main():
    st.title("Data Validation Web App")

    uploaded_file = st.file_uploader("Upload a data file", type=["csv", "xlsx", "json"])

    if uploaded_file is not None:
        df = load_data(uploaded_file)
        show_data_preview(df)
        validation_rules = get_validation_rules(df)
        validate_data(df, validation_rules)

        while True:
            failed_rows = fix_failed_rows(df, failed_rows, validation_rules)
            confirm_changes = st.checkbox("Confirm changes and export validation results")

            if st.button("Save and Export") and confirm_changes:
                export_validation_results(df, failed_rows)
            else:
                st.info("Changes not confirmed. Reverting to original data.")

            # Reload original data file if not confirmed
            if not confirm_changes:
                df = load_data(uploaded_file)
                show_data_preview(df)
                validation_rules = get_validation_rules(df)

            validate_data(df, validation_rules)

            failed_rows = []

def load_data(uploaded_file):
    file_type = uploaded_file.name.split(".")[-1]

    if file_type == "csv":
        df = pd.read_csv(uploaded_file)
    elif file_type == "xlsx":
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    elif file_type == "json":
        df = pd.read_json(uploaded_file)
    else:
        st.error("Invalid file format. Please upload a CSV, Excel, or JSON file.")
        st.stop()

    return df

def show_data_preview(df):
    st.subheader("Data Preview")
    st.dataframe(df.head())

def get_validation_rules(df):
    validation_rules = {}

    for col in df.columns:
        rule_type = st.selectbox(f"Select validation rule for column '{col}'", [
            "Required fields", "Data types", "String length",
            "Numeric ranges", "Categorical values", "Date/time constraints",
            "Pattern matching", "Unique values", "Dependencies between columns",
            "Custom validation functions"
        ])
        validation_rules[col] = rule_type

    return validation_rules

def validate_data(df, validation_rules):
    st.subheader("Data Validation")

    progress_bar = st.progress(0)
    total_columns = len(validation_rules)
    failed_rows = []

    for idx, (col, rule_type) in enumerate(validation_rules.items()):
        st.write(f"Validating '{col}' using rule: {rule_type}")

        if rule_type == "Required fields":
            if df[col].isnull().any():
                st.warning(f"Column '{col}' has empty values.")
                failed_rows.append(idx)
            else:
                st.success(f"Column '{col}' passed validation.")
        
        # Add other validation rule checks here
        
        elif rule_type == "Unique values":
            if df.duplicated(subset=[col]).any():
                st.warning(f"Column '{col}' has duplicate values.")
                failed_rows.append(idx)
                
        elif rule_type == "Dependencies between columns":
            if "Start Date" in validation_rules and "End Date" in validation_rules:
                if (pd.to_datetime(df["Start Date"]) >= pd.to_datetime(df["End Date"])).any():
                    st.warning(f"Column 'Start Date' should be before 'End Date'.")
                    failed_rows.append(idx)
                
        elif rule_type == "Pattern matching":
            if col == "Email Address":
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if df[col].apply(lambda x: not re.match(pattern, str(x))).any():
                    st.warning(f"Column '{col}' has values that don't match the email pattern.")
                    failed_rows.append(idx)
        
        elif rule_type == "Custom validation functions":
            if col == "Phone Number":
                if df[col].apply(lambda x: not custom_phone_number_validation(x)).any():
                    st.warning(f"Column '{col}' has values that don't pass custom phone number validation.")
                    failed_rows.append(idx)

        # Simulating some processing time
        time.sleep(0.5)

        # Update progress bar
        progress_bar.progress((idx + 1) / total_columns)

    st.write("Validation complete!")

    if len(failed_rows) > 0:
        st.subheader("Failed Validation Rows")
        st.dataframe(df.iloc[failed_rows])
        st.warning("Some rows have failed validation. Please fix them.")
    
    return failed_rows

def fix_failed_rows(df, failed_rows, validation_rules):
    st.subheader("Fixing Failed Rows")

    new_failed_rows = []

    for idx in failed_rows:
        st.write(f"Fixing data for row {idx}")
        new_values = {}
        for col in df.columns:
            if validation_rules[col] == "Required fields":
                new_values[col] = st.text_input(f"Enter value for '{col}'", value=df.loc[idx, col])
            # Add other fixes here

        # Update the DataFrame with the new values
        df.loc[idx] = new_values

        # Simulating some processing time
        time.sleep(0.3)

        # Validate the fixed row again
        if not validate_row(df.loc[idx], validation_rules):
            new_failed_rows.append(idx)

    st.success("Data fixes applied!")
    return new_failed_rows

def custom_phone_number_validation(value):
    # Implement your custom phone number validation logic here
    return True  # Return True if validation passes, False otherwise

def validate_row(row, validation_rules):
    for col, rule_type in validation_rules.items():
        if rule_type == "Required fields":
            if pd.isnull(row[col]):
                return False
        elif rule_type == "Unique values":
            if row.duplicated(subset=[col]).any():
                return False
        elif rule_type == "Dependencies between columns":
            if "Start Date" in validation_rules and "End Date" in validation_rules:
                if pd.to_datetime(row["Start Date"]) >= pd.to_datetime(row["End Date"]):
                    return False
        elif rule_type == "Pattern matching":
            if col == "Email Address":
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(pattern, row[col]):
                    return False
        elif rule_type == "Custom validation functions":
            if col == "Phone Number":
                if not custom_phone_number_validation(row[col]):
                    return False
        # Add other validation checks here
    return True

def export_validation_results(df, failed_rows):

    if st.checkbox("Export validation results"):
        file_format = st.selectbox("Select file format", ["CSV", "Excel", "JSON"])

        if file_format == "CSV":
            df.to_csv(f"validation_results.csv", index=False)
        elif file_format == "Excel":
            df.to_excel(f"validation_results.xlsx", index=False)
        elif file_format == "JSON":
            df.to_json(f"validation_results.json")

        st.success("Validation results exported successfully!")

if __name__ == "__main__":
    main()
