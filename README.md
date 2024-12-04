# BatExtraction

## Extracting the LEDs

+ Step 1: run_extract_intensities.py
    + Run this first with `boxes_only = True`

+ Step 2: run_process_intensities.py
+ Step 3: run_mark_led_videos.py

## Audio

Nomenclature: `file_index` gives the index of the audio matfiles for each session. 
Each matfile records 20 seconds of audio. So, I could have refered to the files as `chunks`. 
But since when converting the mat files to hdf5, I iterate over the files, the nomemclature stuck.

+ Step 1: run_mat_2_hdf5.py. This converts the matfiles to hdf5 files.
+ Step 2: run_audio.py.