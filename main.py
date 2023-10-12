from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
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


origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/all/{coleccion}", status_code=200, summary="Retrieve all from a collection", tags=["Retrieves"])
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

@app.get("/atrb/{coleccion}")
def get_one(coleccion: Coleccion, req: Request):
    """
    Obtener un documento de la colección especificada en el parámetro **coleccion** que cumpla con los query params.
    
    - **coleccion**: Nombre del archivo JSON generado en fase de desarrollo que corresponde a la colección que se desea consultar.
    - Parámetros opcionales: Puede especificar cualquier query param como criterio de búsqueda.
    """
    
    if coleccion not in Coleccion: 
        raise HTTPException(404, f"La coleccion {coleccion} no existe")
    params = dict(req.query_params)
    for param in req.query_params:
        try:
            params[param] = float(req.query_params[param])
        except ValueError:
            pass
    cole = jsonize(db[coleccion.value].find_one(params))
    if not cole:
        raise HTTPException(404, "Ningún documento coincide con la búsqueda")
    return {"res":cole}