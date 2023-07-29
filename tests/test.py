import os
import subprocess 

rsyncCMD = 'rsync -avzh --progress --recursive idg@172.16.1.127:/home/idg/pics/06-02-2023/raw-00000009.fits /Users/aidancgray/src/cam-pics/06-02-2023/'
rsyncPWD = '3701sanmartin'

#os.system(f"echo 3701sanmartin | echo hello!")
#os.system(f"echo 3701sanmartin | {rsyncCMD}")
#os.system(f"{rsyncCMD} ; echo 3701sanmartin")

#os.system('3701sanmartin')

# p = subprocess.Popen(["python", "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
# output, errors = p.communicate()
# print(output)

p = subprocess.Popen(["rsync", "-avzh", "--progress", "--recursive", "idg@172.16.1.127:/home/idg/pics/06-02-2023/raw-00000009.fits", "/Users/aidancgray/src/cam-pics/06-02-2023/"],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
#p.stdin.write(b"3701sanmartin\n")
resultp = p.stdout.read()
print("p:")
print(resultp)

print('##############')

q = subprocess.Popen(["rsync -avzh --progress --recursive idg@172.16.1.127:/home/idg/pics/06-02-2023/raw-00000009.fits /Users/aidancgray/src/cam-pics/06-02-2023/"],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
q.stdin.write(b"3701sanmartin\n")
resultq = q.stdout.read()
print("q:")
print(resultq)
