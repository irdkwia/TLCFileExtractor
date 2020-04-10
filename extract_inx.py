import os, shutil
import sys
def value(bytes_list):
    n = 0
    for i, b in enumerate(bytes_list):
        n += b * (256**i)
    return n

def extract_bul(data_inx, offsetStart, in_dir, out, verbose=False, leftovers=False):
    filename = ""
    off = offsetStart+0x6
    while data_inx[off]!=0x0:
        filename += chr(data_inx[off])
        off += 1
    off = value(data_inx[offsetStart+0x2:offsetStart+0x6])
    if verbose:
        print("Extracting from "+in_dir+os.path.sep+filename+".bul...")
    if filename!="":
        if not os.path.exists(out+os.path.sep+filename):
            os.makedirs(out+os.path.sep+filename, exist_ok=True)
        else:
            shutil.rmtree(out+os.path.sep+filename)
            os.mkdir(out+os.path.sep+filename)
    try:
        with open(in_dir+os.path.sep+filename+".bul", "rb") as file:
            data_bul = file.read()
            file.close()
    except:
        print("Can't extract from "+in_dir+os.path.sep+filename+".bul!")
        raise Exception("Can't extract from "+in_dir+os.path.sep+filename+".bul!")
    lst_lo = [(4,len(data_bul))]
    nb_pt = value(data_inx[off:off+4])
    off += 4
    for i in range(nb_pt):
        pt_addr = value(data_inx[off:off+4])
        start_data = value(data_inx[pt_addr+4:pt_addr+8])
        len_data = value(data_inx[pt_addr+8:pt_addr+12])
        x = 0
        while x<len(lst_lo):
            if lst_lo[x][0]<=start_data and lst_lo[x][1]>start_data:
                st_lo1 = lst_lo[x][0]
                ed_lo1 = start_data
                st_lo2 = start_data+len_data
                ed_lo2 = lst_lo[x][1]
                del lst_lo[x]
                if ed_lo2-st_lo2>0:
                    lst_lo.insert(x, (st_lo2, ed_lo2))
                if ed_lo1-st_lo1>0:
                    lst_lo.insert(x, (st_lo1, ed_lo1))
                break
            x+=1
        addr_data = start_data
        filename_data = ""
        while data_bul[addr_data]!=0x0:
            filename_data += chr(data_bul[addr_data])
            addr_data += 1
        if verbose:
            print("Extracting "+filename_data+"...")
        addr_data += 1
        with open(out+os.path.sep+filename+os.path.sep+filename_data, "wb") as file:
            file.write(data_bul[addr_data:start_data+len_data])
            file.close()
        off += 4
    if leftovers:
        if verbose:
            print("Extracting leftovers...")
        for i, x in enumerate(lst_lo):
            with open(out+os.path.sep+filename+"_"+str(i)+".bul", "wb") as file:
                file.write(data_bul[x[0]:x[1]])
                file.close()
    
def extract_inx(filename, out=None, verbose=False, leftovers=False):
    in_dir = os.path.dirname(filename)
    if in_dir=='':
        in_dir = '.'
    if out==None:
        out = os.path.dirname(filename)
        if out=='':
            out = '.'
    with open(filename, "rb") as file:
        data = file.read()
        file.close()
    nb_pt = value(data[0:4])
    for i in range(nb_pt):
        if i==0:
            continue
        try:
            extract_bul(data, value(data[4+i*4:8+i*4]), in_dir, out, verbose=verbose, leftovers=leftovers)
        except:pass

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
    if "-L" in lst_opts:
        leftovers = True
    if len(arg)-end_opt>=2:
        extract_inx(arg[end_opt], arg[end_opt+1], verbose=verbose, leftovers=leftovers)
    else:
        extract_inx(arg[end_opt], verbose=verbose, leftovers=leftovers)
else:
    print("Usage: "+arg[0]+" <options> inx_file [output_dir]\n\nOptions: \n -v Verbose\n -L Extract leftovers in .bul files")
