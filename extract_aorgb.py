import os, shutil
from PIL import Image
import sys

def value(bytes_list):
    n = 0
    for i, b in enumerate(bytes_list):
        n += b * (256**i)
    return n

def get_palette(data):
    l_color = []
    for i in range(len(data)//6):
        l_color.append(bytes([data[i*6], data[i*6+2], data[i*6+4], 255]))
    return l_color

def decompress(data, maxlen = None):
    data_dec = b''
    off = 0
    zeros = 0
    while off<len(data) and (maxlen!=None and len(data_dec)<maxlen+zeros):
        if data[off]==0:
            data_dec += bytes(data[off+1]*2)
            zeros += data[off+1]
            off += 1
        elif data[off]==255:
            tmp = bytes([data[off+1]]*data[off+2]).replace(b"\x00", b"\x00\xFF")
            zeros += tmp.count(b"\x00\xFF")
            data_dec += tmp
            off += 2
        else:
            tmp = data[off+1:off+1+data[off]].replace(b"\x00", b"\x00\xFF")
            zeros += tmp.count(b"\x00\xFF")
            data_dec += tmp
            off += data[off]
        off += 1
    return data_dec, off

def get_img(data, base, l_color):
    width = value(data[base+2:base+4])
    height = value(data[base+4:base+6])
    data_dec, length = decompress(data[base+6:], width*height)
    img = []
    i = 0
    nb = 0
    while i < len(data_dec):
        b = data_dec[i]
        if b!=0 or data_dec[i+1]==0xff:
            img.append(l_color[b])
        elif b==0:
            img.append(b'\x00\x00\x00\x00')
        if b==0:
            i += 1
        i += 1
        nb += 1
    return Image.frombytes(mode='RGBA', size=(width,height),data=b''.join(img), decoder_name='raw'), length+6

def extract_ao(filename, output):
    print("Extracting from "+filename+"...")
    try:
        with open(filename+".rgb", "rb") as file:
            l_color = get_palette(file.read())
            file.close()
        with open(filename+".ao", "rb") as file:
            data = file.read()
            file.close()
    except:
        print("Missing .rgb file for "+filename+"!")
        raise Exception("Missing .rgb file for "+filename+"!")
    if not os.path.exists(output):
        os.makedirs(output, exist_ok=True)
    else:
        shutil.rmtree(output)
        os.mkdir(output)
    off = 0xe+value(data[0x2:0x4])*4
    off += 2+value(data[off:off+2])*8
    nb = 0
    for i in range(value(data[0x2:0x4])):
        if data[off]==0x4 and data[off+1]==0x0:
            img, length = get_img(data, off, l_color)
            off += length
            nb += 1
            img.save(output+os.path.sep+"nb"+str(nb)+".png", "PNG")
        else:
            raise Exception("Invalid start at "+hex(off))

def search_ao(path=".", out=None):
    if out==None:
        out = path
    lst = os.listdir(path)
    for elt in lst:
        if elt.split(".")[-1]=="ao":
            try:
                extract_ao(path+os.path.sep+elt[:-3], out+os.path.sep+elt[:-3])
            except:pass
        elif os.path.isdir(path+os.path.sep+elt):
            search_ao(path+os.path.sep+elt, out+os.path.sep+elt)

arg = sys.argv
if len(arg)>=2:
    if len(arg)>=3:
        search_ao(arg[1], arg[2])
    else:
        search_ao(arg[1])
else:
    print("Usage: "+arg[0]+" from_path [output_dir]")
