# uv_spec

A simple commandline tool that takes some calibration data and an unknown 
sample file file and returns the spectra plot of the calibration data and
the concentration of the unknown sample.

The tool takes the form
::
    uv_spec <calibration file> <unknown sample file>

To install and see a demo run the following:
::
    git clone https://github.com/doconnell2020/uv_spec.git

    cd uv_spec

    poetry install

    poetry run python uv_spec demo

The special `demo` argument uses the sample files found in the uv_spec/data
directory