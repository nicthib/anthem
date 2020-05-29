import midi2audio, sys
from midi2audio import FluidSynth
filein = sys.argv[1] + '.mid'
fileout = sys.argv[1] + '.wav'
midi2audio filein fileout 