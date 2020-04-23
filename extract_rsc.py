import os, shutil
import sys
from common.tools import *

SECTION_SIZE = 0x200
MIME_TYPES = {"WAVE":"wav", "RRGB":"rgb", "ASEQ":"ao", "JPEG":"jpg", "TEXT":"txt", "NFNT":"nfnt"}

def get_section(data, id_section, len_section):
    return data[id_section*SECTION_SIZE:(id_section+len_section)*SECTION_SIZE]
def extract_rsc(filename, out=None, verbose=False):
    in_dir = os.path.dirname(filename)
    if in_dir=='':
        in_dir = '.'
    if out==None:
        out = in_dir
    with open(filename, "rb") as file:
        data = file.read()
        file.close()
    off = 0xea
    header = get_section(data, value(data[off:off+2]), value(data[off+2:off+4]))
    off += 0xc
    off_head = 0x0
    nb_ent = value(data[off+2:off+4])
    off += 0x8
    dict_types = dict()
    while value(header[off_head:off_head+2])>0:
        if verbose:
            print(hex(off))
        data_file = get_section(data, value(data[off:off+2]), value(data[off+2:off+4]))
        size = value(header[off_head:off_head+2])
        mime_type = header[off_head+6:off_head+10].replace(b'\x00', b'').decode(encoding="ascii")
        if mime_type in MIME_TYPES:
            real_type = MIME_TYPES[mime_type]
        else:
            real_type = mime_type.lower()
        if real_type in dict_types:
            dict_types[real_type] += 1
        else:
            dict_types[real_type] = 1
        with open(out+os.path.sep+str(dict_types[real_type])+"."+real_type, "wb") as file:
            file.write(data_file)
            file.close()
        off_head+=size
        off += 0xc
        nb_ent -= 1
        if nb_ent==0:
            nb_ent = value(data[off+2:off+4])
            off += 0x8

arg = sys.argv
end_opt = 1
lst_opts = []
while end_opt<len(arg):
    opt = arg[end_opt]
    if opt[0]!="-":
        break
    else:
        lst_opts.append(opt)
    end_opt += 1
if len(arg)-end_opt>0:
    verbose = False
    if "-v" in lst_opts:
        verbose = True
    if len(arg)-end_opt>=2:
        extract_rsc(arg[end_opt], arg[end_opt+1], verbose=verbose)
    else:
        extract_rsc(arg[end_opt], verbose=verbose)
else:
    print("Usage: "+arg[0]+" <options> rsc_file [output_dir]\n\nOptions: \n -v Verbose")
