from xml.sax import *
import io
import re
import zipfile
import shutil
import os
import sys

#sys.argv =[sys.argv[0],'./moshikou.kml']

#source_name = "./moshikou.kml"
#source_name = "./waypoints.kmz"
source_name = sys.argv[1]
data_file = "./GpsOffsetData.txt"
data_file_two = "./Mars2Wgs_converted.txt"
temp_dir = "./temp/kmz"

target_name = source_name[0:len(source_name)-4] + "_converted" + source_name[len(source_name)-4:]
# 控制加偏还是纠偏。这里纠偏采用data_file只是简单加改为减，不太准确。GE上测量与某纠偏软件相比向西北偏了7米
is_fix = True
# 控制使用第一份数据还是第二份数据 0 or 1
data_index = 1

class TransLatePosition:

    offset_file = open(data_file, encoding="utf8")
    data = offset_file.readline()
    print("Totoal size of data one:%d" % data.__sizeof__())

    @staticmethod
    def translate(old_lat, old_log):
        if type(old_lat) != float or type(old_log) != float:
            print("Parameter is not float")
            return
        
        pattern = re.compile("%.1f,%.1f[\d.,]+ " % (old_lat,old_log))
        data_array = pattern.findall(TransLatePosition.data)
        print(data_array)
        if len(data_array) == 1:
            data_found = data_array[0].strip()
            found_array = data_found.split(",")
            if len(found_array) >= 4:
                if is_fix:
                    new_lat = old_lat - float(found_array[2])
                    new_log = old_log - float(found_array[3])
                else:
                    new_lat = old_lat + float(found_array[2])
                    new_log = old_log + float(found_array[3])
                return new_lat, new_log
        else:
            print("More than one or none value found")
        return None, None


class TransLatePositionTwo:

    offset_file = open(data_file_two)
    data = offset_file.readline()
    print("Totoal size of data two:%d" % data.__sizeof__())

    @staticmethod
    def translate(old_lat, old_log):
        if type(old_lat) != float or type(old_log) != float:
            print("Parameter is not float")
            return
        
        pattern = re.compile("%d[\d]{4,4} %d[\d]{4,4}" % (int(old_lat*10),int(old_log*10)))
        data_array = pattern.findall(TransLatePositionTwo.data)
        if len(data_array) == 1:
            data_found = data_array[0].strip()
            found_array = data_found.split(" ")
            if len(found_array) >= 2:
                if is_fix:
                    new_lat = old_lat - float(found_array[0][-4:])/100000
                    new_log = old_log - float(found_array[1][-4:])/100000
                else:
                    new_lat = old_lat + float(found_array[0][-4:])/100000
                    new_log = old_log + float(found_array[1][-4:])/100000
                return new_lat, new_log
        else:
            print("More than one or none value found")
        return None, None

class OffsetHandler(ContentHandler):
    
    temp=""
    #coordinates = []
    file_writer = None
    level = 0
    #only contains \t \n and space
    all_sep_pattern = re.compile(r"^[\t\n ]+$")
    sep_pattern = re.compile(r"[\n\t ]+")

    def setFileWriter(self,filewriter):
        self.file_writer = filewriter

    def startDocument(self):
        self.file_writer.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        print("start xml document")

    def endDocument(self):
        print("end xml document")
    
    def startElement(self,name,attrs):
        toWrite = ""
        index = 0
        
        while index < self.level:
            toWrite += "\t"
            index += 1
            
        self.level += 1

        toWrite += "<" + name
        
        for name in attrs.getNames():
            toWrite += " " + name + "=\"" + attrs.getValue(name) + "\""

        toWrite += ">\n"
        
        self.file_writer.write(toWrite)
        self.temp=""

    def endElement(self,name):
        if name=="coordinates":
            splitArray = re.split(self.sep_pattern,self.temp)
            self.temp = ""
            
            index = 0
            while index < len(splitArray):
                if splitArray[index] != "" and splitArray[index] != "\n":
                    #self.coordinates.append(splitArray[index])
                    coordinateArray = splitArray[index].split(",")
                    if len(coordinateArray) > 2:
                        oldLat = float(coordinateArray[0])
                        oldLog = float(coordinateArray[1])
                        if data_index == 0:
                            lat,log = TransLatePosition.translate(oldLat, oldLog)
                        else:
                            lat,log = TransLatePositionTwo.translate(oldLat, oldLog)

                        if lat != None:
                            coordinateArray[0] = "%r" % lat
                        if log != None:
                            coordinateArray[1] = "%r" % log 
                        #print("Converted: %f %f" % (coordinateArray[0], coordinateArray[1]))
                        i = 0
                        temp = ""
                        while i < len(coordinateArray):
                            if temp != "":
                                temp += ","
                            temp += "%s" % coordinateArray[i]
                            i += 1
                        if self.temp != "":
                            self.temp += " "
                        self.temp += temp
                    
                index += 1
            
        index = 0
        tabs = ""

        while index < self.level-1:
            tabs += "\t"
            index += 1

        self.level -= 1

        if "<" in self.temp or "&" in self.temp:
            self.temp = "<![CDATA[" + self.temp + "]]>"
        if self.all_sep_pattern.match(self.temp):
            toWrite = ""
        else:
            toWrite = tabs + "\t" + self.temp + "\n"
            
        toWrite += tabs + "</" + name + ">\n"
        self.file_writer.write(toWrite)
        
        self.temp = ""

    def characters(self,content):
        self.temp+=content

    @staticmethod
    def parseFile(filename):
        print("===============start parse===============")
        parser = make_parser()
        handler = OffsetHandler()

        if not os.path.isfile(filename):
            print("%r is not a file"  % filename)
            return
        if filename[-3:] == "kml":
            with open(target_name, mode="w", encoding="utf8") as file_writer:
                handler.setFileWriter(file_writer)
                parser.setContentHandler(handler)
                data=""
                with open(source_name, encoding="utf8") as file:
                    data = file.read().strip()
                    file.close()
                parser.parse(io.StringIO(data))
                file_writer.close()
        elif filename[-3:] == "kmz":
            file_list = None
            with zipfile.ZipFile(filename) as kmz_zip:
                file_list = kmz_zip.namelist()
                kmz_zip.extractall(path=temp_dir)
                kmz_zip.close()

            with open(temp_dir + "/doc_converted.kml", mode="w", encoding="utf8") as file_writer:
                handler.setFileWriter(file_writer)
                parser.setContentHandler(handler)
                data=""
                with open(temp_dir + "/doc.kml", encoding="utf8") as file:
                    data = file.read().strip()
                    file.close()
                parser.parse(io.StringIO(data))
                file_writer.close()
            
            with zipfile.ZipFile(target_name, mode='w', compression=zipfile.ZIP_DEFLATED) as kmz_write:
                kmz_write.write(temp_dir + "/doc_converted.kml", "doc.kml")
                for contained_file in file_list:
                    if contained_file != "doc.kml":
                        kmz_write.write(temp_dir + "/" + contained_file, contained_file)
                
                kmz_write.close()
            
            shutil.rmtree(temp_dir)
        else:
            print("文件扩展名有误")
            return
        
        print("===============print result===============")
        print("结果输出到%s" % target_name);


OffsetHandler.parseFile(source_name)
