import os
import json

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime

import src.preprocessing as preprocessing
import src.scorer as scorer

ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = FastAPI()

class FileListResponse(BaseModel):
    files: list

@app.post('/upload')
async def upload(file: UploadFile = File(...)):
    # File import
    if file and allowed_file(file.filename):
        filename = file.filename

        # Local file saving
        new_filename = f'{filename.split(".")[0]}_{str(datetime.now())}.csv'
        save_location = os.path.join('input', new_filename)
        
        with open(save_location, 'wb') as f:
            f.write(await file.read())

        # Getting input data
        input_df = preprocessing.import_data(save_location)

        # Starting preprocessing
        preprocessed_df = preprocessing.run_preprocessing(input_df)

        # Running scorer to receive the submission file
        submission = scorer.make_pred(preprocessed_df, save_location)
        submission.to_csv(save_location.replace('input', 'output'), index=False)

        # Saving the top 5 important model features
        json_filename = new_filename.replace('.csv', '_feature_importances.json').replace('input', 'output')
        json_location = os.path.join('output', json_filename)

        feature_importances_dict = scorer.get_feature_importances()
        with open(json_location, 'w', encoding='utf-8') as json_file:
            json.dump(feature_importances_dict, json_file, ensure_ascii=False)

        # Saving the density plot of predicted scores
        preds = submission['preds'].values
        plot_filename = new_filename.replace('.csv', '_density_plot.png').replace('input', 'output')
        plot_location = os.path.join('output', plot_filename)
        scorer.save_density_plot(preds, plot_location)

        return {"message": "File processed successfully"}

    raise HTTPException(status_code=400, detail="Invalid file type")

@app.get('/download', response_model=FileListResponse)
def download():
    files = [f for f in os.listdir('output') if not f.startswith('.DS_Store')]
    return {'files': files}

@app.get('/download/{filename}')
def download_file(filename):
    file_path = os.path.join('output', filename)
    
    if filename.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as json_file:
            content = json.load(json_file)
        return JSONResponse(content=content,
                            headers={'Content-Disposition': f'attachment; filename="{filename}"'},
                            media_type='application/json; charset=utf-8')
    else:
        return FileResponse(file_path,
                            headers={'Content-Disposition': f'attachment; filename="{filename}"'})