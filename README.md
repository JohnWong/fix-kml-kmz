fix-kml-kmz
===========

众所周知，Google Maps与Google Earth在中国坐标存在一定的“误差”。本程序用于修正kml与kmz格式文件，将其从Google Maps坐标转换为Google Earth坐标。

OffsetXml.py用于纠偏。使用方式为:切换到其所在目录后执行

``` shell
python OffsetXml.py D:\py\moshikou.kml
```

在输入的kml文件所在目录生成moshikou_converted.kml。若存在该名称文件，则直接覆盖。kmz文件命令类似。

InitData.py用于数据格式转换，将Mars2Wgs.txt转换为Mars2Wgs_converted.txt。如果已存在Mars2Wgs_converted.txt则不需要再执行。

新增windows下可执行程序，只需在命令行下输入OffsetXml.exe D:\py\moshikou.kml即可
