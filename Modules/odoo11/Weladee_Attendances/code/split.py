#!/usr/bin/env python3
# -*- coding: utf-8 -*-





def main():
    path = '/home/cka/Documents/go/src/frontware.com/weladee/odoo/Modules/odoo11/Weladee_Attendances/code/test.txt'
    new_data = ""
    with open(path, 'r') as myfile:
        data = myfile.read().replace('\n', '')
        list = data.split("UPDATE")
        duplicate_name = []
        has_duplicate_name = []
        for r in list :
            origindata = "UPDATE" + r
            s1 = origindata.split(") = (")
            if len(s1) > 1 :
                s2 = s1[1].split(",")[0]
                id = s2
                code = s1[1].split(",")[1]
                udata = origindata.replace("id=","id="+id)
                s3 = s1[1].split(",")[2]
                fullname = s3.split("'")[1]
                sfullname = fullname.split(" ")
                if len(sfullname) == 2 :
                    if not fullname in duplicate_name :
                        udata = "UPDATE employee SET (id,code,first_name_thai, last_name_thai) = (" 
                        udata += id + ", " + code + ", '" + sfullname[1].strip() + "', '" + sfullname[0].strip() + "') WHERE id=" + id + " ;"
                        duplicate_name.append( fullname )
                        print(udata)
                    else:
                        has_duplicate_name.append(id + " : " + fullname)
                new_data += udata+"\n"

        print( has_duplicate_name )
        #f = open("new.txt","w+")
        f = open("ex_new.txt","w+")
        f.write( new_data )

if __name__ == "__main__":
    import sys
    import os
    import glob

    # if --optimize then restart application with -O parameter.
    if '--optimize' in sys.argv:
        sys.argv.remove('--optimize')
        os.execl(sys.executable, sys.executable, '-O', *sys.argv)
    else:
        main()