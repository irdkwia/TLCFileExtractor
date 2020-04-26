import os, shutil
from PIL import Image
import sys

VERSION = "3.2"

def value(bytes_list, signed = False):
    n = 0
    for i, b in enumerate(bytes_list):
        n += b * (256**i)
    if signed and n>=(256**len(bytes_list))//2:
        return n-(256**len(bytes_list))
    else:
        return n

def get_palette(data):
    l_color = []
    for i in range(len(data)//6):
        l_color.append(bytes([data[i*6], data[i*6+2], data[i*6+4], 255]))
    return l_color

def create_img(data_dec, width, height, l_color):
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
    return Image.frombytes(mode='RGBA', size=(width,height),data=b''.join(img), decoder_name='raw')

def decompress(data, maxlen = None):
    data_dec = b''
    off = 0
    zeros = 0
    #print("Data:")
    while off<len(data) and (maxlen==None or len(data_dec)<maxlen+zeros):
        if data[off]==0:
            data_dec += bytes(data[off+1]*2)
            zeros += data[off+1]
            #print("Style 00:", data[off+1])
            off += 1
        elif data[off]==255:
            tmp = bytes([data[off+1]]*data[off+2]).replace(b"\x00", b"\x00\xFF")
            zeros += tmp.count(b"\x00\xFF")
            data_dec += tmp
            #print("Style FF:", data[off+2])
            off += 2
        else:
            tmp = data[off+1:off+1+data[off]].replace(b"\x00", b"\x00\xFF")
            zeros += tmp.count(b"\x00\xFF")
            data_dec += tmp
            #print("Normal Style:", data[off])
            off += data[off]
        off += 1
    return data_dec

def get_img(data, base, l_color):
    width = value(data[base+2:base+4])
    height = value(data[base+4:base+6])
    data_dec = decompress(data[base+6:], width*height)
    return create_img(data_dec, width, height, l_color)

def decompress_m2(data, maxlen = None):
    data_dec = b''
    off = 0
    while off<len(data) and (maxlen==None or len(data_dec)<maxlen*4):
        style = value(data[off:off+2])
        count = value(data[off+2:off+4])
        off += 4
        if style==0:
            data_dec += bytes(count*4)
        elif style==1:
            for x in range(count):
                val = value(data[off:off+2])
                b = val%32
                g = (val>>6)%32
                r = (val>>11)%32
                data_dec += bytes([r*8, g*8, b*8, 255])
                off+=2
        elif style==2:
            for x in range(count):
                val = value(data[off:off+2])
                b = val%32
                g = (val>>6)%32
                r = (val>>11)%32
                data_dec += bytes([r*8, g*8, b*8, data[off+2]])
                off+=3
        else:
            raise Exception("Unsupported style", style, "offset", off)
    return data_dec

def get_img_m2(data, base):
    width = value(data[base+2:base+4])
    height = value(data[base+4:base+8])
    data_dec = b''
    for i in range(height):
        data_dec += decompress_m2(data[base+value(data[base+8+i*4:base+8+(i+1)*4]):], width)
    return Image.frombytes(mode='RGBA', size=(width,height),data=data_dec, decoder_name='raw')
def extract_ao(filename, output, verbose=False):
    if verbose:
        print("Extracting from "+filename+"...")
    with open(filename+".ao", "rb") as file:
        data = file.read()
        file.close()
    if not os.path.exists(output):
        os.makedirs(output, exist_ok=True)
    else:
        shutil.rmtree(output)
        os.mkdir(output)
    str_xml = "<obj>\n"
    str_xml += "\t<version>"+VERSION+"</version> <!-- Version of the extractor -->\n"
    str_xml += "\t<header>\n"
    str_xml += "\t\t<speed>"+str(value(data[0x4:0x6]))+"</speed>\n"
    str_xml += "\t\t<unknown1>"+str(value(data[0x6:0x8]))+"</unknown1>\n"
    mode = value(data[0x8:0xa])
    if mode==1:
        try:
            with open(filename+".rgb", "rb") as file:
                l_color = get_palette(file.read())
                file.close()
        except:
            print("Missing .rgb file for "+filename+"!")
            raise Exception("Missing .rgb file for "+filename+"!")
    str_xml += "\t\t<mode>"+str(mode)+"</mode>\n"
    str_xml += "\t</header>\n"
    off = 0xa+value(data[0x2:0x4])*4
    str_xml += "\t<header2>\n"
    str_xml += "\t\t<unknown1>"+str(value(data[off:off+2]))+"</unknown1>\n"
    str_xml += "\t\t<unknown2>"+str(value(data[off+2:off+4]))+"</unknown2>\n"
    str_xml += "\t</header2>\n"
    off += 4
    str_xml += "\t<animation>\n"
    for i in range(value(data[off:off+2])):
        str_xml += "\t\t<part>\n"
        str_xml += "\t\t\t<xpos>"+str(value(data[off+2+i*8:off+2+i*8+2], signed=True))+"</xpos>\n"
        str_xml += "\t\t\t<ypos>"+str(value(data[off+2+i*8+2:off+2+i*8+4], signed=True))+"</ypos>\n"
        img = value(data[off+2+i*8+4:off+2+i*8+6], signed=True)
        if img>=0:
            img+=1
        str_xml += "\t\t\t<img>"+str(img)+"</img>\n"
        str_xml += "\t\t\t<other>"+str(value(data[off+2+i*8+6:off+2+i*8+8], signed=True))+"</other>\n"
        str_xml += "\t\t</part>\n"
    str_xml += "\t</animation>\n"
    str_xml += "</obj>"
    off += 2+value(data[off:off+2])*8
    nb = 0
    for i in range(value(data[0x2:0x4])):
        if mode==1:
            img = get_img(data, off+value(data[0xa+i*4:0xa+i*4+4]), l_color)
            nb += 1
            img.save(output+os.path.sep+"nb"+str(nb)+".png", "PNG")
        elif mode==2:
            img = get_img_m2(data, off+value(data[0xa+i*4:0xa+i*4+4]))
            nb += 1
            img.save(output+os.path.sep+"nb"+str(nb)+".png", "PNG")
        else:
            raise Exception("Unsupported mode", mode)
    with open(output+os.path.sep+"anim.xml", "w") as file:
        file.write(str_xml)
        file.close()

def search_ao(path=".", out=None, verbose=False):
    if out==None:
        out = path
    lst = os.listdir(path)
    for elt in lst:
        if elt.split(".")[-1]=="ao":
            try:
                extract_ao(path+os.path.sep+elt[:-3], out+os.path.sep+elt[:-3], verbose)
            except:pass
        elif os.path.isdir(path+os.path.sep+elt):
            search_ao(path+os.path.sep+elt, out+os.path.sep+elt, verbose)

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
    leftovers = False
    if len(arg)-end_opt>=2:
        search_ao(arg[end_opt], arg[end_opt+1], verbose=verbose)
    else:
        search_ao(arg[end_opt], verbose=verbose)
else:
    print("Usage: "+arg[0]+" <options> from_path [output_dir]\n\nOptions: \n -v Verbose")
