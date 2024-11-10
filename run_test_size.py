import numpy as np

# Create an example array with dtype float64 and <f8
data_float64 = np.random.rand(8000000, 25).astype(np.float64)
data_f8 = data_float64.astype('<f8')

# Save both with and without compression
np.save("float64_data.npy", data_float64)
np.save("f8_data.npy", data_f8)
np.savez_compressed("float64_data_compressed.npz", data=data_float64)
np.savez_compressed("f8_data_compressed.npz", data=data_f8)