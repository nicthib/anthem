from os.path import realpath, join
self_fns = {
'fr':'entry',
'st_p':'entry',
'en_p':'entry',
'baseline':'entry',
'brightness':'entry',
'threshold':'entry',
'oct_add':'entry',
'scale_type':'entry',
'key':'entry',
'audio_format':'entry',
'Wshow':'entry',
'cmapchoice':'entry', 
'speed':'entry',
'file_in':'entry',
'file_out':'entry',
'save_path':'entry',
'Wshow_arr':'value'}

oct_add_opts = ['0','1','2','3','4','5']

scale_type_opts = ['Chromatic (12/oct)','Major scale (7/oct)','Minor scale (7/oct)', 
'Maj. triad (3/oct)','Min. triad (3/oct)','Aug. triad (3/oct)',
'Dim. triad (3/oct)','Maj. 6th (4/oct)','Min. 6th (4/oct)',
'Maj. 7th (4/oct)','Min. 7th (4/oct)','Aug. 7th (4/oct)',
'Dim. 7th (4/oct)','Maj. 7/9 (5/oct)','Min. 7/9 (5/oct)']
key_opts = ['C','C#/D♭','D','D#/E♭','E','F','F#/G♭','G','G#/A♭','A','A#/B♭','B']

cmaps_opts = tuple(sorted(['viridis', 'plasma', 'inferno', 'magma', 'cividis','binary', 
'bone', 'pink','spring', 'summer', 'autumn', 'winter', 'cool','hot','copper','Spectral', 
'coolwarm', 'bwr', 'seismic','twilight', 'hsv', 'Paired', 'prism', 'ocean', 
'terrain','brg', 'rainbow', 'jet'],key=lambda s: s.lower()))

pth=realpath(__file__)
example_files_decomp = [join(pth,d) for d in ['demo1.mat','demo2.mat','demo3.mat','demo4.mat']]
example_files_raw = [join(pth,d) for d in ['raw1.mat','raw2.mat']]


