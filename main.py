from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson.json_util import dumps
from json import loads
from dotenv import load_dotenv
import config
from enum import Enum

jsonize = lambda a: loads(dumps(a))

app = FastAPI(
    title='Mexico Profundo API',
    version='0.0.1',
    summary='API para consultar documentos de MongoDB desde la app México Profundo',
    openapi_tags=[{"name": "Retrieves"}]
)
load_dotenv()
db = MongoClient(f"mongodb+srv://{config.MONGOUSER}:{config.MONGOPASS}@cluster0.sxistir.mongodb.net/?retryWrites=true&w=majority&appName=AtlasApp").MexicoProfundo

@app.exception_handler(PyMongoError)
def pymongo_error_handler(req, e: PyMongoError):
    return JSONResponse(
        status_code=503,
        content={"pymongo_error":jsonable_encoder(e)}
    ) 

@app.exception_handler(Exception)
def pymongo_error_handler(req, e: Exception):
    return JSONResponse(
        status_code=503,
        content={"error":str(e)}
    )

Coleccion = Enum('Coleccion', {v:v for v in db.list_collection_names()})

@app.get("/all/{coleccion}", status_code=200, summary="Retrieve all", tags=["Retrieves"])
def get_all(coleccion: Coleccion
            ):
    """
    Obtener todos los documentos de la colección especificada en el parámetro **coleccion**.
    
    - **coleccion**: Nombre del archivo JSON generado en fase de desarrollo que corresponde a la colección que se desea consultar.
    """
    
    if coleccion not in Coleccion:
        raise HTTPException(404, f"La coleccion {coleccion} no existe")
    cole = jsonize(db[coleccion.value].find())
    return {"count": len(cole),"res":cole}
    # return {'message': f"Hello World: {config.PRUEBA}"}