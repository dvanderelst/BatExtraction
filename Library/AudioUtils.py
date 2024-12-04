import dill
import os
import zipfile
from io import BytesIO

# selected_fields = ['file_idx', 'channel_idx', 'segments', 'indices']
#
# class ZipPickleList:
#     def __init__(self, outputfolder, channel_idx):
#         # Set the path for the zip file
#         self.file_name = os.path.join(outputfolder, f'channel_{channel_idx}.zip')
#
#         # Delete the existing zip file if it already exists
#         if os.path.exists(self.file_name):
#             os.remove(self.file_name)
#
#     def add(self, index, data):
#         selected_data = {key: data[key] for key in selected_fields}
#         # Create a pickle file for the current data entry
#         pickle_data = BytesIO()
#         dill.dump(selected_data, pickle_data)
#         pickle_data.seek(0)
#         # Add the pickle file to the zip archive with a filename based on the index
#         with zipfile.ZipFile(self.file_name, mode='a', compression=zipfile.ZIP_STORED) as zf:
#             zf.writestr(f'{index}.pkl', pickle_data.read())
#
#     def get_data(self, index=None):
#         # Read and load data from the zip file
#         with zipfile.ZipFile(self.file_name, mode='r') as zf:
#             if index is not None:
#                 # Fetch a specific entry by index
#                 try:
#                     with zf.open(f'{index}.pkl') as file:
#                         return dill.load(file)
#                 except KeyError:
#                     return None  # Return None if the specified index does not exist
#             else:
#                 # Fetch all entries
#                 all_data = {}
#                 for file_name in zf.namelist():
#                     idx = file_name.split('.pkl')[0]
#                     with zf.open(file_name) as file:
#                         all_data[idx] = dill.load(file)
#                 return all_data
