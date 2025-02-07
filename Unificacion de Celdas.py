import pandas as pd
import numpy as np

data = {'Entity': ['Donald Trump', 'Trump', 'White', 'White House', "Karoline Leavitt", "American","FOX Bussiness","Department", "Stuart Varney"], 
        'Type': ['GPE', 'FACILITY', 'ORGANIZATION', 'PERSON'], 
        'Ocurrences': [1, 2, 3, 4]}
df = pd.DataFrame(data)
def unificar_celdas(df, columna):
  
    # Crear una nueva columna con las celdas unificadas
    df['Unified_' + columna] = df[columna].str.replace(r'\s+', ' ', regex=True) # Eliminar espacios adicionales
    df['Unified_' + columna] = df['Unified_' + columna].str.lower() # Convertir a minúsculas
    df['Unified_' + columna] = df['Unified_' + columna].str.strip() # Eliminar espacios al principio y al final
    
    # Agrupar por la nueva columna y sumar las ocurrencias
    df = df.groupby('Unified_' + columna).agg({'Entity': 'first', 'Type': 'first', 'Ocurrences': 'sum'})
    
    # Resetear el índice
    df = df.reset_index()
    
    return df
df = unificar_celdas(df, 'Entity')
print(df)