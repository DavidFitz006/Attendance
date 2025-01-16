import streamlit as st
import pandas as pd
import webbrowser

option = st.selectbox(
    "Select unit:",
    ("45 Whiskey", "45 Yankee"),
)
if option == "45 Yankee":
    sheet_url = "https://docs.google.com/spreadsheets/d/1JZsnrbtk2y4hUrdEFkS9-zhlkiFzOKGjcju0QbYd3Hw/export?format=csv&gid=1607918864"
    title = "45 Yankee Attendance"
    form_link = "https://docs.google.com/forms/d/1SMrYHtv1azQVdOilPHg6wFdLnQoG8qdiZDXk88EDGuA/prefill"
else:
    sheet_url = "https://docs.google.com/spreadsheets/d/13XMctk_OQcjI2ojxjjD3g8XdlR9cySYoEXMu4Z2bEgc/export?format=csv&gid=4944438"
    title = "45 Whiskey Attendance"
    form_link = "https://docs.google.com/forms/d/e/1FAIpQLScc4PfkdoHV_dMznIleakOWWfstA7Zyk5gjcG9EUnTaCjS3cg/viewform?usp=header"

# Load the Google Sheet data into a pandas DataFrame
@st.cache_data(ttl=3600)
def load_data(url):
    return pd.read_csv(url)
df = load_data(sheet_url)

# Streamlit App Title
st.title(title)


def load_data(url):
    return pd.read_csv(url)
df = load_data(sheet_url)

# Initialize attendance_summary and operations_count
attendance_summary = None
operations_count = None

# Check if required columns exist in the data
if 'Attendance:' in df.columns and 'Operation or training:' in df.columns:
    # Create a list to store attendance data
    attendance_data = []

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Ensure the Attendance column has a value before processing
        if pd.notna(row['Attendance:']):
            # Split names separated by commas and clean whitespace
            names = [name.strip() for name in row['Attendance:'].split(',')]
            
            # Pair each name with its attendance type
            for name in names:
                attendance_data.append({'Name': name, 'Type': row['Operation or training:']})
    
    # Create a DataFrame to track attendance
    attendance_df = pd.DataFrame(attendance_data)
    
    # Count occurrences for each name in both categories
    total_attendance = attendance_df.groupby('Name').size().reset_index(name='Total Attendance')
    operation_attendance = attendance_df[attendance_df['Type'].str.contains("Operation", case=False, na=False)].groupby('Name').size().reset_index(name='Operation Attendance')
    training_attendance = attendance_df[attendance_df['Type'].str.contains("Training", case=False, na=False)].groupby('Name').size().reset_index(name='Training Attendance')
    
    # Merge attendance counts into a single DataFrame
    attendance_summary = (
        total_attendance
        .merge(operation_attendance, on='Name', how='left')
        .merge(training_attendance, on='Name', how='left')
        .fillna(0)
    )
    
    # Convert attendance counts to integers
    attendance_summary[['Operation Attendance', 'Training Attendance']] = attendance_summary[['Operation Attendance', 'Training Attendance']].astype(int)
    
    # Calculate percentages
    attendance_summary['Operation %'] = ((attendance_summary['Operation Attendance'] / attendance_summary['Total Attendance']) * 100).round(0).astype(int)
    attendance_summary['Training %'] = ((attendance_summary['Training Attendance'] / attendance_summary['Total Attendance']) * 100).round(0).astype(int)

    # Select only the columns for display
    attendance_summary = attendance_summary[['Name', 'Operation %', 'Training %']]

    # Calculate the total number of unique events
    operation_count = attendance_df['Type'].nunique()

    # Calculate the total attendance count per name
    name_counts = df['Attendance:'].str.split(',').explode().str.strip().value_counts()

    # Calculate the percentage attendance for each name
    operations_count = pd.DataFrame(name_counts).reset_index()
    operations_count.columns = ['Name', 'Attendance Count']
    operations_count['Total Attendance Percent'] = ((operations_count['Attendance Count'] / operation_count) * 100).round(0).astype(int)

    # Calculate average attendance for operations and trainings
    # Process the attendance column: split names into lists
    df['Attendance List'] = df['Attendance:'].apply(lambda x: str(x).split(',') if pd.notnull(x) else [])
    
    # Count the number of attendees for each event
    df['Attendance Count'] = df['Attendance List'].apply(len)
    
    # Calculate average attendance for operations and trainings
    avg_operations = df[df['Operation or training:'] == 'Operation']['Attendance Count'].mean()
    avg_trainings = df[df['Operation or training:'] == 'Training']['Attendance Count'].mean()
    # Display average attendance statistics
    st.subheader("Average Attendance Statistics")
    st.write(f"**Average number of people attending operations:** {avg_operations:.2f}")
    st.write(f"**Average number of people attending trainings:** {avg_trainings:.2f}")

    # Display the Total Attendance Percent table
    st.subheader("Total Attendance Percentage")
    st.table(operations_count)

    # Display the attendance percentage table
    st.subheader("Operation to Training Ratio")
    st.table(attendance_summary)

else:
    st.error("The required columns are not found in the data.")

# Button to open Google Form
st.link_button("Attendance Form", form_link)
