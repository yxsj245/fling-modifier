#===运行库===
import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, urlsplit
import zipfile
from tqdm import tqdm

#===方法库===
#模拟浏览器访问
def get_redirected_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    # 发送HEAD请求获取重定向后的URL
    response = requests.head(url, headers=headers, allow_redirects=True)
    if response.status_code == 200:
        return response.url
    else:
        return None

#下载文件
def download_file(url, directory, filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    # 发送HTTP请求并获取响应
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        # 创建文件夹
        os.makedirs(directory, exist_ok=True)
        # 拼接文件保存路径
        filepath = os.path.join(directory, filename)
        # 获取文件大小
        total_size = int(response.headers.get('content-length', 0))
        # 下载文件并显示进度条
        with open(filepath, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as progress_bar:
                for data in response.iter_content(chunk_size=1024):
                    f.write(data)
                    progress_bar.update(len(data))
        return filepath
    else:
        print(f"Failed to download file from {url}")
        return None

#解压文件
def unzip_file(zipfile_path, extract_folder):
    # 解压文件
    with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)

#删除文件
def delete_file(file_path):
    os.remove(file_path)

#解析网页标签
def get_first_attachment_link(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    # 发送HTTP请求并获取HTML内容
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        html_content = response.text
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        # 查找第一个class属性为attachment-link的a标签
        attachment_link = soup.find('a', class_='attachment-link')
        if attachment_link:
            file_url = urljoin(url, attachment_link.get('href'))
            redirected_url = get_redirected_url(file_url)
            if redirected_url:
                title = attachment_link.get('title')
                print("Title:", title)
                print("Href:", redirected_url)
                return title, redirected_url
            else:
                print(f"Failed to get redirected URL for {file_url}")
        else:
            print("No attachment link found.")
            return None, None
    else:
        print("Failed to retrieve the webpage.")
        return None, None

#下载核心文件
def download_and_extract_attachment(url):
    print("正在访问和解析网站，如果长时间无反应后崩溃则是网络或网站问题")
    title, first_attachment_url = get_first_attachment_link(url)
    if first_attachment_url:
        filename = os.path.basename(first_attachment_url)
        print(f"成功解析出下载地址，文件名称: {filename}")
        # 解析URL获取最后一个路径部分作为文件夹名称
        folder_name = unquote(urlsplit(url).path.split('/')[-2])
        # 创建以标题为名的文件夹
        folder_path = os.path.join('data', folder_name)
        # 获取文件路径
        filepath = os.path.join(folder_path, filename)
        # 下载文件
        print(f"开始下载修改器")
        if not os.path.exists(folder_path) or filename not in os.listdir(folder_path):
            filepath = download_file(first_attachment_url, folder_path, filename)
            if filepath:
                print("提取修改器主程序")
                unzip_file(filepath, folder_path)
                delete_file(filepath)
                print("下载完毕，请重新运行程序即可启动修改器界面选择对应修改器即可启动")
                input()
        else:
            print("File already exists in target directory.")

        # 更新 JSON 文件中的值
        update_data_json(True)

#创建json
def create_data_json():
    data = {"run": False}  # 默认值为 False
    with open("data.json", "w") as json_file:
        json.dump(data, json_file)

#读取json
def read_data_json():
    if os.path.exists("data.json"):
        with open("data.json", "r") as json_file:
            data = json.load(json_file)
        return data
    else:
        return None

#更新json
def update_data_json(run_value):
    data = {"run": run_value}
    with open("data.json", "w") as json_file:
        json.dump(data, json_file)

#遍历目录
def list_folders(directory):
    folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
    folders.sort()
    return folders


#启动修改器
def launch_exe(directory):
    exes = [f for f in os.listdir(directory) if f.endswith('.exe')]
    if exes:
        exe_path = os.path.join(directory, exes[0])
        os.system('start "" "{}"'.format(exe_path))
    else:
        print("No executable (.exe) files found in the directory.")


# 检查是否首次运行程序
if not os.path.exists("data.json"):
    create_data_json()
data = read_data_json()
if data is not None and not data["run"]:
    # 调用函数并传入指定网站的URL
    urldata = input("请输入需要下载的风灵月影修改器地址:")
    url = urldata
    download_and_extract_attachment(url)
else:
    #启动修改器主程序
    data_dir = 'data'
    folders = list_folders(data_dir)
    for i, folder in enumerate(folders, start=1):
        print(f"{i}. {folder}")

    try:
        print("权限提升安全提醒：由于Windows权限规则，启动exe文件必须以管理员身份运行，输入后程序将会请求Windows以管理员身份启动修改器。")
        choice = int(input("请输入要启动的游戏名称修改器(输入前面序号即可): "))
        if 1 <= choice <= len(folders):
            selected_folder = os.path.join(data_dir, folders[choice - 1])
            launch_exe(selected_folder)
        else:
            print("请输入正确序号")
    except ValueError:
        print("捕捉到错误")
