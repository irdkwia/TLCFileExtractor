import os, sys
from xml.etree import ElementTree
from common.tools import *

def extract_resources(path, out, elt, verbose):
    path_to_rsc = os.path.dirname(sys.argv[0])
    if path_to_rsc=='':
        path_to_rsc = '.'
    path_to_rsc += os.path.sep+"res_rsc"+os.path.sep
    if verbose:
        print("Building "+elt+".rsc...")
    tree = ElementTree.parse(path+os.path.sep+elt+os.path.sep+"rsc.xml")
    root = tree.getroot()
    types = root.find("files").findall("type")
    
    with open(path_to_rsc+"header.bin", 'rb') as file:
        header = file.read()
        file.close()
    with open(path_to_rsc+"end_header.bin", 'rb') as file:
        end_header = file.read()
        file.close()
    with open(path_to_rsc+"borland.bin", 'rb') as file:
        borland = file.read()
        file.close()
    with open(path_to_rsc+"footer.bin", 'rb') as file:
        footer = file.read()
        file.close()
    size_header = len(header)+0xc+0x8*len(types)
    for t in types:
        size_header += 0xc*len(t.findall("file"))
    size_header += len(end_header)
    nb_sect_header = size_header//SECTION_SIZE
    if size_header%SECTION_SIZE!=0:
        nb_sect_header += 1
    off_1 = size_header-0xa8
    off_2 = size_header-0xcf
    off_3 = size_header-0xbd
    off_4 = size_header-0xb9
    off_5 = size_header-0xe
    sect_1 = nb_sect_header
    sect_2 = nb_sect_header+1
    sect_3 = nb_sect_header+3
    bytes_rsc = header[:0x94]+byte_value(off_1, 2)
    bytes_rsc += header[0x96:0xb6]+byte_value(off_2, 2)+byte_value(off_3, 2)+byte_value(off_4, 2)+byte_value(off_5, 2)
    bytes_rsc += header[0xbe:0xc8]+byte_value(sect_1, 2)
    bytes_rsc += header[0xca:0xd0]+byte_value(sect_2, 2)
    bytes_rsc += header[0xd2:0xd8]+byte_value(sect_3, 2)+header[0xda:]

    lst_files = []
    listing = b''
    data = b''
    for i, t in enumerate(types):
        lst_files.append([])
        for f in t.findall("file"):
            filename = f.text
            num = int(filename.split(".")[0])
            ext = filename.split(".")[1]
            for k, v in MIME_TYPES.items():
                if v==ext:
                    ext = k
                    break
            ext = ext.upper()
            with open(path+os.path.sep+elt+os.path.sep+filename, 'rb') as file:
                content = file.read()
                file.close()
            if len(content)%SECTION_SIZE!=0:
                content += bytes(SECTION_SIZE-len(content)%SECTION_SIZE)
            data += content
            lst_files[-1].append((num, len(content)//SECTION_SIZE))
            listing += byte_value(0x8+len(ext), 2)+bytes([i+1, 0xff])+byte_value(num, 2)+ext.encode(encoding="ascii")+bytes(2)
    if len(listing)%SECTION_SIZE!=0:
        listing += bytes(SECTION_SIZE-len(listing)%SECTION_SIZE)
    nb_sect_to_listing = nb_sect_header+len(borland)//SECTION_SIZE
    nb_sect_listing = len(listing)//SECTION_SIZE

    bytes_rsc += byte_value(nb_sect_to_listing, 2)+byte_value(nb_sect_listing, 2)+b'\x30\x1c\x01\x80'+bytes(4)
    off_sect = nb_sect_to_listing+nb_sect_listing
    for i, t in enumerate(lst_files):
        bytes_rsc += bytes([i+1, 0xff])+byte_value(len(t), 2)+bytes(4)
        for f in t:
            bytes_rsc += byte_value(off_sect, 2)+byte_value(f[1], 2)+b'\x30\x0c'+byte_value(f[0]|0x8000, 2)+bytes(4)
            off_sect += f[1]
    bytes_rsc += end_header
    if len(bytes_rsc)%SECTION_SIZE!=0:
        bytes_rsc += bytes(SECTION_SIZE-len(bytes_rsc)%SECTION_SIZE)
    bytes_rsc += borland
    bytes_rsc += listing
    bytes_rsc += data
    bytes_rsc += footer
    if not os.path.exists(out):
        os.makedirs(out, exist_ok=True)
    
    with open(out+os.path.sep+elt+".rsc", 'wb') as file:
        file.write(bytes_rsc)
        file.close()

def search_resources(path=".", out=None, verbose=False):
    if out==None:
        out = path
    lst = os.listdir(path)
    for elt in lst:
        if os.path.isdir(path+os.path.sep+elt):
            if os.path.exists(path+os.path.sep+elt+os.path.sep+"rsc.xml"):
                extract_resources(path, out, elt, verbose)
            else:
                search_resources(path+os.path.sep+elt, out+os.path.sep+elt, verbose)

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
        search_resources(arg[end_opt], arg[end_opt+1], verbose=verbose)
    else:
        search_resources(arg[end_opt], verbose=verbose)
else:
    print("Usage: "+arg[0]+" <options> from_path [output_dir]\n\nOptions: \n -v Verbose")
