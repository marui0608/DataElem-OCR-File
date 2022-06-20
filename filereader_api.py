# -*- encoding: utf-8 -*-
'''
@File    :   filereader_api.py
@Time    :   2022/06/10 09:31:06
@Author  :   Fighter.Ma
@Email   :   fighter_ma1024@163.com
@Software:   VsCode
@License :   (C)Copyright 2021-2022, Fighter-Ma-China
'''

# here put the import lib
import os
import time
import argparse
from requests import post, get
from tools.fileBase64 import b64_file
from tools.showTime import calculate_time
from tools.showTime import electronic_clock


class FileReader_API:
    def __init__(self, server_ip, input_folder, save_folder, output_fileType) -> None:
        """
        server: FileReader 服务器地址
        port:   服务器端口
        files:  待上传PDF文件
        """
        self.taskNo = ''
        self.totalSubTask = ''
        self.processSubTask = ''
        self.doneSubTask = ''
        self.result_value = ''

        self.server_ip = server_ip
        self.input_folder = input_folder
        self.save_folder = save_folder
        self.output_fileType = output_fileType

        # http://222.74.8.218:50014/service/
        self.upload_file = 'http://' + self.server_ip + '/service' + '/readFileAsync'
        self.inquire_res = 'http://' + self.server_ip + '/service' + '/getResult'
        self.download_file = 'http://' + self.server_ip + '/service' + '/getResultFile'

    def readFileAsync(self):
        """
        上传PDF任务，获取任务编号
        """
        # print(f"-----开始上传PDF文件-----\n【{self.input_folder}】")
        # with open(self.input_folder, 'rb') as f:
        #     data = {'file': (f.read())}
        data = {'file': (os.path.split(self.input_folder)[-1], open(self.input_folder, 'rb'))}
        result = post(url=self.upload_file, files=data).json()
        self.taskNo = result['data'] if result['code'] == 200 else None
        print(f"PDF文件上传成功:【{os.path.split(self.input_folder)[-1]}】，任务编号为：【{self.taskNo}】")


    def getResult(self):
        """
        查询任务结果
        """
        # print('*' * 100)
        # print('*' * 47 + '开始查询' + '*' * 47)
        data = {
            'taskNo': self.taskNo, 
            'totalSubTask': self.totalSubTask, 
            'processSubTask': self.processSubTask, 
            'doneSubTask': self.doneSubTask
            }
        num = 3
        while True:
            result = get(url=self.inquire_res, params=data).json()
            totalSubTask = result['data']['totalSubTask']
            processSubTask = result['data']['processSubTask']
            doneSubTask = result['data']['doneSubTask']
            if totalSubTask == 1 and processSubTask == 0 and doneSubTask == 0:
                print(num)
                if not num: break
                num = num - 1
            state = result['data']['state']
            # print(state)
            if state == 30: break
            time.sleep(2)
    

    def getResultFile(self):
        """
        下载结果：双层PDF 0 / TXT 1  默认0
        """
        # print("——————————————————获取对应的结果————————————————")
        data = {'name': self.taskNo, 'fileType': self.output_fileType}
        result = get(url=self.download_file, params=data)
        # print(f"任务号taskNo：【{self.taskNo}】")
        if self.output_fileType == 0: self.result_value = result.content
        if self.output_fileType == 1: self.result_value = result.text


    def toFile(self):
        """"
        将字节流 / 文本 写入对应的PDF文件、TXT文件
        """
        if self.output_fileType == 0:
            with open(f'{self.save_folder}' + '\\' + f'{os.path.splitext(os.path.split(self.input_folder)[-1])[0]}' + '.pdf', 'wb') as f:
                f.write(self.result_value)
        if self.output_fileType == 1:
            with open(f'{self.save_folder}' + '\\' + f'{os.path.splitext(os.path.split(self.input_folder)[-1])[0]}' + '.txt', 'w', encoding='UTF-8') as f:
                f.write(self.result_value)


    @calculate_time
    def main_process(self):
        fileReader = FileReader_API(
            server_ip=self.server_ip, 
            input_folder=self.input_folder, 
            save_folder=self.save_folder, 
            output_fileType=self.output_fileType)
        fileReader.readFileAsync()
        fileReader.getResult()
        fileReader.getResultFile()
        fileReader.toFile()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='The script transfer FileReader to image or pdf recognition')
    parser.add_argument('-sp', '--server_ip', help='Server Ip path (only server ip)', type=str, default='')
    parser.add_argument('-i', '--input_folder', help='Input folder path (only folder)', type=str, default='')
    parser.add_argument('-s', '--save_folder', help='Save folder path (only folder)', type=str, default='')
    parser.add_argument('-of', '--output_fileType', help='Which way you want, OutPut FileType 0 or 1?', type=int, default=1)
    args = parser.parse_args()

    print('----------------- Start the process -----------------')
    start = time.perf_counter()

    dirs = os.listdir(args.input_folder)
    for i in dirs:
        file = args.input_folder + '\\' + i
        FileReader_API(args.server_ip, file, args.save_folder, args.output_fileType).main_process()

    stop = time.perf_counter() - start
    final_show = electronic_clock(stop)
    hour, minute, second = final_show[0], final_show[1], final_show[2]
    print('Time consumption of PDF to Image is 「 %02d : %02d : %02d 」' % (hour, minute, second))
    print('-------------- All process is complete --------------')