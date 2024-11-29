# Shader Autograder

This autograder is designed for [graphics662-pipeline](http://github.com/yig/graphics662-pipeline).
Download this repository and run it via:

    python3 autograde.py --all path/to/build/pipeline path/to/examples

If you download `graphics662-pipeline-autograder` and place it
next to `graphics662-pipeline` in the filesystem, then the command would be:

    python3 autograde.py --all ../graphics662-pipeline/build/pipeline ../graphics662-pipeline/examples

Instead of `--all`, you can also specify one or more of:

    --all-but-sampling  Whether to execute all tests except PBR with sampling.
    --pbr-direct              Whether to execute PBR tests (no sampling).
    --pbr-sampling              Whether to execute PBR tests (with environment map sampling).
    --matcap             Whether to execute matcap tests.
    --normalmap          Whether to execute tangent-space normal mapping tests.

The numbers in the score column measure the average absolute difference in pixel values between the ground truth and the tested executable magnified by 10.
(Because of aliasing artifacts near the boundaries of shapes, the difference actually uses the minimum to a pixel or its 8 neighbors.)
A perfect score is 100. A score of 0 means that the average absolute difference is 10%.
This does not translate to a grade for the assignment.

## Installing

The autograder depends on Python 3.x and the following modules: `numpy` and `pillow`. You can install the modules via:

    pip3 install numpy pillow

or install the dependencies via `pip` (possibly in a virtual environment via `python3 -m venv venv` and `source venv/bin/activate`):

    pip install -r requirements.txt

## Changing the examples

The autograder runs the `pipeline` executable on some JSON files in the
`examples` directory. If you create a new example for students, an easy way to generating the ground truth images is to run:

    parallel path/to/solution/build/pipeline --width 500 --height 500 --screenshot 'reference_images/{/.}@2x.png' '{}' ::: examples/file.json
    parallel path/to/solution/build/pipeline --width 250 --height 250 --screenshot 'reference_images/{/.}.png' '{}' ::: examples/file.json

using the solution `pipeline` executable. The reason images with both 250 and 500 is for students with high-DPI screens.

For the current (as of this writing) [graphics662-pipeline](http://github.com/yig/graphics662-pipeline), the examples argument for parallel could be:

```
../examples/matcap_bunny.json ../examples/matcap_head.json ../examples/matcap_sphere.json ../examples/pbr_boombox-nonormals-direct.json ../examples/pbr_boombox-nonormals-sampled.json ../examples/pbr_boombox-normals-direct.json ../examples/pbr_boombox-normals-sampled.json ../examples/pbr_bunny.json ../examples/pbr_cube2.json ../examples/pbr_earth.json ../examples/pbr_robot.json ../examples/pbr_sphere-dielectric-direct-lights.json ../examples/pbr_sphere-dielectric-direct.json ../examples/pbr_sphere-dielectric-sampled.json ../examples/pbr_sphere-metal-direct.json ../examples/pbr_sphere-metal-sampled.json
```
