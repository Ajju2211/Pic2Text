import shutil
import os
import subprocess


'''
Building Executables
'''
print('Started build...')

build = subprocess.Popen(["pyinstaller", "--onefile", "--windowed", "--icon=logo.ico", "Pic2Text.py"],
                        stdin =subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True,
                        bufsize=0)
 
# Send OP
build.stdin.write("uname -a\n")
build.stdin.write("uptime\n")
build.stdin.close()

# Fetch output
for line in build.stdout:
    print(line.strip())

print("Completed build !!!")

FOLDERS = ['ui','ICONS','Tesseract-OCR']
'''
Copying files to dist
'''
print('Started copying files to dist...')
try:
    for folder in FOLDERS:
        if os.path.isdir('dist/'+folder):
            shutil.rmtree('dist/'+folder)
            print('Removed dist/{}'.format(folder))
        shutil.copytree(folder,'dist/'+folder)
        print('Copied {} to "dist"'.format(folder))
    print('Completed Files copying !!!')
except Exception as e:
    print('Error while copying files to dist')




