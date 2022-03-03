import json
from datetime import datetime
from types import SimpleNamespace
import uuid 

# Carrega o objeto json e transforma em objetos dentro da classe UR (basicamente converte o Json em um objeto)
def jsonToObject(jsonString : str):
    return json.loads(jsonString, object_hook=lambda d: SimpleNamespace(**d))

# Converte a data no json em um objeto datetime
def stringToDate(dataString : str) -> datetime:
    data = dataString[:18]  # Corta parte com .z54 (ou algo do tipo)
    return datetime.strptime(data, '%Y-%m-%dT%H:%M:%S')

def gerarID() -> uuid:
    novoId = uuid.uuid4()
    return novoId