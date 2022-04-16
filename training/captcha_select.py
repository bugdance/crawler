# -*- coding: utf-8 -*-
# =============================================================================
# Copyright (c) 2018-, pyLeo Developer. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================
import numpy as np
from PIL import Image
import os
import random
import io



class CaptchaSelect:
    
    def __init__(self):
        # self.number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.number = ['2', '3', '4', '5', '6', '7', '8', '9']
        self.low_case = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z']
        # self.up_case = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
        #    'V', 'W', 'X', 'Y', 'Z']
        self.up_case = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U',
                        'V', 'W', 'X', 'Y', 'Z']
        self.captcha_list = self.number + self.up_case
        self.captcha_len = 4
        self.captcha_height = 40
        self.captcha_width = 60
        self.train_path = '../test2/'  # 图片文件夹
        self.test_path = '../test4/'

    def random_captcha_text(self):
        """
        随机生成定长字符串
        :param char_set: 备选字符串列表 CAPTCHA_LIST
        :param captcha_size: 字符串长度 CAPTCHA_LEN
        :return: 字符串
        """
        char_set = self.captcha_list
        captcha_size = self.captcha_len
        captcha_text = [random.choice(char_set) for _ in range(captcha_size)]
        return ''.join(captcha_text)

    def gen_captcha_train_and_image(self):
        """
        生成随机验证码
        :param width: 验证码图片宽度
        :param height: 验证码图片高度
        :param save: 是否保存（None）
        :return: 验证码字符串，验证码图像np数组
        """
        names = []
        dirs = os.listdir(self.train_path)
        for dir in dirs:
            names.append(dir)

        p = random.choice(names)
        s = p.split("-")
        captcha_image = Image.open(self.train_path + p)
        # 转化为np数组
        captcha_image = np.array(captcha_image)
        return s[0][:4], captcha_image    # 这里要改

    def gen_captcha_test_and_image(self):
        """
        生成随机验证码
        :param width: 验证码图片宽度
        :param height: 验证码图片高度
        :param save: 是否保存（None）
        :return: 验证码字符串，验证码图像np数组
        """
        names = []
        dirs = os.listdir(self.test_path)
        for dir in dirs:
            names.append(dir)
        
        p = random.choice(names)
        s = p.split("-")
        captcha_image = Image.open(self.test_path + p)
        # 转化为np数组
        captcha_image = np.array(captcha_image)
        return s[0][:4], captcha_image    # 这里要改


    # transform
    def convert2gray(self, img):
        """
        图片转为黑白，3维转1维
        :param img: np
        :return:  灰度图的np
        """
        if len(img.shape) > 2:
            img = np.mean(img, -1)
        return img
    
    
    def text2vec(self, text):
        """
        验证码文本转为向量
        :param text:
        :param captcha_len: CAPTCHA_LEN
        :param captcha_list: CAPTCHA_LIST
        :return: vector 文本对应的向量形式
        """
        captcha_len = self.captcha_len
        captcha_list = self.captcha_list
        
        text_len = len(text)    # 欲生成验证码的字符长度
        if text_len > captcha_len:
            raise ValueError('验证码最长4个字符')
        vector = np.zeros(captcha_len * len(captcha_list))      # 生成一个一维向量 验证码长度*字符列表长度
        for i in range(text_len):
            vector[captcha_list.index(text[i])+i*len(captcha_list)] = 1     # 找到字符对应在字符列表中的下标值+字符列表长度*i 的 一维向量 赋值为 1
        return vector
    
    
    def vec2text(self, vec):
        """
        验证码向量转为文本
        :param vec:
        :param captcha_list: CAPTCHA_LIST
        :param captcha_len: CAPTCHA_LEN
        :return: 向量的字符串形式
        """
        captcha_list = self.captcha_list
        captcha_len = self.captcha_len
        
        vec_idx = vec
        text_list = [captcha_list[int(v)] for v in vec_idx]
        return ''.join(text_list)
    
    
    # def wrap_gen_captcha_text_and_image(self, shape=(50, 180, 3)):
    #     """
    #     返回特定shape图片
    #     :param shape:
    #     :return:
    #     """
    #     t, im = self.gen_captcha_text_and_image()
    #     return t, im

    def get_train_batch(self, batch_count=60):
        """
        获取训练图片组
        :param batch_count: default 60
        :param width: 验证码宽度
        :param height: 验证码高度
        :return: batch_x, batch_yc
        """

        width = self.captcha_width
        height = self.captcha_height

        batch_x = np.zeros([batch_count, width * height])
        batch_y = np.zeros([batch_count, self.captcha_len * len(self.captcha_list)])
        for i in range(batch_count):    # 生成对应的训练集
            text, image = self.gen_captcha_train_and_image()
            image = self.convert2gray(image)     # 转灰度numpy
            # 将图片数组一维化 同时将文本也对应在两个二维组的同一行
            batch_x[i, :] = image.flatten() / 255
            batch_y[i, :] = self.text2vec(text)  # 验证码文本的向量形式
        # 返回该训练批次
        return batch_x, batch_y
    
    def get_test_batch(self, batch_count=60):
        """
        获取训练图片组
        :param batch_count: default 60
        :param width: 验证码宽度
        :param height: 验证码高度
        :return: batch_x, batch_yc
        """

        width = self.captcha_width
        height = self.captcha_height
        
        batch_x = np.zeros([batch_count, width * height])
        batch_y = np.zeros([batch_count, self.captcha_len * len(self.captcha_list)])
        for i in range(batch_count):    # 生成对应的训练集
            text, image = self.gen_captcha_test_and_image()
            image = self.convert2gray(image)     # 转灰度numpy
            # 将图片数组一维化 同时将文本也对应在两个二维组的同一行
            batch_x[i, :] = image.flatten() / 255
            batch_y[i, :] = self.text2vec(text)  # 验证码文本的向量形式
        # 返回该训练批次
        return batch_x, batch_y

    def content2image(self, content):
        
        captcha_image = Image.open(io.BytesIO(content))
        # 转化为np数组
        image = np.array(captcha_image)
        image = self.convert2gray(image)
        image = image.flatten() / 255
        return image
        