# Shader Autograder

This autograder is designed for [graphics101-raytracing](http://github.com/yig/graphics101-pipeline).
Download this repository and run it via:

    python3 autograde.py path/to/build/pipeline path/to/examples

If you download `graphics101-pipeline-autograder` and place it
next to `graphics101-pipeline` in the filesystem, then the command would be:

    python3 autograde.py ../graphics101-pipeline/build/pipeline ../graphics101-pipeline/examples

The numbers in the score column measure the average absolute difference in pixel values between the ground truth and the tested executable magnified by 10.
(Because of aliasing artifacts near the boundaries of shapes, the difference actually uses the minimum to a pixel or its 8 neighbors.)
A perfect score is 100. A score of 0 means that the average absolute difference is 10%.
This does not translate to a grade for the assignment.

## Installing

The autograder depends on Python 3.x and the following modules: `numpy` and `pillow`. You can install the modules via:

    pip3 install numpy pillow

or install the [Poetry](https://python-poetry.org/) dependency manager and run:

    poetry install
    poetry shell

## Changing the examples

The autograder runs the `pipeline` executable on some JSON files in the
`examples` directory. If you create a new example for students, an easy way to generating the ground truth images is to run:

    parallel path/to/solution/build/pipeline --width 500 --width 500 --screenshot 'reference_images/{.}@2x.png' '{}' ::: examples/file.json
    parallel path/to/solution/build/pipeline --width 250 --width 250 --screenshot 'reference_images/{.}.png' '{}' ::: examples/file.json

using the solution `pipeline` executable. The reason images with both 250 and 500 is for students with high-DPI screens.
