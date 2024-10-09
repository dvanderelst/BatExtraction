import time
import uuid
from Library import Utils
from Library import Settings
import os.path as path
import os
import ast


class FolderManager:
    def __init__(self, video_folder, empty_log_folder=True):
        self.video_folder = video_folder
        self.base_output_folder = path.split(video_folder)[1]
        self.output_drive = Settings.output_drive
        self.video_files = Utils.get_video_files(self)
        self.folders = create_output_folder_structure(self.base_output_folder, True)
        self.log_file = path.join(self.output_drive, self.base_output_folder, 'log.html')
        if empty_log_folder: Utils.empty_folder(self.folders['log_folder'])

    def get_video_folder(self):
        return self.video_folder

    def get_log_file(self):
        log_folder = self.get_log_folder()
        unique_name = str(uuid.uuid4())
        unique_file_name = os.path.join(log_folder, unique_name + '.txt')
        return unique_file_name

    def log(self, level, message):
        level_type = 'NONE'
        if level == 0: level_type = 'INFO'
        if level == 1: level_type = 'WARNING'
        if level >= 2: level_type = 'ERROR'
        asc_time = time.asctime()
        time_stamp = time.time()
        log_item = [time_stamp, asc_time, level_type, message]
        fl = open(self.get_log_file(), 'w')
        fl.write(str(log_item))
        fl.close()

    def read_and_sort_logs(self):
        log_folder = self.get_log_folder()
        log_entries = []
        # Loop through all txt files in the folder
        for file_name in os.listdir(log_folder):
            if file_name.endswith('.txt'):
                file_path = os.path.join(log_folder, file_name)
                # Read each file and extract the log entry
                with open(file_path, 'r') as file:
                    log_entry = ast.literal_eval(file.read().strip())  # Convert the string to a list
                    log_entries.append(log_entry)
        # Sort the log entries by the timestamp (the first element of each list)
        sorted_log_entries = sorted(log_entries, key=lambda x: x[0])
        return sorted_log_entries

    def write_log(self):
        log_entries = self.read_and_sort_logs()
        write_logs_to_html(log_entries, self.log_file)

    def get_log_folder(self):
        return self.folders['log_folder']

    def get_output_folder(self):
        return self.folders['output_folder']

    def get_base_output_folder(self):
        return self.folders['base_output_folder']

    def get_result_folders(self, channel, tp):
        if tp == 'led':
            return self.folders['led_folders'][channel-1]
        elif tp == 'int':
            return self.folders['int_folders'][channel-1]

    def print_contents(self):
        print('Base output folder:', self.get_base_output_folder())
        print('Output folder:', self.get_output_folder())
        print('LED folders:')
        for folder in self.folders['led_folders']: print(folder)
        print('Intensity folders:')
        for folder in self.folders['int_folders']: print(folder)
        print('Log folder:', self.get_log_folder())


def create_output_folder_structure(base_output_folder, make=False):

    output_drive = Settings.output_drive
    output_folder = path.join(output_drive, base_output_folder)

    led_channel_1_folder = path.join(output_folder, 'led_channel_1')
    led_channel_2_folder = path.join(output_folder, 'led_channel_2')
    led_channel_3_folder = path.join(output_folder, 'led_channel_3')
    led_channel_4_folder = path.join(output_folder, 'led_channel_4')

    int_channel_1_folder = path.join(output_folder, 'intensities_channel_1')
    int_channel_2_folder = path.join(output_folder, 'intensities_channel_2')
    int_channel_3_folder = path.join(output_folder, 'intensities_channel_3')
    int_channel_4_folder = path.join(output_folder, 'intensities_channel_4')

    log_folder = path.join(output_folder, 'logs')

    led_folders = [led_channel_1_folder, led_channel_2_folder, led_channel_3_folder, led_channel_4_folder]
    int_folders = [int_channel_1_folder, int_channel_2_folder, int_channel_3_folder, int_channel_4_folder]

    if make:
        os.makedirs(output_folder, exist_ok=True)

        os.makedirs(led_channel_1_folder, exist_ok=True)
        os.makedirs(led_channel_2_folder, exist_ok=True)
        os.makedirs(led_channel_3_folder, exist_ok=True)
        os.makedirs(led_channel_4_folder, exist_ok=True)

        os.makedirs(int_channel_1_folder, exist_ok=True)
        os.makedirs(int_channel_2_folder, exist_ok=True)
        os.makedirs(int_channel_3_folder, exist_ok=True)
        os.makedirs(int_channel_4_folder, exist_ok=True)

        os.makedirs(log_folder, exist_ok=True)

    result = {}
    result['base_output_folder'] = base_output_folder
    result['output_folder'] = output_folder
    result['led_folders'] = led_folders
    result['int_folders'] = int_folders
    result['log_folder'] = log_folder
    return result



def write_logs_to_html(log_entries, output_filename):
    # Start HTML structure
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
        <h2>Sorted Log Entries</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Date</th>
                <th>Level</th>
                <th>Message</th>
            </tr>
    """

    # Loop through the log entries and add each one as a table row
    for log_entry in log_entries:
        timestamp, date, level, message = log_entry
        html_content += f"""
            <tr>
                <td>{timestamp}</td>
                <td>{date}</td>
                <td>{level}</td>
                <td>{message}</td>
            </tr>
        """

    # Close the table and HTML
    html_content += """
        </table>
    </body>
    </html>
    """

    # Write the HTML content to the output file
    with open(output_filename, 'w') as file:
        file.write(html_content)

    print(f"Logs have been written to {output_filename}")


 #
 # self.progress_files = create_progress_files(self.video_files, self.folders['log_folder'])
 #
 #    def update_progress_file(self, video_file_name, content):
 #        base_name = os.path.basename(video_file_name)
 #        progress_files = self.get_progress_files()
 #        progress_file = progress_files[base_name]
 #        fl = open(progress_file, 'w')
 #        fl.write(content)
 #        fl.close()
 #
 #    def get_progress_files(self):
 #        return self.progress_files