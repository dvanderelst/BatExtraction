import os
from Library import AudioUtils
from concurrent.futures import ProcessPoolExecutor
max_workers = 2
def preprocess_audio_folder(input_folder, output_folder):
    mat_files, _ = AudioUtils.get_mat_files(input_folder)
    os.makedirs(output_folder, exist_ok=True)
    # Use ProcessPoolExecutor to run tasks in parallel
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks for each file
        futures = [
            executor.submit(AudioUtils.preprocess_mat_file, file_name, input_folder, output_folder)
            for file_name in mat_files
        ]
        # Wait for all tasks to complete
        for future in futures:
            future.result()  # This will raise an exception if any task failed