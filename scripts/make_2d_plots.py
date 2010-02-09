#!/usr/bin/env python
# File created on 09 Feb 2010
#file make_2d_plots.py

from __future__ import division

__author__ = "Jesse Stombaugh"
__copyright__ = "Copyright 2010, The QIIME project"
__credits__ = ["Jesse Stombaugh"]
__license__ = "GPL"
__version__ = "1.0-dev"
__maintainer__ = "Jesse Stombaugh"
__email__ = "jesse.stombaugh@colorado.edu"
__status__ = "Pre-release"
 

from qiime.util import parse_command_line_parameters
from optparse import make_option
from qiime.make_2d_plots import generate_2d_plots
from qiime.parse import parse_map,parse_coords,group_by_field,group_by_fields
import shutil
import os
from qiime.util import get_qiime_project_dir
from qiime.make_3d_plots import combine_map_label_cols,get_map,get_coord,\
                         process_colorby,create_dir

script_description = """This script generates 2D PCoA plots using the principal \
coordinates file generated by performing beta diversity measures of an OTU \
table."""

script_usage = """
Requirements:
MatPlotLib 0.98.5.2

Example 1: Create 2D plots from only the pca/pcoa data:

Usage: make_2d_plots.py -i raw_pca_data.txt

Example 2: Create two separate html files, one for Day and one for Type:

Usage: make_2d_plots.py -i raw_pca_data.txt -m input_map.txt -b 'Day,Type'

Example 3: Create 2D plots for a combination of label headers from a mapping 
file:

Usage: make_2d_plots.py -i raw_pca_data.txt -m input_map.txt 
-b 'Type&&Day' -o ./test/
"""

required_options = [\
 # Example required option
 #make_option('-i','--input_dir',help='the input directory'),\
 make_option('-i', '--coord_fname', dest='coord_fname', \
 help='This is the path to the principal coordinates file (i.e., resulting file \
from principal_coordinates.py)')
]

optional_options = [\
 # Example optional option
 #make_option('-o','--output_dir',help='the output directory [default: %default]'),\
 make_option('-m', '--map_fname', dest='map_fname', \
     help='This is the user-generated mapping file [default=%default]'),
 make_option('-b', '--colorby', dest='colorby',\
     help='This is the categories to color by in the plots from the \
user-generated mapping file. The categories must match the name of a column \
header in the mapping file exactly and multiple categories can be list by comma \
separating them without spaces. The user can also combine columns in the \
mapping file by separating the categories by "&&" without spaces \
[default=%default]'),
 make_option('-o', '--dir_path', dest='dir_path',\
     help='This is the location where the resulting output should be written \
[default=%default]',default='')
]

def main():
    option_parser, opts, args = parse_command_line_parameters(
      script_description=script_description,
      script_usage=script_usage,
      version=__version__,
      required_options=required_options,
      optional_options=optional_options)

    data = {}

    #Open and get coord data
    data['coord'] = get_coord(opts.coord_fname)

    #Open and get mapping data, if none supplied create a pseudo mapping
    #file
    if opts.map_fname:
        mapping = get_map(opts, data)
    else:
        data['map']=(([['#SampleID','Sample']]))
        for i in range(len(data['coord'][0])):
            data['map'].append([data['coord'][0][i],'Sample'])

    #Determine which mapping headers to color by, if none given, color by
    #Sample ID's
    if opts.colorby:
        prefs,data=process_colorby(opts.colorby,data)
    else:
        prefs={}
        prefs['Sample']={}
        prefs['Sample']['column']='#SampleID'

    filepath=opts.coord_fname
    filename=filepath.strip().split('/')[-1]

    qiime_dir=get_qiime_project_dir()

    js_path=os.path.join(qiime_dir,'support_files/js/')

    dir_path=opts.dir_path
    if dir_path and not dir_path.endswith("/"):
        dir_path=dir_path+"/"

    dir_path=create_dir(dir_path,'2d_plots_')

    js_dir_path = dir_path+'/js/'
    try:
        os.mkdir(js_dir_path)
    except OSError:
        pass

    shutil.copyfile(os.path.join(js_path,'/overlib.js'), js_dir_path+'overlib.js')

    try:
        action = generate_2d_plots
    except NameError:
        action = None
    #Place this outside try/except so we don't mask NameError in action
    if action:
        action(prefs, data, dir_path,filename)


if __name__ == "__main__":
    main()