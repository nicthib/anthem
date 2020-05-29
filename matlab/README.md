# mlauvi: An audiovisualization tool for neuroimaging datasets

## Introduction

MatLab AUdioVIsualizer (MLAUVI) is a tool that can create beautiful audiovisualizations of neuroimaging (and other) datasets. MLAUVI allows you to adjust a variety of parameters to create an effective audiovisualization, and even allows you to save settings if you want to tweak parameters in the future.

### Requirements:
- MATLAB (2017 or later - previous versions have not been tested)
- ffmpeg (required for combined audio/video files)
- Some data (example data is included to help you get yours into the proper format)

## Installation

1. Clone or download this repository.
2. Make sure you have ffmpeg installed.
    - For mac/linux, ffmpeg can be easily installed using brew: `brew install ffmpeg`
    - For windows, you can [follow this guide](https://github.com/adaptlearning/adapt_authoring/wiki/Installing-FFmpeg) for a straightforward installation.
3. In order to point Matlab to your ffmpeg installation, first navigate to the `mlauvi` folder and then input:
    - (mac/linux) if installed with brew, run `readlink $(which ffmpeg) > ffmpegpath.txt`. Otherwise, `which ffmpeg > ffmpegpath.txt` should work.
    - (windows) `where ffmpeg > ffmpegpath.txt`
4. Open and run `mlauvi.m`. Make sure to select "Add to Path" if prompted.
5. You are now ready to create some cool audiovisualizations!

## Demo: Creating you first audiovisualization
1. Load a demo dataset by choosing `Load > from .mat` from the toolbar.
2. Choose a .mat file from  `mlauvi/demodata/`.
3. When prompted `Choose Temporal Variable`, choose the variable T from the list.
4. Similarly, when prompted `Choose Spatial Variable`, choose the variable S from the list.
5. Your GUI should now update and look like this:
<p align="center">
<img src="https://images2.imgbox.com/b8/0c/WcdfoyKd_o.png?format=750w" width="75%">
</p>
6. Now that you have the raw data loaded, you can either convert the imported data for audiovisualization by pressing the button `Update H'`, or modify some setting before doing so. 

#### `data parameters`
This box has options for adjusting:
- Framerate of the outputted video (frames per second)
- Brightness
- % Range of data you want to output.

#### `audio parameters`
When converting data to audio, timecourses are mapped onto a sequence of notes, with the first timecourse as the lowest note and each subsequent timecourse a higher note. These options control the parameters of that scale and when a note is played.
- `Threshold`, the minimum value at which a note is played
- `Octave shift`, an integer that increases/decreases the pitch of the outputted audio
- `Scale type`, the arrangement of notes you want
    - As a general rule, the note range should fit on a standard 88 key piano. You will see a warning in the `Status` box if you selected a note arrangement that does not fit within this range.
    - For data with very few timecourses (~10), you can spread the notes out much more than if you have a larger number of timecourses
    - See the `Scale` section for more details on what these options mean.
- `Key`, the note that your first component 
