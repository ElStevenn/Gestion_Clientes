


from pathlib import Path
import pandas as pd
from pandas.errors import EmptyDataError
import numpy as np
import asyncio
import json, string
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
            path = Path("datasets/main_dataset_manager2.csv").resolve()
            self.columns_names = ['Nombre', 'Apellidos', 'Numero Telefono', 'Codigo Postal', 'Url Registro', 'Otra Información', 'Estado', 'Respuesta', 'Columna Reservada']

            try:
                self.manage_dataset = pd.read_csv(path)
                # Check if the DataFrame is empty
                if self.manage_dataset.empty:
                    raise EmptyDataError
            except (FileNotFoundError, EmptyDataError):
                # If the file does not exist or is empty, create an empty DataFrame with the specified columns
                self.manage_dataset = pd.DataFrame(columns=self.columns_names)
                self.manage_dataset.to_csv(path, index=False)

            self.manage_dataset_numy = self.manage_dataset.to_numpy()

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

    def remove_duplicated_values(self, a2_array: np.ndarray, columns_to_check):
        """
        Return `a2_array` without the rows that have matching column values in `self.manage_dataset_numy`.
        
        Parameters:
        a2_array (np.ndarray): The array from which duplicates will be removed.
        columns_to_check (list): Column indices to check for duplicates.
        
        Returns:
        np.ndarray: The filtered array with duplicates removed.
        """
        if not isinstance(a2_array, np.ndarray):
            raise ValueError("a2_array must be a numpy ndarray.")
        
        # Validate columns_to_check
        if not all(isinstance(col, int) for col in columns_to_check):
            raise ValueError("columns_to_check must be a list of integers.")
        
        # Create a set of tuples for the selected columns in `self.manage_dataset_numy`
        set1 = {tuple(row[columns_to_check]) for row in self.manage_dataset_numy}
        
        # Use numpy boolean indexing for finding non-matching indices
        mask = np.array([tuple(row[columns_to_check]) not in set1 for row in a2_array])
        filtered_array2 = a2_array[mask]
        
        return filtered_array2
    
    async def update_dataset_status(self, new_values: np.ndarray):
        """
        Updates the dataset by removing duplicated values based on specified columns
        and saves the updated dataset to a CSV file.
        
        Parameters:
        new_values (np.ndarray): New data to update the dataset with.
        """
        try:
            cleaned_array = self.remove_duplicated_values(new_values, columns_to_check=[3])
            self.manage_dataset_numy = cleaned_array

            self.manage_dataset = pd.DataFrame(self.manage_dataset_numy, columns=self.columns_names)
            await self.async_to_csv(self.manage_dataset, "datasets/main_dataset_manager2.csv")
        except Exception as e:
            print(f"An error occurred: {e}")

    def to_csv_wrapper(self, df, filename, index, encoding):
        try:
            # Ensure the path is a string, as pd.to_csv expects a string path or buffer
            df.to_csv(str(filename), index=index, encoding=encoding)
            print("CSV writing successful to:", filename)
        except Exception as e:
            print(f"Error in CSV writing: {e}")

    async def async_to_csv(self, df: pd.DataFrame, filename: str):
        loop = asyncio.get_event_loop()
        # The filename is converted to a Path object, ensure to convert it back to string if needed
        await loop.run_in_executor(None, self.to_csv_wrapper, df, Path(filename), False, 'utf-8')





if __name__ == "__main__":

    # Ejemplo de uso de DTManage_manager()

    DFTester = DTManage_manager()
   
