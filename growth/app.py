import streamlit as st
import pandas as pd
import os
import datetime
from io import BytesIO

st.set_page_config(page_title="Data Sweeper", layout="wide")

# Title and description
st.title("📀 Datasweeper Sterling Integrator By Rimsha Aslam")
st.write(
    "Transform your files between CSV & Excel formats with built-in data cleaning and visualization, "
    "creating the project for Quarter 03!"
)

# File Uploader
uploaded_files = st.file_uploader(
    "Upload your files (accepts CSV or Excel):",
    type=["csv", "xlsx"],
    accept_multiple_files=True,
)

if uploaded_files:
    files_processed = 0  # Track processed files

    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Process CSV files
        if file_ext == ".csv":
            df = pd.read_csv(file)
        # Process Excel files (specifying engine to ensure compatibility)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file, engine="openpyxl")
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Check for empty DataFrame
        if df.empty:
            st.error(f"{file.name} is empty!")
            continue

        # File Metadata (using current time as placeholder for creation and modified time)
        st.write(f"**File Metadata for {file.name}:**")
        creation_time = datetime.datetime.now()  # Placeholder as we can't get file metadata from Streamlit uploads
        last_modified_time = datetime.datetime.now()  # Placeholder as we can't get file metadata from Streamlit uploads

        st.write(f"File size: {file.size / (1024 * 1024):.2f} MB")
        st.write(f"Creation time: {creation_time}")
        st.write(f"Last modified time: {last_modified_time}")

        # Display file details
        st.write("Preview the head of the DataFrame")
        st.dataframe(df.head())

        # Show basic statistics
        if st.checkbox(f"Show statistics for {file.name}"):
            st.write(df.describe())

        # Data cleaning options
        st.subheader("🛠 Data Cleaning Options")
        if st.checkbox(f"Clean data for {file.name}"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Remove duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("✅ Duplicates removed!")
            with col2:
                if st.button(f"Fill missing values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("✅ Missing values have been filled!")

        # Select columns to keep
        st.subheader("🎯 Select Columns To Keep")
        selected_columns = st.multiselect(
            f"Choose columns for {file.name}", df.columns, default=df.columns
        )
        df = df[selected_columns]

        # Search Data
        st.subheader("🔍 Search Data")
        search_term = st.text_input("Search data", "")
        if search_term:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
            st.write(f"Found {len(df)} rows matching your search term.")
            st.dataframe(df)

        # Data Visualization
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include="number").iloc[:, :2])

        # Line chart for numeric columns
        if st.checkbox(f"Show line chart for {file.name}"):
            st.line_chart(df.select_dtypes(include="number").iloc[:, :2])

        # Pie chart for categorical data
        st.subheader("📊 Pie chart for Categorical Data")
        categorical_cols = df.select_dtypes(include="object").columns
        if len(categorical_cols) > 0:
            selected_categorical = st.selectbox(f"Choose categorical column for pie chart {file.name}", categorical_cols)
            pie_data = df[selected_categorical].value_counts()
            st.write(pie_data.plot.pie(autopct='%1.1f%%', figsize=(5, 5), title=f"{selected_categorical} Distribution"))
        else:
            st.write("No categorical columns available for pie chart.")

        # Conversion Options
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(
            f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name
        )
        if st.button(f"Convert {file.name}"):
            if df.empty:
                st.warning(f"{file.name} is empty, conversion cannot be done.")
            else:
                buffer = BytesIO()
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"
                elif conversion_type == "Excel":
                    df.to_excel(buffer, index=False, engine="openpyxl")
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                buffer.seek(0)
                st.download_button(
                    label=f"Download {file.name} as {conversion_type}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type,
                )

        # Remove unwanted columns
        remove_columns = st.multiselect(f"Select columns to remove from {file.name}", df.columns)
        if remove_columns:
            df = df.drop(columns=remove_columns)
            st.write(f"✅ Removed columns: {remove_columns}")

        # Normalize numeric columns
        if st.checkbox(f"Normalize data for {file.name}"):
            numeric_cols = df.select_dtypes(include=["number"]).columns
            if numeric_cols.size > 0:  # Ensure there are numeric columns
                # Check if any numeric column has more than 1 unique value
                columns_with_variation = [col for col in numeric_cols if df[col].nunique() > 1]
                if columns_with_variation:
                    df[columns_with_variation] = df[columns_with_variation].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
                    st.write("✅ Data normalized!")
                else:
                    st.warning("No variation in numeric columns, normalization skipped.")
            else:
                st.warning("No numeric columns available for normalization.")

        # Filter rows based on a condition
        st.subheader("📑 Advanced Filtering")
        filter_col = st.selectbox(f"Choose a column to filter for {file.name}", df.columns)

        if filter_col:
            # Handle numeric column filtering
            if df[filter_col].dtype in ['float64', 'int64']:
                filter_value = st.number_input(f"Enter a value for {filter_col}:",
                                              min_value=float(df[filter_col].min()),
                                              max_value=float(df[filter_col].max()))
                filtered_df = df[df[filter_col] >= filter_value]
                st.write(f"Filtered data (rows where {filter_col} >= {filter_value}):")
                st.dataframe(filtered_df)
            else:
                st.error(f"The column '{filter_col}' is not numeric. Please select a numeric column for filtering.")
        else:
            st.error("Please select a column to filter.")

        files_processed += 1

    if files_processed == len(uploaded_files):
        st.success("🎉 All Files Processed Successfully!")
