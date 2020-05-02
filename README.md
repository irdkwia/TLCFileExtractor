# TLC files extractor

A command-line tool for extracting from various files of The Learning Company games written in python 3, which includes: 

- A script for extracting files from .inx/.bul
- A script for extracting files from a .bul file alone
- A script for building .inx/.bul from a folder
- A script for extracting images from .ao/.rgb
- A script for building .ao/.rgb from images
- A script for extracting files from .rsc
- A script for building .rsc files

## How to install it

You need to have python 3.x installed (see https://www.python.org/downloads/)

For the .ao/.rgb files extractor/builder, you need to install the pillow package for python3 (see https://pillow.readthedocs.io/en/stable/installation.html)

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

Run in the command line the extract_bul.py script: 

python3 extract\_bul.py <options> bul\_file \[output\_dir\]

where "bul\_file" is the path to the .bul file

and "output\_dir" (optional) is the folder where the files will be extracted; if not given it will be in the same folder as the .bul file; note that they will be extracted in a subfolder named after the .bul file

the only option currently available is: 

-v Verbose: prints the list of files extracted

NOTE: This TRIES to extract from .bul files, searching for possibles filenames in it. As there is no .inx file attached, it is impossible to exactly determine where are the files, so the result will not be as accurate as it would be with a .inx file.

### Building .bul/.inx files

Run in the command line the build_inx.py script: 

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

Note: Since this version, the extractor adds an xml file called "anim.xml" that stores additionnal metadata, mainly for the animation, which is useful to build an .ao/.rgb file again. If you extracted and edited the extracted images with an older version then extract from them again and replace the images by the one you edited.

### Building .ao/.rgb files

Run in the command line the build_aorgb.py script: 

python3 build\_aorgb.py <options> from\_path \[output\_dir\]

where "from\_path" is the folder where are located the image files you want to build; it recognizes each folder with a "anim.xml" file in it as a .ao/.rgb file to build

and "output\_dir" (optional) is the folder where the .ao/.rgb files will be built; if not given it will be the same as from\_path

the options available are: 

-v Verbose: prints the list of .ao/.rgb files built
-m=X Force mode X: Forces the animation files to be built using mode X instead of the one specified in animation (tag "unknown2" or "mode" in the header)

Notes: 
There are currently 2 modes supported ("1" and "2"). The 1st mode allows only 256 colors and uses a .rgb file for the palette while the 2nd mode allows more colors and transparency levels but is more memory-consuming (about 2 to 3 times more than mode 1).
As mode 1 is not optimized as it should, the algorithm is REALLY slow, so it is recommended to only build the .ao/.rgb files you need to. Also, there are still some parts of the metadata that are unknown, hence the "unknown" tags in the xml file. In later versions, the xml structure will be altered so these xml files could be incompatible. As a result, always build with the same version you extracted them.

### Extracting from .rsc files

Run in the command line the extract_rsc.py script: 

python3 extract\_rsc.py <options> from\_path \[output\_dir\]

where "from\_path" is the folder where are located the .rsc files

and "output\_dir" (optional) is the folder where the files will be extracted; if not given it will be in the same folder as the .rsc files; the files have a default as they are not named in the rsc file

the only option currently available is: 

-v Verbose: prints the list of files extracted

### Building .rsc files

Run in the command line the build_rsc.py script: 

python3 build\_rsc.py <options> from\_path \[output\_dir\]

where "from\_path" is the folder where are located the resources files you want to build; it recognizes each folder with a "rsc.xml" file in it as a .rsc file to build

and "output\_dir" (optional) is the folder where the .rsc files will be built; if not given it will be the same as from\_path

the only option currently available is: 

-v Verbose: prints the list of .rsc files built

