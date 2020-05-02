import os, shutil
import sys
from common.tools import *

def get_section(data, id_section, len_section):
    return data[id_section*SECTION_SIZE:(id_section+len_section)*SECTION_SIZE]
def extract_rsc(filename, out=None, verbose=False):
    if verbose:
        print("Extracting from "+filename+".rsc...")
    with open(filename+".rsc", "rb") as file:
        data = file.read()
        file.close()
    if not os.path.exists(out):
        os.makedirs(out, exist_ok=True)
    else:
        shutil.rmtree(out)
        os.mkdir(out)
    str_xml = "<obj>\n"
    off = 0xea
    header = get_section(data, value(data[off:off+2]), value(data[off+2:off+4]))
    off += 0xc
    off_head = 0x0
    str_xml += "\t<version>"+VERSION+"</version> <!-- Version of the extractor -->\n"
    str_xml += "\t<files>\n"
    nb_ent = 0
    dict_types = dict()
    while value(header[off_head:off_head+2])>0:
        if nb_ent==0:
            str_xml += "\t\t<type>\n"
            nb_ent = value(data[off+2:off+4])
            off += 0x8
        data_file = get_section(data, value(data[off:off+2]), value(data[off+2:off+4]))
        size = value(header[off_head:off_head+2])
        num = value(header[off_head+4:off_head+6])
        if num!=(value(data[off+6:off+8])&(~0x8000)):
            print("Not matching!", hex(num), hex(value(data[off+6:off+8])))
        mime_type = header[off_head+6:off_head+size-2].decode(encoding="ascii")
        if mime_type in MIME_TYPES:
            real_type = MIME_TYPES[mime_type]
        else:
            real_type = mime_type.lower()
        if real_type in dict_types:
            dict_types[real_type] += 1
        else:
            dict_types[real_type] = 1
        str_xml += "\t\t\t<file>"+str(num)+"."+real_type+"</file>\n"
        with open(out+os.path.sep+str(num)+"."+real_type, "wb") as file:
            file.write(data_file)
            file.close()
        off_head+=size
        off += 0xc
        nb_ent -= 1
        if nb_ent==0:
            str_xml += "\t\t</type>\n"
    str_xml += "\t</files>\n"
    str_xml += "</obj>"
    with open(out+os.path.sep+"rsc.xml", "w") as file:
        file.write(str_xml)
        file.close()

def search_rsc(path=".", out=None, verbose=False):
    if out==None:
        out = path
    lst = os.listdir(path)
    for elt in lst:
        if elt.split(".")[-1]=="rsc":
            try:
                extract_rsc(path+os.path.sep+elt[:-4], out+os.path.sep+elt[:-4], verbose)
            except:pass
        elif os.path.isdir(path+os.path.sep+elt):
            search_rsc(path+os.path.sep+elt, out+os.path.sep+elt, verbose)

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
        search_rsc(arg[end_opt], arg[end_opt+1], verbose=verbose)
    else:
        search_rsc(arg[end_opt], verbose=verbose)
else:
    print("Usage: "+arg[0]+" <options> from_path [output_dir]\n\nOptions: \n -v Verbose")
