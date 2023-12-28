import pandas as pd
import random, requests
import uuid
from faker import Faker

fake = Faker()

def reset_dataset():
    df = pd.DataFrame(columns=['id','nombre','apellidos','numero_telefono','codigo_postal','url_registro','otra_info','estado','respuesta'])
    df.to_csv('main_dataset_manager2.csv', index=False, encoding='utf-8-sig')

def reset_dataset2():
    # Crear un DataFrame vacío con las columnas especificadas
    df = pd.DataFrame(columns=['nombre', 'apellidos', 'numero_telefono', 'codigo_postal', 'url_registro', 'otra_info', 'estado', 'respuesta', 'columa_adicional'])

    # Generar 20 filas de datos de muestra
    for _ in range(65):
        df = df._append({
            'nombre':  str(fake.first_name()),  
            'apellidos': str(fake.name_nonbinary()), 
            'numero_telefono': '+34 ' + str(random.randint(100000000, 999999999)), 
            'codigo_postal': random.randint(10000, 99999),  
            'url_registro': 'https://ejemplo.com/registro/{}'.format(random.randint(1, 100)),  
            'otra_info': '*información adicional*', 
            'estado': random.choice(['Actiu', 'Pendent', 'Fallit']),  
            'respuesta': random.choice(['Cuelga/no colabora', 'No contesta', 'Telefono erroneo', 'No contrata por mejor oferta', 'Robinsion', 'Volver a llamar', 'Contrata', 'NO interesa propuesta', 'Telefono erroneo']),  # Respuesta
            'campo_adicional': ''
        }, ignore_index=True)

    # Guardar el DataFrame en un archivo CSV
    df.to_csv('main_dataset_manager2.csv', index=True, encoding='utf-8-sig')

if __name__ == "__main__":
    reset_dataset2()