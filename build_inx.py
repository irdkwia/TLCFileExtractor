import os, shutil
import sys
import time
from common.tools import *

def build_section(section, offsetStart):
    header = byte_value(len(section))
    data = b''
    offsetAdd = (len(section)+1)*4
    for s in section:
        header += byte_value(offsetStart+offsetAdd)
        data += s
        offsetAdd+=len(s)
    return header+data

def build_bul(index, timecode, arch_name, in_dir, out, verbose=False):
    if verbose:
        print("Creating "+arch_name+".bul...")
    header_lst = []
    data_bul = byte_value(timecode)
    for ent in sorted(os.listdir(in_dir+os.path.sep+arch_name), key=lambda x:x.lower()):
        if not os.path.isdir(in_dir+os.path.sep+arch_name+os.path.sep+ent):
            data_ent = ent.encode(encoding='ascii')+b'\x00'
            if verbose:
                print("Opening "+ent+"...")
            with open(in_dir+os.path.sep+arch_name+os.path.sep+ent, 'rb') as file:
                data_ent += file.read()
                file.close()
            if verbose:
                print("Opening "+ent+"...")
            entry = b'\x80\x00'+byte_value(index, 2)
            entry += byte_value(len(data_bul))+byte_value(len(data_ent))+bytes(6)
            entry += ent.encode(encoding='ascii')+b'\x00'
            data_bul += data_ent
            header_lst.append(entry)
    with open(out+os.path.sep+arch_name+'.bul', 'wb') as file:
        file.write(data_bul)
        file.close()
    return header_lst

def build_inx(in_dir=".", out=None, verbose=False):
    if out==None:
        out = in_dir
    lst_arch = []
    for ent in sorted(os.listdir(in_dir), key=lambda x:x.lower()):
        if os.path.isdir(in_dir+os.path.sep+ent):
            lst_arch.append(ent)
    offsetStart = (len(lst_arch)+2)*4

    sections_lst = []

    section_name = b'*bulkFiles'
    offsetAdd = 0x6+len(section_name)+1
    header_section = b'\x00\x04'+byte_value(offsetStart+offsetAdd)+section_name+b'\x00'
    header_lst = []
    timecode_root = int(time.time())
    for i, arch in enumerate(lst_arch):
        timecode = timecode_root+i
        entry = b'\x80\x00'+byte_value(i, 2)+byte_value(timecode)+bytes(10)
        entry += arch.encode(encoding='ascii')+b'.bul\x00'
        header_lst.append(entry)
    header_section += build_section(header_lst, offsetStart+offsetAdd)
    sections_lst.append(header_section)
    offsetStart += len(header_section)

    for i, arch in enumerate(lst_arch):
        section_name = arch.encode(encoding='ascii')
        offsetAdd = 0x6+len(section_name)+1
        header_section = b'\x00\x04'+byte_value(offsetStart+offsetAdd)+section_name+b'\x00'
        header_lst = build_bul(i, timecode_root+i, arch, in_dir, out, verbose)
        header_section += build_section(header_lst, offsetStart+offsetAdd)
        sections_lst.append(header_section)
        offsetStart += len(header_section)
    
    if verbose:
        print("Creating root.inx...")
    data_inx = build_section(sections_lst, 0)
    with open(out+os.path.sep+'root.inx', 'wb') as file:
        file.write(data_inx)
    
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
        build_inx(arg[end_opt], arg[end_opt+1], verbose=verbose)
    else:
        build_inx(arg[end_opt], verbose=verbose)
else:
    print("Usage: "+arg[0]+" <options> from_path [output_dir]\n\nOptions: \n -v Verbose")
