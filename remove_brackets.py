import os
import re

def remove_brackets(filename):
    """删除文件名中的括号及其内容"""
    return re.sub(r' ?\(\d+\)', '', filename)

def clean_filenames_in_directory(directory_path):
    """遍历目录并处理文件名"""
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            filepath = os.path.join(root, filename)
            if filename == ".DS_Store":
                # 删除.DS_Store文件
                os.remove(filepath)
            else:
                # 清理文件名并重命名
                new_filename = remove_brackets(filename)
                if new_filename != filename:
                    new_filepath = os.path.join(root, new_filename)
                    os.rename(filepath, new_filepath)

directory_path = os.path.expanduser('~/Downloads/torrent_p/[皮三豆]祈求光明的百合1-2(中文无修)/2')
clean_filenames_in_directory(directory_path)
