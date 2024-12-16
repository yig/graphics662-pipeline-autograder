#!/usr/bin/env python3

from datetime import datetime, date
import webbrowser
import numpy as np
import os, sys, subprocess, multiprocessing
from pathlib import Path
from collections import namedtuple
import imgdiff


######
###### Some global definitions
######

## Where are the tests stored?
## https://stackoverflow.com/questions/4060221/how-to-reliably-open-a-file-in-the-same-directory-as-a-python-script
## assert os.path.abspath( os.pwd() ) == os.path.dir( os.path.abspath( __file__ ) )
## __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
assert len( sys.path[0] ) > 0
HERE_DIR = Path( sys.path[0] )
TRUTH_DIR = HERE_DIR / 'reference_images'

## Where is the output stored?
OUTPUT_DIR = HERE_DIR / f'autograde-{datetime.now().strftime("%Y-%m-%d at %H-%M-%S")}'
OUTPUT_HTML = Path( str(OUTPUT_DIR) + '.html' )

######
###### Let's start processing
######

## A helper function to run one test. This needs to be out here
## so that multiprocessing finds it.
def run_one( exepath, jsonpath, output_dir ):
    print( f"Starting {jsonpath.name}..." )
    ## All this str(.as_posix()) business is to solve a problem on some Windows machines
    ## the complained that a WindowsPath is not iterable.
    subprocess.run([
        str(Path(exepath).as_posix()),
        '--width', '500',
        '--height', '500',
        '--screenshot',
        str(jsonpath2outputpath( jsonpath, output_dir ).as_posix()),
        str(jsonpath.as_posix()),
        ])
    print( f"Finished {jsonpath.name}." )
def jsonpath2outputpath( jsonpath, output_dir ): return output_dir / ( jsonpath.stem + '.png' )

## Since we use multiprocessing to run tests in parallel, we need to make
## sure this file can be imported without actually running the code.
if __name__ == '__main__':
    
    import argparse
    def path_exists( path ):
        if not Path(path).exists(): raise argparse.ArgumentTypeError(f"Path does not exist: {path}")
        return path
    parser = argparse.ArgumentParser( description = 'Grade Shaders.' )
    # parser.add_argument( 'command', choices = ['grade', 'truth'], help = 'The command to run.' )
    parser.add_argument( 'executable', type=path_exists, help = 'The path to the pipeline executable.' )
    parser.add_argument( 'examples', type=path_exists, help = 'The path to the examples directory containing the JSON files.' )
    
    parser.add_argument( '--all', action = 'store_true', help = 'Whether to execute all tests.' )
    parser.add_argument( '--all-but-sampling', action = 'store_true', help = 'Whether to execute all tests except PBR with sampling.' )
    
    parser.add_argument( '--pbr-direct', action = 'store_true', help = 'Whether to execute PBR tests (no sampling).' )
    parser.add_argument( '--pbr-sampling', action = 'store_true', help = 'Whether to execute PBR tests (with environment map sampling).' )
    parser.add_argument( '--matcap', action = 'store_true', help = 'Whether to execute matcap tests.' )
    parser.add_argument( '--normalmap', action = 'store_true', help = 'Whether to execute tangent-space normal mapping tests.' )
    
    parser.add_argument( '--filter', help = 'Filter tests with a substring that must be present in the test name. Must be used with an inclusion flag.' )
    
    args = parser.parse_args()
    
    examples = [
        ( "pbr_boombox-nonormals-direct.json", ( "pbr", "direct" ) ),
        ( "pbr_bunny.json", ( "pbr", "direct" ) ),
        ( "pbr_cube2.json", ( "pbr", "direct", "normals" ) ),
        ( "pbr_earth.json", ( "pbr", "direct" ) ),
        ( "pbr_robot.json", ( "pbr", "direct", "normals" ) ),
        ( "pbr_sphere-dielectric-direct-lights.json", ( "pbr", "direct" ) ),
        ( "pbr_sphere-dielectric-direct.json", ( "pbr", "direct" ) ),
        ( "pbr_sphere-metal-direct.json", ( "pbr", "direct" ) ),
        ( "pbr_boombox-normals-direct.json", ( "pbr", "direct", "normals" ) ),
        ( "pbr_boombox-normals-sampled.json", ( "pbr", "sampled", "normals" ) ),
        ( "pbr_boombox-nonormals-sampled.json", ( "pbr", "sampled" ) ),
        ( "matcap_bunny.json", ( "matcap" ) ),
        ( "matcap_head.json", ( "matcap" ) ),
        ( "matcap_sphere.json", ( "matcap" ) )
    ]
    
    ## Collect all tests
    all_tests = [
        example for example, attribs in examples
        if
            args.all
            or (args.all_but_sampling and not "sampling" in attribs)
            or (args.pbr_sampling and "sampled" in attribs)
            or (args.pbr_direct and "direct" in attribs)
            or (args.normalmap and "normals" in attribs)
            or (args.matcap and "matcap" in attribs)
    ]
    if args.filter is not None: all_tests = [ example for example in all_tests if args.filter in example ]
    all_tests = [ Path(args.examples) / jsonname for jsonname in all_tests ]
    
    ## Create the output directory
    print( OUTPUT_DIR )
    assert not OUTPUT_DIR.exists()
    os.makedirs( OUTPUT_DIR )
    assert OUTPUT_DIR.exists()
    
    ## Run all tests in parallel:
    ## We must wrap the output in a list(), because otherwise nothing happens.
    ## We must pass the output directory as a parameter,
    ## since it is derived from the current time and that may be different in
    ## other instantiations.
    # with multiprocessing.Pool() as pool: list(pool.starmap( run_one, ( (args.executable,test,OUTPUT_DIR) for test in all_tests ), 1 ))
    ## Run all tests serially:
    for test in all_tests: run_one( args.executable, test, OUTPUT_DIR )
    
    ## Organize them into categories
    from collections import OrderedDict
    category2test = OrderedDict()
    Test = namedtuple('Test', ['jsonpath', 'outputpath'])
    for jsonpath in all_tests:
        category = jsonpath.name.split('_')[0]
        category2test.setdefault( category, [] ).append( Test( jsonpath, jsonpath2outputpath( jsonpath, OUTPUT_DIR ) ) )
    
    ## Measure and save the output
    out = open( OUTPUT_HTML, 'w' )
    out.write( open( HERE_DIR / "header.html" ).read() )
    
    ## Iterate over categories
    for category in category2test.keys():
        tests = category2test[ category ]
        
        out.write( f'<h3>{category} tests</h3>' )
        out.write( '''
    <table style="width:100%">
    <tr><th>Scene</th><th>Correct</th><th>Yours</th><th>Difference</th><th>Score</th></tr>
    ''' )
    
        for test in tests:
            ## Ground truth images are next to the json files.
            gt_path = TRUTH_DIR / test.jsonpath.with_suffix( '.png' ).name
            ## Create a difference image.
            if test.outputpath.exists():
                diff_path = test.outputpath.parent / (test.outputpath.stem + '-diff.png')
                try:
                    diffimg = imgdiff.mindiff_in_neighborhood( gt_path, test.outputpath, diff_path )
                except TypeError:
                    diffimg = imgdiff.mindiff_in_neighborhood( gt_path.parent / ( gt_path.stem + '@2x.png' ), test.outputpath, diff_path )
                ## The score is the average absolute pixel difference.
                ## These values range from 0 to 255.
                ## Convert them to [0,1] and then scale to [100,0].
                ## Boost differences by an extra 10x, since pixels may be subtly different.
                score = int(round( max( 0, 100 - np.clip( np.average( np.abs( diffimg ) )/255, 0, 1 )*100*10 ) ))
                diff_path_URI = diff_path.relative_to(HERE_DIR).as_posix()
            else:
                diff_path_URI = ""
                score = 0
            
            out.write( f'''
    <tr>
    <td style="width:15%">{test.jsonpath.name}</td>
    <td style="width:25%"><img src="{gt_path.relative_to(HERE_DIR).as_posix()}"></td>
    <td style="width:25%"><img src="{test.outputpath.relative_to(HERE_DIR).as_posix()}"></td>
    <td style="width:25%"><img src="{diff_path_URI}"></td>
    <td style="width:10%"><label>{score}</label></td>
    </tr>
    ''' )
        
        out.write( '</table>' )
        out.write( '' )
    
    ###
    ### Footer
    ###
    
    out.write( '</body>' )
    out.write( '</html>' )
    out.close()
    
    print( 'Saved:', OUTPUT_HTML )
    
    webbrowser.open( OUTPUT_HTML.as_uri() )
