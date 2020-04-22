def byte_value(value, nums = 4):
    if value<0:
        value += 256**nums
    lst_b = []
    for i in range(nums):
        lst_b.append(value%256)
        value//=256
    return bytes(lst_b)

def value(bytes_list, signed = False):
    n = 0
    for i, b in enumerate(bytes_list):
        n += b * (256**i)
    if signed and n>=(256**len(bytes_list))//2:
        return n-(256**len(bytes_list))
    else:
        return n
