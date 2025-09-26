import streamlit as st
import requests
import pandas as pd
import io

# Streamlit app configuration
st.set_page_config(page_title="Log Classification Tool", layout="wide")

st.title("Log Classification Tool")
st.write("Upload a CSV file with log messages to get them classified automatically.")

# FastAPI backend URL
API_URL = "http://localhost:8000"

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Display uploaded file info
    st.write("### Uploaded File")
    df_preview = pd.read_csv(uploaded_file)
    st.write(f"**Rows:** {len(df_preview)} | **Columns:** {len(df_preview.columns)}")
    
    # Show preview
    st.write("**Preview:**")
    st.dataframe(df_preview.head())
    
    # Classify button
    if st.button("Classify Logs", type="primary"):
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Send file to FastAPI backend
            with st.spinner("Classifying logs..."):
                files = {"file": ("uploaded.csv", uploaded_file.getvalue(), "text/csv")}
                response = requests.post(f"{API_URL}/classify/", files=files)
            
            if response.status_code == 200:
                st.success("Classification completed!")
                
                # Get the classified results
                result_csv = response.content.decode('utf-8')
                df_result = pd.read_csv(io.StringIO(result_csv))
                
                # Display results
                st.write("### Classification Results")
                st.dataframe(df_result)
                
                # Summary statistics
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Classification Summary:**")
                    classification_counts = df_result['target_label'].value_counts()
                    st.bar_chart(classification_counts)
                
                with col2:
                    st.write("**Statistics:**")
                    st.metric("Total Logs", len(df_result))
                    st.metric("Unique Classifications", len(classification_counts))
                    most_common = classification_counts.index[0]
                    st.metric("Most Common", most_common, classification_counts[most_common])
                
                # Download button
                csv = df_result.to_csv(index=False)
                st.download_button(
                    label="Download Results",
                    data=csv,
                    file_name="classified_logs.csv",
                    mime="text/csv"
                )
                
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the classification service. Make sure the FastAPI server is running on port 8000.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Instructions
with st.expander("Instructions"):
    st.write("""
    ### How to use:
    1. **Start Ollama**: Ensure the Ollama server is running for LLM classification
    1. **Start the FastAPI server**: Run `python app.py` in your terminal
    2. **Prepare your CSV**: Ensure it has 'source' and 'log_message' columns
    3. **Upload**: Select your CSV file using the upload button
    4. **Classify**: Click the "Classify Logs" button
    5. **Download**: Get your results with the download button
    
    ### CSV Format:
    ```
    source,log_message
    ModernCRM,"User login failed"
    BillingSystem,"Payment processed successfully"
    ```
    """)

# Status indicator
try:
    health_response = requests.get(f"{API_URL}/classify/", timeout=2)
    if health_response.status_code in [405, 422]:  # Method not allowed or validation error is expected
        st.sidebar.success("FastAPI Server: Connected")
    else:
        st.sidebar.warning("FastAPI Server: Unexpected response")
except:
    st.sidebar.error("FastAPI Server: Not running")
    st.sidebar.write("Start with: `python app.py`")