#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
截图自动重命名工具
功能：
1. 监控桌面新截图
2. 使用 OCR 识别图片文字
3. 调用 AI 生成文件名
4. 移动文件到指定文件夹并重命名
"""

import os
from openai import OpenAI
from PIL import Image
import time
import tkinter as tk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import easyocr

# 设置 API key
API_KEY = 'sk-a7adb9abbd004a8dbabfac022dbabf72'

def get_screen_size():
    """在主线程中获取屏幕尺寸"""
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    return screen_width, screen_height

class ScreenshotHandler(FileSystemEventHandler):
    def __init__(self, screen_size):
        print("\n=== 初始化截图处理器 ===")
        self.client = OpenAI(
            api_key=API_KEY,
            base_url="https://api.deepseek.com"
        )
        # 初始化 OCR reader
        print("初始化 OCR 识别器...")
        self.reader = easyocr.Reader(['ch_sim', 'en'])
        # 保存屏幕尺寸
        self.screen_width, self.screen_height = screen_size
        print("初始化完成")
        
    def is_screenshot(self, filename):
        clean_name = filename.lstrip('.')
        is_ss = clean_name.startswith("Screenshot") and clean_name.endswith(".png")
        print(f"检查文件: {filename} -> 清理后: {clean_name} -> 是否为截图: {is_ss}")
        return is_ss

    def get_image_description(self, image_path):
        try:
            print(f"\n开始处理图片: {image_path}")
            
            if not os.path.exists(image_path):
                print(f"文件不存在: {image_path}")
                return None, None
            
            # 检查是否是全屏截图
            with Image.open(image_path) as img:
                if abs(img.width - self.screen_width) <= 100 and abs(img.height - self.screen_height) <= 100:
                    print("检测到全屏截图")
                    return "全屏截图", image_path
            
            # OCR 识别文字
            print("正在进行 OCR 文字识别...")
            results = self.reader.readtext(image_path)
            
            # 提取所有文字
            texts = [result[1] for result in results]
            if not texts:
                print("未识别到文字")
                return "未知图片", image_path
                
            full_text = " ".join(texts)
            print(f"识别到的文字: {full_text}")
            
            try:
                # 使用 AI 提取关键词
                print("正在生成文件名...")
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {
                            "role": "system",
                            "content": """请根据提供的文字生成简短的文件名：
1. 只提取1-2个最重要的关键词
2. 使用下划线连接多个词
3. 保持原文语言（中文或英文）
4. 去掉所有标点符号
5. 每个词首字母大写
6. 总长度控制在20个字符以内
7. 不要添加任何解释"""
                        },
                        {
                            "role": "user",
                            "content": f"请为这段文字生成文件名：{full_text}"
                        }
                    ],
                    max_tokens=50
                )
                
                result = response.choices[0].message.content.strip()
                print(f"生成的文件名: {result}")
                
                if not result:
                    print("生成文件名失败，使用默认名称")
                    return "未知图片", image_path
                
                return result, image_path
                
            except Exception as e:
                print(f"AI 处理失败: {str(e)}")
                return "未知图片", image_path
                
        except Exception as e:
            print(f"处理出错: {str(e)}")
            return None, None

    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = event.src_path
        filename = os.path.basename(file_path)
        
        print(f"\n检测到新文件: {file_path}")
        
        # 忽略已经重命名的文件
        if not self.is_screenshot(filename):
            return
            
        # 如果是临时文件，等待正式文件
        if filename.startswith('.'):
            print(f"检测到临时文件: {filename}")
            final_path = os.path.join(
                os.path.dirname(file_path),
                filename.lstrip('.')
            )
            print(f"等待正式文件: {final_path}")
            
            # 等待临时文件消失和正式文件出现
            max_attempts = 10
            for attempt in range(max_attempts):
                if os.path.exists(final_path):
                    print(f"找到正式文件: {final_path}")
                    time.sleep(1)  # 等待文件系统稳定
                    self.process_screenshot(final_path)
                    break
                time.sleep(0.5)
            return
            
        # 处理正式文件
        self.process_screenshot(file_path)

    def process_screenshot(self, file_path):
        """处理截图文件"""
        print(f"\n开始处理截图: {file_path}")
        
        # 等待文件稳定
        time.sleep(1)
        
        if not os.path.exists(file_path):
            print("文件不存在，跳过处理")
            return
            
        description, final_path = self.get_image_description(file_path)
        
        # 添加调试信息
        print(f"准备重命名:")
        print(f"原始路径: {final_path}")
        print(f"文件是否存在: {os.path.exists(final_path)}")
        
        if description and final_path and os.path.exists(final_path):
            try:
                # 确保截图文件夹存在
                screenshots_dir = os.path.join(os.path.expanduser("~/Desktop"), "截图")
                if not os.path.exists(screenshots_dir):
                    os.makedirs(screenshots_dir)
                    print(f"创建截图文件夹: {screenshots_dir}")
                
                new_filename = f"{description}.png"
                new_path = os.path.join(screenshots_dir, new_filename)
                print(f"新文件路径: {new_path}")
                
                # 检查新文件名是否已存在
                if os.path.exists(new_path):
                    print(f"目标文件已存在，添加时间戳")
                    timestamp = time.strftime("%H%M%S")
                    new_filename = f"{description}_{timestamp}.png"
                    new_path = os.path.join(screenshots_dir, new_filename)
                
                os.rename(final_path, new_path)
                print(f"\n文件已重命名并移动到截图文件夹: {new_filename}")
            except Exception as e:
                print(f"重命名或移动失败: {str(e)}")
                print(f"错误类型: {type(e)}")
        else:
            print("重命名条件不满足:")
            print(f"description: {description}")
            print(f"final_path: {final_path}")
            print(f"文件存在: {os.path.exists(final_path) if final_path else False}")
                
        print("\n等待下一个截图...")

def main():
    print("\n=== 程序启动 ===")
    
    # 在主线程中获取屏幕尺寸
    screen_size = get_screen_size()
    
    source_path = os.path.expanduser("~/Desktop")
    print(f"监控路径: {source_path}")
    
    # 传入屏幕尺寸
    event_handler = ScreenshotHandler(screen_size)
    observer = Observer()
    observer.schedule(event_handler, source_path, recursive=False)
    observer.start()
    
    print("\n开始监控桌面，请进行截图操作...")
    print("按 Ctrl+C 可停止程序")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n程序已停止")
    
    observer.join()

if __name__ == "__main__":
    main() 