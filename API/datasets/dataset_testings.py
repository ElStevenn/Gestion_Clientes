import pandas as pd
import random
import uuid
from faker import Faker

fake = Faker()

def reset_dataset():
    df = pd.DataFrame(columns=['id','nombre','apellidos','numero_telefono','codigo_postal','url_registro','otra_info','estado','respuesta'])
    df.to_csv('main_dataset_manager.csv', index=False, encoding='utf-8-sig')

def reset_dataset2():
    # Crear un DataFrame vacío con las columnas especificadas
    df = pd.DataFrame(columns=['id', 'nombre', 'apellidos', 'numero_telefono', 'codigo_postal', 'url_registro', 'otra_info', 'estado', 'respuesta', 'columa_adicional'])

    # Generar 20 filas de datos de muestra
    for _ in range(65):
        df = df._append({
            'id': str(uuid.uuid4()),  # ID único
            'nombre':  str(fake.first_name()),  # Nombres de muestra
            'apellidos': str(fake.name_nonbinary()),  # Apellidos de muestra
            'numero_telefono': '+34 ' + str(random.randint(100000000, 999999999)),  # Número de teléfono de muestra
            'codigo_postal': random.randint(10000, 99999),  # Código postal de muestra
            'url_registro': 'https://ejemplo.com/registro/{}'.format(random.randint(1, 100)),  # URL de registro de muestra
            'otra_info': '*información adicional*',  # Otra información
            'estado': random.choice(['Actiu', 'Pendent', 'Fallit']),  # Estado
            'respuesta': random.choice(['Cuelga/no colabora', 'No contesta', 'Telefono erroneo', 'No contrata por mejor oferta', 'Robinsion', 'Volver a llamar', 'Contrata', 'NO interesa propuesta', 'Telefono erroneo']),  # Respuesta
            'campo_adicional': ''
        }, ignore_index=True)

    # Guardar el DataFrame en un archivo CSV
    df.to_csv('main_dataset_manager.csv', index=False, encoding='utf-8-sig')

# dt = pd.read_csv('main_dataset_manager.csv')
# print(dt)



# reset_dataset()
reset_dataset2()