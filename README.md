=======
uv_spec
=======

A simple commandline tool that takes some calibration data and an unknown 
sample file and returns the spectra plot of the calibration data and
the concentration of the unknown sample.

The tool takes the form
::
    uv_spec -c data.csv -s sample.csv -cn -r 5

When run you will be asked if either the calibration or sample data requires
normalisation (blank subtraction).


====
Installation
====
To install and see a demo, run the following:
::
    git clone https://github.com/doconnell2020/uv_spec.git

    cd uv_spec

    uv run ./uv_spec.py --demo    

The special "demo" argument uses the sample files found in the uv_spec/data
directory
