from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from enum import Enum
import pandas as pd
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid


from .calculator import calculate

app = FastAPI()

origins = [
    "http://vm2208021875.vds.ru",
    "http://stelari-start.com",
    "http://localhost:3000",
    "http://localhost:80",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Elastic(BaseModel):
    ps: float
    pd: float
    pwv: float
    pwvType: str


@app.post("/elastic")
def elastic(rqBody: Elastic):
    if rqBody.pwvType == "cf":
        result_column_name = "Stelari"
    else:
        result_column_name = rqBody.pwvType + "Start"

    try:
        return { "result": result_column_name + " " + str(calculate(rqBody.ps, rqBody.pd, rqBody.pwv))}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid parameters")


@app.post("/uploadfile/{pwv_type}")
async def create_upload_file(pwv_type: str, file: UploadFile):
    extension = file.filename.split(".")[-1]

    if extension != "xlsx" and extension != "csv":
        raise HTTPException(status_code=400, detail="Extension not allowed")

    if pwv_type == "cf":
        result_column_name = "Stelari"
    else:
        result_column_name = pwv_type.lower() + "Start"

    contents = await file.read()

    buffer = BytesIO(contents)

    if extension == "csv":
        df = pd.read_csv(buffer)
    else:
        df = pd.read_excel(buffer)

    data = pd.DataFrame(df, columns=['Psys', 'Pdia', 'PWV'])

    result = [calculate(row['Psys'], row['Pdia'], row['PWV']) for _, row in data.iterrows()]
    
    data[result_column_name] = result
    data[result_column_name] = data[result_column_name].astype('float').round(2)

    id = str(uuid.uuid4())

    filename = "tmp/" + id + ".xlsx"

    data.to_excel(filename, index=False)

    return {
        "id": id
    }

@app.get('/{id}', response_class=FileResponse)
def get_file(id: str):
    return FileResponse("tmp/" + id + ".xlsx")
