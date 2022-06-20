# -*- encoding: utf-8 -*-
'''
@File    :   ocr_api.py
@Time    :   2022/06/13 13:38:02
@Author  :   Fighter.Ma
@Email   :   fighter_ma1024@163.com
@Software:   VsCode
@License :   (C)Copyright 2021-2022, Fighter-Ma-China
'''

# here put the import lib
import os
import base64
import json
import time
import argparse
from requests import post
from tools.showTime import calculate_time
from tools.showTime import electronic_clock


class Ocr_API():
    def __init__(self, server_ip, input_folder, save_folder, scene_name, model_type) -> None:
        self.server_ip = server_ip
        self.input_folder = input_folder
        self.save_folder = save_folder
        self.scene_name = scene_name
        self.model_type = model_type

        self.element_name = ''
        self.element_value = ''
    
    def general(self):
        url = f'{self.server_ip}/lab/ocr/predict/general'
        b64 = base64.b64encode(open(self.input_folder, 'rb').read()).decode()
        data = {'scene': self.scene_name, 'image': b64,
                'parameters': {'vis_flag': False, 'sdk': True}}
        res = post(url, json=data).json()
        print(res)


    def ticket(self):
        url = f'{self.server_ip}/lab/ocr/predict/ticket'
        b64 = base64.b64encode(open(self.input_folder, 'rb').read()).decode()
        data = {'scene': self.scene_name, 'image': b64,
                'parameters': {'vis_flag': False, 'sdk': True}}
        res = post(url, json=data).json()
        result = res["data"]["result"][0]["data"]
        imgName = self.input_folder.split("\\")[-1].split(".")[0]
        for re in result:
            element_name = re["element_name"]
            element_value = re["element_value"]
            # self.element_name = re["element_name"]
            # self.element_value = re["element_value"]
            res_txt = str(element_name) + ":" + str(element_value)
            self.to_txt(imgName, res_txt)
            # self.to_txt(imgName)


    def to_txt(self, imgName):
        # resultJons = {
        #     "text": { 
        #         "element_name": self.element_name,
        #         "element_value": self.element_value
        #     }
        # }
        with open(f"{self.save_folder}/{imgName}.txt", "a+", encoding="UTF-8") as f:
            # json.dump(resultJons, f, indent=4, ensure_ascii=False)
            f.write(res_txt)
            f.write("\n")


    @calculate_time
    def main_process(self):
        ocrApi = Ocr_API(
            server_ip=self.server_ip, 
            input_folder=self.input_folder, 
            save_folder=self.save_folder, 
            scene_name=self.scene_name, 
            model_type=self.model_type)
        if self.model_type == "0":
            ocrApi.general()
        elif self.model_type == "1":
            ocrApi.ticket()
        else:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='The script transfer FileReader to image or pdf recognition')
    parser.add_argument('-sp', '--server_ip', help='Server Ip path (only server ip)', type=str, default='')
    parser.add_argument('-i', '--input_folder', help='Input folder path (only folder)', type=str, default='')
    parser.add_argument('-s', '--save_folder', help='Save folder path (only folder)', type=str, default='')
    parser.add_argument('-sn', '--scene_name', help='Input model name', type=str, default='')
    parser.add_argument('-mt', '--model_type', help='Which way you want general or ticket, model_type 0 or 1?', type=str, default='1')
    args = parser.parse_args()

    print('----------------- Start the process -----------------')
    start = time.perf_counter()

    dirs = os.listdir(args.input_folder)
    for i in dirs:
        file = args.input_folder + '\\' + i
        Ocr_API(args.server_ip, file, args.save_folder, args.scene_name, args.model_type).main_process()

    stop = time.perf_counter() - start
    final_show = electronic_clock(stop)
    hour, minute, second = final_show[0], final_show[1], final_show[2]
    print('Time consumption of PDF to Image is 「 %02d : %02d : %02d 」' % (hour, minute, second))
    print('-------------- All process is complete --------------')