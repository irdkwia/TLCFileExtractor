# TLC files extractor

A command-line tool for extracting from various files The Learning Company games written in python 3, which includes: 

- A script for extracting files from .inx/.bul
- A script for extracting files from a .bul file alone
- A script for building .inx/.bul from a folder
- A script for extracting images from .ao/.rgb

## How to install it

You need to have python 3.x installed (see https://www.python.org/downloads/)

For the .ao/.rgb files extractor, you need to install the pillow package for python3 (see https://pillow.readthedocs.io/en/stable/installation.html)

Then, clone this repository


## How to use it

### Extracting from .bul/.inx files

Run in the command line the extract_inx.py script: 

python3 extract\_inx.py <options> inx\_file \[output\_dir\]

where "inx\_file" is the path to the .inx file

and "output\_dir" (optional) is the folder where the files will be extracted; if not given it will be in the same folder as the .inx file; note that the files will be extracted in a subfolder named after their .bul file

the options available are: 

-v Verbose: prints the list of files extracted
-L Extract leftovers: create .bul files in output\_dir that contains the parts of original .bul files that were not extracted, i. e. possibly files that are not referenced anymore by the .inx file but still in .bul files

### Extracting from a .bul file alone

Run in the command line the extract_inx.py script: 

python3 extract\_bul.py <options> bul\_file \[output\_dir\]

where "bul\_file" is the path to the .bul file

and "output\_dir" (optional) is the folder where the files will be extracted; if not given it will be in the same folder as the .bul file; note that they will be extracted in a subfolder named after the .bul file

the only option currently available is: 

-v Verbose: prints the list of files extracted

NOTE: This TRIES to extract from .bul files, searching for possibles filenames in it. As there is no .inx file attached, it is impossible to exactly determine where are the files, so the result will not be as accurate as it would be with a .inx file.

### Building .bul/.inx files

Run in the command line the extract_inx.py script: 

python3 build\_inx.py <options> from\_path \[output\_dir\]

where "from\_path" is the folder where are located the files that will be in the .bul archives. Any folder in it represents a .bul file and their contents the content of the .bul archive.

and "output\_dir" (optional) is the folder where the files will be extracted; if not given it will be in the same folder as the .inx file

the only option currently available is: 

-v Verbose: prints the list of files extracted

### Extracting from .ao/.rgb files

Run in the command line the extract_aorgb.py script: 

python3 extract\_aorgb.py <options> from\_path \[output\_dir\]

where "from\_path" is the folder where are located the .ao and .rgb files

and "output\_dir" (optional) is the folder where the image files will be extracted; if not given it will be the same as from\_path

the only option currently available is: 

-v Verbose: prints the list of .ao/.rgb files extracted
