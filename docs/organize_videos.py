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
"""Concat movies."""
# # # Import current path.
import sys

sys.path.append('..')
# # # Base package.
import os
import random


class OrganizeVideos:
    """request爬行器，爬行器用于交互数据。"""

    @classmethod
    def convert_videos(cls, file_path: str = None, rate: int = 3000, max_rate: int = 3500):
        """Set to session. 设置为代理。
    
    Args:
        file_path (str): 地址. C:\新建文件夹\\11。
        rate (int): 速率。
        max_rate (int): 最大速率。
    
    Returns:
        bool
    """
        try:
            # # # Show the list of files.
            os.chdir(file_path)
            fs = os.listdir("../personal")
            print(f"待转视频数为{len(fs)}")

            n = random.randint(1, 10000)
            for i in fs:
                # # # # Fill the file.
                os.system(f"ffmpeg -i {i} -b:v {rate}k -bufsize {rate}k -maxrate {max_rate}k A{n}.mp4")
                n += 1
            print("结束了")
        except Exception as ex:
            print("报错了")
            print(ex)

    @classmethod
    def concat_videos(cls, file_path: str = None):
        """Set to session. 设置为代理。
    
    Args:
        file_path (str): 地址. C:\新建文件夹\\11。
    
    Returns:
        bool
    """
        try:
            # # # Show the list of files.
            os.chdir(file_path)
            fs = os.listdir("../personal")
            print(f"待连接视频数为{len(fs)}")

            with open("filelist.txt", "w+") as f:
                pass

            for i in fs:
                # # # # Fill the file.
                with open("filelist.txt", "a+") as f:
                    f.write(f"file '{i}'\n")

            n = random.randint(1, 10000)

            os.system(f"ffmpeg -f concat -i filelist.txt -c copy O{n}.mp4")
            os.remove("filelist.txt")
            print("结束了")
        except Exception as ex:
            print("报错了")
            print(ex)

    @classmethod
    def change_files(cls, file_path: str = None, suffix_name: str = None):
        """Set to session. 设置为代理。
    
    Args:
        file_path (str): 地址. C:\新建文件夹\\11。
        suffix_name (str): 后缀名. jpg。
    
    Returns:
        bool
    """
        try:
            # # # Show the list of files.
            os.chdir(file_path)
            fs = os.listdir("../personal")
            print(f"待转文件数为{len(fs)}")

            n = random.randint(1, 10000)

            for i in fs:
                os.renames(i, f"{n}.{suffix_name}")
                n += 1
            print("结束了")
        except Exception as ex:
            print("报错了")
            print(ex)

    @classmethod
    def convert_images(cls, file_path: str = None, resolution: int = 2000, max_count: int = 20):
        """Set to session. 设置为代理。
    
    Args:
        file_path (str): 地址. C:\新建文件夹\\11。
        resolution (int): 分辨率. jpg。
            max_count (int): 范围最大值。
            
    Returns:
        bool
    """
        try:
            # # # Show the list of files.
            os.chdir(file_path)
            fs = os.listdir("../personal")
            print(f"待转图片数为{len(fs)}")

            n = random.randint(1, 10000)

            for i in fs:
                # # # Check the file size.
                s = int((os.path.getsize(i) / 1024) / 1024)
                if 0 < s < max_count:
                    os.system(f"magick convert -resize {resolution}x{resolution} {i} A{i}")
                    n += 1

            print("结束了")
        except Exception as ex:
            print("报错了")
            print(ex)


if __name__ == '__main__':
    # ov = OrganizeVideos()
    # ov.convert_videos("C:\新建文件夹\\11", 1200, 1500)
    # ov.concat_videos("C:\新建文件夹\\11")
    # ov.change_files("C:\新建文件夹\\22", "jpg")
    # ov.convert_images("C:\新建文件夹\\22", 1200, 20)
    a = {1: 11, 2: 22, 3: 33}
    
    print(a.)
