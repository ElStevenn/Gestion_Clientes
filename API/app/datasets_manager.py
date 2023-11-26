


from pathlib import Path
import pandas as pd
import numpy as np
import asyncio
import json
from configparser import ConfigParser

"""
 Añadir documentación aquí sobre la gestión de los datasets

"""

class DTManage_manager:
    """
    Clase para manejar un dataset de tokens para el manager.
    Permite añadir nuevas columnas, filas y eliminar filas específicas.
    """

    def __init__(self):
        path = Path("./datasets/main_dataset_manager.csv").resolve()
        self.manage_dataset = pd.read_csv(path)

    @property
    def show_dataset(self):
        return self.manage_dataset

    async def add_new_columns(self, columns: dict):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._add_columns_sync, columns)

    def _add_columns_sync(self, columns: dict):
        for column_name, column_values in columns.items():
            if len(column_values) != len(self.manage_dataset):
                raise ValueError(f"Longitud de '{column_name}' no coincide con la del DataFrame.")

            self.manage_dataset[column_name] = column_values

        path = Path("./datasets/main_dataset_manager.csv").resolve()
        self.manage_dataset.to_csv(path, index=False)

    async def add_new_row(self, row_data: list):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._add_new_row_sync, row_data)

    def _add_new_row_sync(self, row_data: list):
        new_row = pd.Series(row_data, index=self.manage_dataset.columns)
        self.manage_dataset = self.manage_dataset._append(new_row, ignore_index=True)

        path = Path("./datasets/main_dataset_manager.csv").resolve()
        self.manage_dataset.to_csv(path, index=False)

    async def delete_row(self, row_index):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._delete_row_sync, row_index)

    def _delete_row_sync(self, row_index):
        self.manage_dataset.drop(row_index, inplace=True)
        path = Path("./datasets/main_dataset_manager.csv").resolve()
        self.manage_dataset.to_csv(path, index=False)

    def query_row(self, token):
        result_df = self.manage_dataset.loc[self.manage_dataset['id'] == token]
        if not result_df.empty:
            result = result_df.iloc[0].tolist()
            return result
        else:
            return None

    @property
    def dataset_toJson(self):
        """Convierte el dataset a JSON para su uso en frontend."""
        return self.manage_dataset.to_json(orient='records')

    
    def get_xlsx_document(self, filename = "file.xlsx"):
        """devuvleve el docuento pero con la exensión xlsx"""
        
        return self.manage_dataset.to_excel(filename)

    def checkin_dupped_columns(self, phone_number = None, url_reg = None):
        read_numbers = self.manage_dataset[self.manage_dataset['numero_telefono'] ==  phone_number]
        read_url = self.manage_dataset[self.manage_dataset['url_registro'] ==  url_reg]

        if len(read_numbers):
            return True
        elif len(read_url):
            return True
        return False

    @staticmethod
    def dic_writter(dic: dict):
        """esta función es simplemente para definirel campo de información adicionar y ponerlo de forma legible"""
        if not dic:
            return ""
        try:
            result = ""
            for key, value in dic.items():
                key_str = str(key).replace("_", " ").replace("-", " ")
                value_str = str(value).replace("_", " ").replace("-", " ") if value is not None else ""
                result += f"{key_str}: {value_str} | "

            return result
        except Exception as e:
            return ""

class ButtonManager:
    
    def __init__(self):
        pass

    @staticmethod
    def get_actual_position(acual_position = 1):
        """Obtengo la posición acutal de los botones para luego definirlo en el frontend"""
        if acual_position <= 1:
            return [1,2,3,4]
        else:
            return [acual_position -2, acual_position -1, acual_position, acual_position +1]


if __name__ == "__main__":

    # Ejemplo de uso de DTManage_manager()
    """
    async def main():
        manager = DTManage_manager()


        nuevos_datos = ['nuevo_token', 'nuevo_nombre', 'nuevo_apellido', 'nuevo_telefono', 'nuevo_codigo_postal', 'nueva_url',r'{}']
        await manager.add_new_row(nuevos_datos) # Añadir la nueva columna

        
        print(manager.show_dataset)


    asyncio.run(main())"""
    """
        # Ejemplo de uso de convertir a array cada columna
        Table_manager = DTManage_manager()

        # print(Table_manager.show_dataset)
        splited_json = Table_manager.split_jsoneable_dataset()
        print(splited_json[-1])
    """

    DFTester = DTManage_manager()
    result = DFTester.checkin_dupped_columns(phone_number = "+34 34934957a2")
    print(result)
