import requests
import urllib3
import socket
import os
import base64
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- [配置区：已为你填好默认值] ---
# 如果 GitHub Secrets 里没配置，就直接用下面这两行
UUID = os.getenv("MY_UUID", "3afad5df-e056-4301-846d-665b4ef51968")
HOST = os.getenv("MY_HOST", "x.kkii.eu.org")
MAX_WORKERS = 15 
# -------------------------------

def check_ip_port(ip, port):
    """验证 IP 端口是否畅通"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0) # GitHub 环境网速快，1秒足够
        result = s.connect_ex((ip, int(port)))
        s.close()
        return result == 0
    except:
        return False

def process_region(code, name):
    """抓取并验证单个地区"""
    api_url = f"https://proxyip.881288.xyz/api/txt/{code}"
    headers = {'User-Agent': 'v2rayN/6.23'}
    region_nodes = []
    try:
        res = requests.get(api_url, headers=headers, verify=False, timeout=10)
        if res.status_code == 200:
            lines = [l.strip() for l in res.text.splitlines() if l.strip()]
            for line in lines:
                if "#" in line:
                    addr, raw_memo = line.split("#")
                    ip, port = addr.split(":")
                    if check_ip_port(ip, port):
                        # 路径对齐你提供的 Clash 配置
                        dynamic_path = f"/{ip}:{port}"
                        # 剔除备注中的毫秒数
                        clean_memo = raw_memo.split('~')[0].strip()
                        # 组装 VLESS
                        vless = f"vless://{UUID}@{ip}:{port}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={dynamic_path}#{name}_{clean_memo}"
                        region_nodes.append(vless)
    except:
        pass
    return region_nodes

def main():
    # 包含你要求的所有全地区代码
    region_map = {
        "HK": "香港", "TW": "台湾", "JP": "日本", "KR": "韩国", "SG": "新加坡",
        "MY": "马来西亚", "TH": "泰国", "VN": "越南", "ID": "印尼", "PH": "菲律宾",
        "MM": "缅甸", "LA": "老挝", "KH": "柬埔寨", "BD": "孟加拉", "IN": "印度",
        "PK": "巴基斯坦", "BN": "文莱", "US": "美国", "CA": "加拿大", "MX": "墨西哥",
        "BR": "巴西", "AR": "阿根廷", "CL": "智利", "CO": "哥伦比亚", "PE": "秘鲁",
        "GB": "英国", "DE": "德国", "FR": "法国", "NL": "荷兰", "RU": "俄罗斯",
        "IT": "意大利", "ES": "西班牙", "TR": "土耳其", "PL": "波兰", "UA": "乌克兰",
        "SE": "瑞典", "FI": "芬兰", "NO": "挪威", "DK": "丹麦", "CZ": "捷克",
        "RO": "罗马尼亚", "CH": "瑞士", "PT": "葡萄牙", "AU": "澳大利亚", "NZ": "新西兰",
        "ZA": "南非", "EG": "埃及", "NG": "尼日利亚", "SA": "沙特", "AE": "阿联酋",
        "IL": "以色列", "IR": "伊朗", "IQ": "伊拉克"
    }

    all_nodes = []
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 GitHub Actions 多线程扫描启动...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_region, c, n): n for c, n in region_map.items()}
        for future in as_completed(futures):
            res = future.result()
            if res:
                all_nodes.extend(res)
                print(f" √ {futures[future]} 采集完成")

    if all_nodes:
        # 保存明文文件
        with open("nodes.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(all_nodes))
        
        # 保存 Base64 订阅文件
        with open("sub.txt", "w", encoding="utf-8") as f:
            content_str = "\n".join(all_nodes)
            b64_content = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
            f.write(b64_content)
            
        print(f"\n✅ 更新成功，总计 {len(all_nodes)} 个有效节点")
    else:
        print("\n❌ 未抓取到有效节点")

if __name__ == "__main__":
    main()
