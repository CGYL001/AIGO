import requests
import socket
import sys

def get_local_ip():
    """获取本机IP地址"""
    try:
        # 创建一个临时socket连接来获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"  # 如果失败则返回本地回环地址

def check_server(url):
    """检查服务器是否在运行"""
    try:
        response = requests.get(url, timeout=5)
        print(f"服务器状态: {response.status_code}")
        print(f"响应内容: {response.text[:100]}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"无法连接到 {url}")
        return False
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    local_ip = get_local_ip()
    print(f"本机IP地址: {local_ip}")
    
    # 测试不同地址
    urls = [
        "http://127.0.0.1:8080/",
        f"http://{local_ip}:8080/",
        "http://localhost:8080/",
        "http://0.0.0.0:8080/"
    ]
    
    success = False
    for url in urls:
        print(f"\n测试 {url}")
        if check_server(url):
            print(f"服务器在 {url} 运行正常")
            success = True
        else:
            print(f"服务器在 {url} 无法访问")
    
    if not success:
        print("\n所有测试失败，服务器可能未运行")
        sys.exit(1)
