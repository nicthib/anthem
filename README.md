pyanthem: an audiovisualization tool to make your data more interesting
==================================================

pyanthem is a python tool that transforms three-dimensional time-varying datasets into a colorful, audible format. 
pyanthem boasts a variety of features: 
   1) Raw data decomposition
   2) Video and audio preview
   3) A broad variety of video and audio parameters
   4) Command-line reproduction via config files

## Table of Contents

- [Requirements](#requirements) 
- [Installation](#installation)
- [Features](#features)
- [Contributing](#contributing)
- [Team](#team)
- [FAQ](#faq)
- [Support](#support)
- [License](#license)

Requirements
------------
Python 3:
   Currently, pyanthem is tested to work on [Python][1] 3.6+. This will be 
   updated as more versions are tested.

pip:
   pip is needed for the installation of the pyanthem module and its
   dependencies.  Most python versions will have pip installed already, 
   see the  [pip installation][2] page for instructions if you do not 
   have pip.

git (optional):
  [git][3] allows pyanthem to download external audio files quickly and 
  easily.

ffmpeg (optional):
   [ffmpeg][4] enables merging video and audio files into a single output.

[1]: https://www.python.org/
[2]: https://pip.pypa.io/en/latest/installing/
[3]: https://git-scm.com/
[4]: https://ffmpeg.org/

## Installation

Using pip:

   ``
   pip install pyanthem
   ``
   
   Note: installation could take some time to add the required packages, 
   depending on what is already in your environment. To install the 
   optional "Piano" audio engine, import and then use the download command:
   
   ```
   import pyanthem
   pyanthem.AE_download()
   ```
   Note: This requires git. If you do not have git, you will need to 
   follow the alternate installation guide in the [FAQ](#faq).
   
## Contributing

### Step 1

- **Option 1**
    - 🍴 Fork this repo!

- **Option 2**
    - 👯 Clone this repo to your local machine using 
    `git clone https://github.com/nicthib/pyanthem.git`

### Step 2

- **HACK AWAY!**

### Step 3

- 🔃 Create a new pull request using <a href="https://github.com/nicthib/pyanthem/compare/" target="_blank">`https://github.com/nicthib/pyanthem/compare/`</a>.

## Team

| **Nic Thibodeaux** |
| :---: |
| ![](https://avatars1.githubusercontent.com/u/34455769?v=3&s=200)|
| <a href="http://github.com/nicthib" target="_blank">`github.com/nicthib`</a> |

## FAQ

- **How do I do *specifically* so and so?**
    - No problem! Just do this.

## Support

- Twitter at <a href="http://twitter.com/nicthibs" target="_blank">`@nicthibs`</a>

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**
