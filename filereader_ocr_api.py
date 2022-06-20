# -*- encoding: utf-8 -*-
'''
@File    :   filereader_ocr_api.py
@Time    :   2022/06/14 16:29:19
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
    def __init__(self, server_ip, tasktype, recog_name, scene_name, input_folder, save_folder, output_fileType) -> None:
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
        self.tasktype = tasktype
        self.recog_name = recog_name
        self.scene_name = scene_name
        self.input_folder = input_folder
        self.save_folder = save_folder
        self.output_fileType = output_fileType

        # http://222.74.8.218:50014/service/
        self.upload_file = 'http://' + self.server_ip + '/service' + '/submitTask'
        self.inquire_res = 'http://' + self.server_ip + '/service' + '/getResult'
        self.download_file = 'http://' + self.server_ip + '/service' + '/getResultFile'
        self.result_detail = 'http://' + self.server_ip + '/service' + '/getResultDetail'

        # result
        self.ocr_result = ''

    def readFileAsync_ocr(self):
        """
        上传图片
        """
        data = {
            'taskType': self.tasktype, 
            'uri': f'/lab/ocr/predict/{self.recog_name}', 
            'scene': f'{self.scene_name}', 
            'parameters': {'vis_flag': False, 'sdk': True, 'rotateupright': False}
            }
        file = {'file': (os.path.split(self.input_folder)[-1], open(self.input_folder, 'rb'))}
        result = post(url=self.upload_file, data=data, files=file).json()
        self.taskNo = result['data'] if result['code'] == 200 else None
        self.ocr_result = result
        print(f"IMG文件上传成功:【{os.path.split(self.input_folder)[-1]}】，任务编号为：【{self.taskNo}】")

    
    def readFileAsync_filereader(self):
        """
        上传PDF任务，获取任务编号
        """
        data = {'taskType': self.tasktype}
        file = {'file': (os.path.split(self.input_folder)[-1], open(self.input_folder, 'rb'))}
        result = post(url=self.upload_file, data=data, files=file).json()
        self.taskNo = result['data'] if result['code'] == 200 else None
        print(f"PDF文件上传成功:【{os.path.split(self.input_folder)[-1]}】，任务编号为：【{self.taskNo}】")


    def getResult(self):
        """
        查询任务结果
        """
        data = {
            'taskNo': self.taskNo, 
            'totalSubTask': self.totalSubTask, 
            'processSubTask': self.processSubTask, 
            'doneSubTask': self.doneSubTask
            }
        # print('*' * 100)
        # print('*' * 47 + '开始查询' + '*' * 47)
        if self.tasktype == 1:
            num = 3
            while True:
                result = get(url=self.inquire_res, params=data).json()
                totalSubTask = result['data']['totalSubTask']
                processSubTask = result['data']['processSubTask']
                doneSubTask = result['data']['doneSubTask']
                if totalSubTask == 1 and processSubTask == 0 and doneSubTask == 0:
                    if not num: break
                    num = num - 1
                state = result['data']['state']
                # print(state)
                if state == 30: break
                time.sleep(2)
        if self.tasktype == 100:
            # data = {
            # 'taskNo': self.taskNo
            # }
            while True:
                result = get(url=self.inquire_res, params=data).json()
                state = result['data']['state']
                if state == 30: break

    
    def getResultDetail(self):
        """
        查询结果，返回json格式
        """
        # print("——————————————————获取对应的结果————————————————")
        data = {'taskNo': self.taskNo}
        result = get(url=self.result_detail, params=data).json()
        # print(f"任务号taskNo：【{self.taskNo}】")
        print(result)


    def getResultFile(self):
        """
        查询结果，下载：双层PDF 0 / TXT 1  默认0
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
            # print(os.path.splitext(os.path.split(self.input_folder)[-1])[0])
            with open(f'{self.save_folder}' + '\\' + f'{os.path.splitext(os.path.split(self.input_folder)[-1])[0]}' + '.txt', 'w', encoding='UTF-8') as f:
                f.write(self.result_value)


    @calculate_time
    def main_process(self):
        fileReader = FileReader_API(
            server_ip=self.server_ip, 
            tasktype=self.tasktype,
            recog_name=self.recog_name,
            scene_name=self.scene_name,
            input_folder=self.input_folder, 
            save_folder=self.save_folder, 
            output_fileType=self.output_fileType)
        if self.tasktype == 100:
            fileReader.readFileAsync_ocr()
            fileReader.getResult()
            fileReader.getResultDetail()
        elif self.tasktype == 1:
            fileReader.readFileAsync_filereader()
            fileReader.getResult()
            fileReader.getResultFile()
            fileReader.toFile()
        else:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='The script transfer FileReader to image or pdf recognition')
    parser.add_argument('-sp', '--server_ip', help='Server Ip path (only server ip', type=str, default='')
    parser.add_argument('-t', '--tasktype', help='Which way you want, Input taskType 1 or 100?', type=int, default=0)
    parser.add_argument('-rm', '--recog_name', help='Which way you want, Input recog_name general or ticket?', type=str, default='')
    parser.add_argument('-sn', '--scene_name', help='Which way you want, Input scene_name, such as:idcard, spinvoice, dianhuipingzheng...?', type=str, default='')
    parser.add_argument('-i', '--input_folder', help='Input folder path (only folder)', type=str, default='')
    parser.add_argument('-s', '--save_folder', help='Save folder path (only folder)', type=str, default='')
    parser.add_argument('-of', '--output_fileType', help='Which way you want, OutPut FileType PDF or TXT: 0 or 1?', type=int, default=0)
    args = parser.parse_args()

    print('----------------- Start the process -----------------')
    start = time.perf_counter()

    dirs = os.listdir(args.input_folder)
    for i in dirs:
        file = args.input_folder + '\\' + i
        FileReader_API(args.server_ip, args.tasktype, args.recog_name, args.scene_name, file, args.save_folder, args.output_fileType).main_process()

    stop = time.perf_counter() - start
    final_show = electronic_clock(stop)
    hour, minute, second = final_show[0], final_show[1], final_show[2]
    print('Time consumption of PDF to Image is 「 %02d : %02d : %02d 」' % (hour, minute, second))
    print('-------------- All process is complete --------------')