import time
import shutil
from Library import Utils
import os.path as path
import os

class AdminHelper:
    def __init__(self, output_folder):
        self.folders = create_output_folder_structure(output_folder, clear_existing=False)
        self.log_file_name = path.join(output_folder, 'log.txt')
        #self.log_file = open(self.log_file_name, 'w')
        #self.log_file.write(time.asctime() + '\n')
        #self.log_file.close()

    def write(self, text):
        #self.log_file = open(self.log_file_name, 'a')
        #if type(text) == list: text = Utils.list_to_line(text)
        #print(text)
        #self.log_file.write(text + '\n')
        #self.log_file.close()
        pass


    def get_output_folder(self):
        return self.folders['output_folder']

    def get_folder(self, channel, tp):
        if tp == 'led':
            return self.folders['led_folders'][channel-1]
        elif tp == 'int':
            return self.folders['int_folders'][channel-1]



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

