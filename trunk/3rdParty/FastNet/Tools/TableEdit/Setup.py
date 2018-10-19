# -*- coding: utf-8 -*-
from PyInstaller.__main__ import run
# -F:打包成一个EXE文件 
# -w:不带console输出控制台，window窗体格式 
# --paths：依赖包路径 
# --icon：图标 
# --noupx：不用upx压缩 
# --clean：清理掉临时文件
import sys

sys.path.append('C:\\Python\\Python27\\site-packages\\PyQt5\\Qt')

if __name__ == '__main__':
    opts = ['-w', '--paths=C:\\Python\\Python27\\site-packages\\PyQt5\\Qt\\plugins',
            '--noupx', '--clean','--add-binary=C:\Python\Python27\Lib\site-packages\PyQt5\sip.pyd;./','--name=TableEdit',
            'App.py']

    run(opts)