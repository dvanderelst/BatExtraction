import os
import h5py


def read_channel_data(output_folder, channel_idx, chunk_nr = 0):
    chunk_size = 20 * 400 * 1000
    start_index = chunk_nr * chunk_size
    end_index = (chunk_nr + 1) * chunk_size
    hdf5_filename = os.path.join(output_folder, f'channel_{channel_idx}.hdf5')
    with h5py.File(hdf5_filename, 'r') as hdf5_file:
        dataset = hdf5_file[f'data']
        data = dataset[start_index:end_index]
    return data