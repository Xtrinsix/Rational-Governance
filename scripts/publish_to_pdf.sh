#!/bin/bash

# for OS X: 
# requires pandoc (brew install pandoc)
# requires BasicTex (manual download and install frpm pkg file http://www.tug.org/mactex/morepackages.html)
# or a full MacTex
# sudo tlmgr install lm-math
# sudo tlmgr install titlesec

# run as bash util/<filename>


curr_dir=`pwd`
output_dir="${curr_dir}/output"
temp_dir="${curr_dir}/output/temp"
chapters_dir="${curr_dir}/output/temp/chapters"
appx_dir="${curr_dir}/output/temp/appendices"
tex_dir="${curr_dir}/scripts/tex"
template_file="${temp_dir}/wise_river_template.tex"

echo $chapters_dir
mkdir -p $temp_dir
mkdir -p $chapters_dir
mkdir -p $appx_dir


echo "cp $tex_dir/wise_river_template.tex $temp_dir"
cp $tex_dir/wise_river_template.tex $temp_dir
cp $tex_dir/wise_river.cls $temp_dir
cp $tex_dir/W-BOOKPS.STY $temp_dir
python scripts/prep_tex_files.py $curr_dir $temp_dir $tex_dir/wise_river_template.tex

# pandoc --variable fontsize=12pt 1.0.0_introduction.mdown -o output/temp/chapters/1.0.0_introduction.tex
# pandoc --variable fontsize=12pt 2.09.0_doctrine_responsible_capitalism.mdown -o output/temp/chapters/2.09.0_doctrine_responsible_capitalism.tex

# echo pdflatex $template_file -output-directory=$output_dir
cd $temp_dir
# run pdflatex twice so the table of contents will be built and then inserted
xelatex `basename $template_file`
xelatex `basename $template_file`
cp *.pdf $output_dir
cd $output_dir

open wise_river_template.pdf
# # cd output
# cd scripts/tex
# pdflatex wise_river_template.tex -output-directory=../output/
# # pdflatex endGoal.tex -output-directory=output/
# open output/wise_river_template.pdf
