import os.path as path
from os.path import basename

folders = [
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_01_30_3Ind_manuel',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_01_31_Ind05_manuel',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_02_01_Ind02',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_02_02_Ind03',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_03_17_Ind03',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_03_17_Ind05',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_03_18_Ind01',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_03_18_Ind04',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_03_19_Ind02',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_04_11_Ind02',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_04_11_Ind08',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_04_12_Ind01',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_04_12_Ind06',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_04_13_Ind03',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_04_13_Ind09',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_04_14_Ind05',
    '/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_04_14_Ind07',
'/media/dieter/Mmicrotis_search_Dieter/Mmicrotis_audio/2024_04_15_Ind04'
]

base_folders = []
for folders in folders:
    base_name = path.basename(folders)
    new = 'Mmicrotis_video/' + base_name
    base_folders.append(new)
