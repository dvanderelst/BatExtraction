import time
import shutil
from Library import Utils
import os.path as path
import os
from multiprocessing import Manager, Lock

from multiprocessing import Manager, Lock

class AdminHelper:
    def __init__(self, video_folder, output_folder, shared_data, log_lock):
        self.video_files = Utils.get_video_files(video_folder)
        self.processing_progress = video_files_to_dict(self.video_files)
        self.folders = create_output_folder_structure(output_folder, clear_existing=False)
        self.log_file = path.join(output_folder, 'log.html')
        self.shared_data = shared_data  # Shared dictionary for logging across processes
        self.log_lock = log_lock  # Lock to synchronize access to shared log list

    def log(self, level, message, write2file=False):
        level_type = 'NONE'
        if level == 0: level_type = 'INFO'
        if level == 1: level_type = 'WARNING'
        if level >= 2: level_type = 'ERROR'
        asc_time = time.asctime()

        log_item = [asc_time, level_type, message]

        # Use a lock to prevent race conditions when appending to the shared log list
        with self.log_lock:
            self.shared_data['log_list'].append(log_item)

        if write2file:
            self.write2logfile(log_item)

    def write_log(self):
        # Write logs from shared data to the HTML log file
        write_logs_to_html(self.shared_data['log_list'], self.log_file)

    def write2logfile(self, log_item):
        # You can expand this function to directly append new logs to the HTML file if needed.
        pass

    def get_output_folder(self):
        return self.folders['output_folder']

    def get_folder(self, channel, tp):
        if tp == 'led':
            return self.folders['led_folders'][channel-1]
        elif tp == 'int':
            return self.folders['int_folders'][channel-1]


def video_files_to_dict(video_files):
    result = {}
    channel = 1
    for channel_files in video_files:
        current_dict = {}
        for file in channel_files:
            base_name = path.basename(file)
            current_dict[base_name] = [False, False]
            result[channel] = current_dict
        channel += 1
    return result


def create_output_folder_structure(main_folder, clear_existing=False):
    led_channel_1_folder = path.join(main_folder, 'led_channel_1')
    led_channel_2_folder = path.join(main_folder, 'led_channel_2')
    led_channel_3_folder = path.join(main_folder, 'led_channel_3')
    led_channel_4_folder = path.join(main_folder, 'led_channel_4')

    int_channel_1_folder = path.join(main_folder, 'intensities_channel_1')
    int_channel_2_folder = path.join(main_folder, 'intensities_channel_2')
    int_channel_3_folder = path.join(main_folder, 'intensities_channel_3')
    int_channel_4_folder = path.join(main_folder, 'intensities_channel_4')

    led_folders = [led_channel_1_folder, led_channel_2_folder, led_channel_3_folder, led_channel_4_folder]
    int_folders = [int_channel_1_folder, int_channel_2_folder, int_channel_3_folder, int_channel_4_folder]

    try:
        if path.exists(main_folder) and clear_existing: shutil.rmtree(main_folder)

        os.makedirs(main_folder, exist_ok=True)

        os.makedirs(led_channel_1_folder, exist_ok=True)
        os.makedirs(led_channel_2_folder, exist_ok=True)
        os.makedirs(led_channel_3_folder, exist_ok=True)
        os.makedirs(led_channel_4_folder, exist_ok=True)

        os.makedirs(int_channel_1_folder, exist_ok=True)
        os.makedirs(int_channel_2_folder, exist_ok=True)
        os.makedirs(int_channel_3_folder, exist_ok=True)
        os.makedirs(int_channel_4_folder, exist_ok=True)

    except Exception as e:
        print(f"Error creating folder structure: {e}")

    result = {}
    result['output_folder'] = main_folder
    result['led_folders'] = led_folders
    result['int_folders'] = int_folders
    return result


def write_logs_to_html(logs, filename="log_output.html"):
    html_content = """
    <html>
    <head>
        <title>Log Output</title>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <h2>Log Output</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Level</th>
                <th>Message</th>
            </tr>
    """

    for log_item in logs:
        asc_time, level_type, message = log_item
        html_content += f"""
            <tr>
                <td>{asc_time}</td>
                <td>{level_type}</td>
                <td>{message}</td>
            </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    with open(filename, 'w') as f:f.write(html_content)
    print(f"Logs have been written to {filename}")

