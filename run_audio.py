import os
from Library import Audio
from Library import AudioUtils
from matplotlib import pyplot as plt
audio_input_folder = '/media/dieter/Extreme SSD/audio_test/2024_03_17_Ind03'
audio_output_folder = '/media/dieter/Extreme SSD/processed_audio'

mat_files, _ = AudioUtils.get_mat_files(audio_input_folder)
current_file = os.path.join(audio_input_folder, mat_files[0])
data = AudioUtils.read_mat_file(current_file)
data = AudioUtils.preprocess_channels(data, inplace=True)
#%%
energy = data ** 2
smoothed_energy = AudioUtils.boxcar_smooth(energy, window_size=32)
#%%
plt.figure()
plt.plot(energy[0:150000, 0], label='Raw Energy')
plt.plot(smoothed_energy[0:150000, 0], label='Smoothed Energy')
plt.legend()
plt.show()