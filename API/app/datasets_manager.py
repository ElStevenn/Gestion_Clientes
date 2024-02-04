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
        datasets_dir = Path("./datasets")
        datasets_dir.mkdir(parents=True, exist_ok=True)

        # This is the main dataset where the users work
        self.dataset_path = datasets_dir / "main_dataset_manager2.csv"

        self.google_sheed_crud = Document_CRUD(conf['GOOGLE-SHEET']['spreadsheet_id'])

        try:
            self.columns_names = self.get_column_names(True)
        except Exception as e:
            # Handle exceptions related to Google Sheets API call
            print(f"Error retrieving column names: {e}")
            self.columns_names = ['index']  # Default column names

        try:
            self.manage_dataset = pd.read_csv(self.dataset_path)
            if self.manage_dataset.empty:
                raise pd.errors.EmptyDataError
        except (FileNotFoundError, pd.errors.EmptyDataError):
            self.manage_dataset = pd.DataFrame(columns=self.columns_names)
            self.manage_dataset.to_csv(self.google_sheed_crud, index=False)

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

    async def add_new_columns(self, **columns):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._add_columns_sync, columns)

    def _add_columns_sync(self, columns):
        # Ensure manage_dataset is initialized
        if self.manage_dataset.empty:
            # Initialize manage_dataset with the index set to the range of the first column's length
            first_column_name, first_column_values = next(iter(columns.items()))
            self.manage_dataset = pd.DataFrame(index=range(len(first_column_values)))

        for column_name, column_values in columns.items():
            if len(column_values) != len(self.manage_dataset):
                raise ValueError(f"Length of '{column_name}' does not match the DataFrame length.")

            # Add or update the column in the DataFrame
            self.manage_dataset[column_name] = column_values

        # Save the updated DataFrame to CSV
        path = Path("datasets/main_dataset_manager.csv").resolve()
        self.manage_dataset.to_csv(path, index=False)

    async def add_new_row(self, row_data: np.ndarray):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._add_new_row_sync, row_data)

    def _add_new_row_sync(self, row_data: np.ndarray):
        # Ensure row_data is a list with thir prespective lenght
        if not isinstance(row_data, np.ndarray):
            raise ValueError("The given data is not event an array list")
        
        # Handle lenght error
        query  = np.array(self.columns_names) != None
        result = np.array(self.columns_names)[query]
        if len(result) != len(row_data):
            raise ValueError(f"Worng array lenght, the right lenght should be {len(result)}")

        """        
        if missing_columns:
            # Optionally handle missing columns: raise an error, add them, ignore, etc.
            raise ValueError(f"Missing columns in the dataset: {missing_columns}")

        # Append the new row to the DataFrame
        new_row = pd.DataFrame([row_data])  # Convert dict to DataFrame for appending
        self.manage_dataset = pd.concat([self.manage_dataset, new_row], ignore_index=True)

        # Save the updated DataFrame back to CSV
        self.manage_dataset.to_csv(self.dataset_path, index=False)
        """

    async def delete_row(self, row_index):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._delete_row_sync, row_index)

    def _delete_row_sync(self, row_index):
        self.manage_dataset.drop(row_index, inplace=True)
        path = Path("datasets/main_dataset_manager.csv").resolve()
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
        """esta función es simplemente para definirel campo de información adicional y ponerlo de forma legible \ ya no está en uso por el autho schema"""
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
                    duplicate_messages.append(f"{rows_str} tiene el mismo valor \"{value}\" en la columna \"{self.get_column_names()[index-1]}\"") if value != '' else None

        if duplicate_messages:
            self.google_sheed_crud.send_message(", ".join(duplicate_messages), 'warning')
        else:
            self.google_sheed_crud.clear_cell_formatting()


    async def update_dataset_status(self, new_values: np.ndarray):
        column_indic, column_name_inic = self.get_unique_values()
        self.find_duplicate_rows_by_columns(new_values, column_indices = column_indic, column_names=column_name_inic)
        try:
            self.manage_dataset = pd.DataFrame(new_values, columns=self.get_column_names(True))

            if not self.manage_dataset.empty:
                await self.async_to_csv(self.manage_dataset, "datasets/main_dataset_manager2.csv")
            else:
                print("Error: DataFrame is empty, not writing to CSV.")
        except ValueError:
            self.google_sheed_crud.send_message("You've changed the column shape, this can take a while!", "message")
            

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


async def main():
    DT_manager = DTManage_manager()
    np_values = np.array([
        ['sd', 'dss', 'dss', 'sd', 'sd', 'sd', 'sd', 'sd', 'sd']
    ])
    # Try to add a new row into the dataset
    await DT_manager.add_new_row(np_values)



if __name__ == "__main__":
    asyncio.run(main())


