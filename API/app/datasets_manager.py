#!/usr/bin/env python3

from pathlib import Path
import pandas as pd
from pandas.errors import EmptyDataError
import numpy as np
import asyncio, os
import json, string
from configparser import ConfigParser
from .google_sheet_imp import Document_CRUD 

"""
    Añadir documentación aquí sobre la gestión de los datasets

"""

config_path = Path(__file__).parent.parent / 'conf.ini'
conf = ConfigParser()
conf.read(config_path)

class DTManage_manager():
    """
    Clase para manejar el dataset el cuál es usado para detectar valores duplicados, valores erroneos y entre muchas cosas más
    Permite añadir nuevas columnas, filas y eliminar filas específicas.
    """

    def __init__(self):
        # Directory for datasets
        datasets_dir = Path("datasets")
        datasets_dir.mkdir(parents=True, exist_ok=True)

        # Full path to the CSV file
        path = datasets_dir / "main_dataset_manager2.csv"

        self.google_sheed_crud = Document_CRUD(conf['GOOGLE-SHEET']['spreadsheet_id'])

        try:
            self.columns_names = self.get_column_names(True)
        except Exception as e:
            # Handle exceptions related to Google Sheets API call
            print(f"Error retrieving column names: {e}")
            self.columns_names = ['index']  # Default column names

        try:
            self.manage_dataset = pd.read_csv(path)
            if self.manage_dataset.empty:
                raise pd.errors.EmptyDataError
        except (FileNotFoundError, pd.errors.EmptyDataError):
            self.manage_dataset = pd.DataFrame(columns=self.columns_names)
            self.manage_dataset.to_csv(path, index=False)

        self.manage_dataset_numy = self.manage_dataset.to_numpy()

    def get_column_names(self, index=False):
        """get all column names from the Google spreadseet document"""

        if not index:
            return [val.get('value', None) for val in self.get_columns_ns]
        else:
             
            res = [val.get('value', None) for val in self.get_columns_ns]
            res.insert(0, 'index')
            return res

    def get_unique_values(self):
        """
        1: Get all the unique values (it means it's italic) and returns in an array with the position. e.g. [1,4,7]
        2: Get the columns name with unique values. e.g. [{'position': 1, 'name': 'Surname'}, {'position': 4, 'name': 'City'}, {'position': 7, 'name': 'Description'}]
        """
        all_unique_values = []
        name_unq_with_values = []
        with open('app/config/config_column_status.json', 'r') as f:
            column_names = json.loads(str(f.read()))
        
        for i, pos in enumerate(column_names):
            if pos.get('is_italic', None):
                all_unique_values.append(i+1)
                name_unq_with_values.append({'position': i+1, 'name': column_names[i]})

        return all_unique_values, name_unq_with_values

    @property
    def get_columns_ns(self):
        """Get column name and if is unique or not"""
        with  open('app/config/config_column_status.json', 'r') as f:
            return json.loads(f.read())       

    @property
    def get_excel_range(self):
        """Get excel range_name by its column range, saved in a JSON file"""
        with open('app/config/general_config.json', 'r') as f:
            result = json.loads(f.read())
        return str(result['range_name'])

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


    @staticmethod
    def dic_writter(dic: dict):
        """esta función es simplemente para definirel campo de información adicional y ponerlo de forma legible"""
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

    def find_duplicate_rows_by_columns(self, data, column_indices, column_names):
        """
        Identify rows in a numpy array that have duplicate values in the specified columns.

        :param data: Numpy array of data
        :param column_indices: List of indices of the columns to check for duplicate values
        :return: String messages indicating which rows have the same values in the specified columns
        """
        duplicate_messages = []

        # Convert column_indices to integers if they are strings
        column_indices = [int(index) for index in column_indices]

        for index in column_indices:
            # Create a dictionary to track values and their corresponding rows
            value_to_rows = {}
            for row_idx, value in enumerate(data[:, index]):
                if value in value_to_rows:
                    value_to_rows[value].append(row_idx)
                else:
                    value_to_rows[value] = [row_idx]

            # Identify duplicates and prepare messages
            for value, rows in value_to_rows.items():
                if len(rows) > 1:
                    rows_str = ' y '.join(['la fila ' + str(row + 9) for row in rows])
                    duplicate_messages.append(f"{rows_str} tiene el mismo valor \"{value}\" en la columna \"{self.get_column_names()[index-1]}\"")

        if duplicate_messages:
            self.google_sheed_crud.send_message(", ".join(duplicate_messages), 'warning', ['Error ocurrido'])
        else:
            self.google_sheed_crud.clear_cell_formatting()


    async def update_dataset_status(self, new_values: np.ndarray):
        column_indic, column_name_inic = self.get_unique_values()
        self.find_duplicate_rows_by_columns(new_values, column_indices = column_indic, column_names=column_name_inic)
        self.manage_dataset = pd.DataFrame(new_values, columns=self.get_column_names(True))

        if not self.manage_dataset.empty:
            await self.async_to_csv(self.manage_dataset, "app/datasets/main_dataset_manager2.csv")
        else:
            print("Error: DataFrame is empty, not writing to CSV.")


    def to_csv_wrapper(self, df, filename, index, encoding):
        try:
            if not df.empty:
                df.to_csv(filename, mode='w', index=index, encoding=encoding)
                print("CSV writing successful to:", filename)
            else:
                print("Error: DataFrame is empty, not writing to CSV.")
        except Exception as e:
            print(f"Error in CSV writing: {e}")

    async def async_to_csv(self, df: pd.DataFrame, filename: str):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.to_csv_wrapper, df, filename, False, 'utf-8-sig')

if __name__ == "__main__":
    pass

