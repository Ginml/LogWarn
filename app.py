import pandas as pd
from classifier import classify

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"], # Streamlit default port
    allow_methods=["GET", "POST"], # methods needed by streamlit
    allow_headers=["*"],
)

@app.post("/classify/")
async def classify_logs(file: UploadFile):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")
    
    try:
        df = pd.read_csv(file.file)
        if 'source' not in df.columns or 'log_message' not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain 'source' and 'log_message' columns.")
        
        # classify log messages
        df['target_label'] = classify(zip(df['source'], df['log_message']))


        # save to output file
        output_path = 'resources/output.csv'
        df.to_csv(output_path, index=False)

        return FileResponse(output_path, media_type='text/csv', filename='output.csv')

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during processing: {e}")
    
    finally:
        file.file.close()