import requests
import urllib3
import socket
import os
import base64
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- [配置区] ---
UUID = os.getenv("MY_UUID", "3afad5df-e056-4301-846d-665b4ef51968")
HOST = os.getenv("MY_HOST", "x.kkii.eu.org")
MAX_WORKERS = 15 
SUFFIX = "@schpd_chat" # 你要求的后缀
# -------------------------------

def check_ip_port(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        result = s.connect_ex((ip, int(port)))
        s.close()
        return result == 0
    except:
        return False

def process_region(code, name):
    api_url = f"https://proxyip.881288.xyz/api/txt/{code}"
    headers = {'User-Agent': 'v2rayN/6.23'}
    region_nodes = []
    try:
        res = requests.get(api_url, headers=headers, verify=False, timeout=10)
        if res.status_code == 200:
            lines = [l.strip() for l in res.text.splitlines() if l.strip()]
            for index, line in enumerate(lines):
                if "#" in line:
                    addr, raw_memo = line.split("#")
                    ip, port = addr.split(":")
                    if check_ip_port(ip, port):
                        dynamic_path = f"/{ip}:{port}"
                        
                        # --- 【优化：按照要求命名】 ---
                        # 生成 01, 02 这种格式的编号
                        idx_str = str(index + 1).zfill(2)
                        # 最终命名：地区名 + 编号 + 后缀
                        node_name = f"{name}{idx_str}{SUFFIX}"
                        # ----------------------------

                        vless = f"vless://{UUID}@{ip}:{port}?encryption=none&security=tls&sni={HOST}&type=ws&host={HOST}&path={dynamic_path}#{node_name}"
                        region_nodes.append(vless)
    except:
        pass
    return region_nodes

def main():
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
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_region, c, n): n for c, n in region_map.items()}
        for future in as_completed(futures):
            all_nodes.extend(future.result())

    if all_nodes:
        # 保存 nodes.txt (明文)
        with open("nodes.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(all_nodes))
        
        # 保存 sub.txt (Base64)
        with open("sub.txt", "w", encoding="utf-8") as f:
            b64_content = base64.b64encode("\n".join(all_nodes).encode("utf-8")).decode("utf-8")
            f.write(b64_content)
        print(f"成功更新 {len(all_nodes)} 个节点")

if __name__ == "__main__":
    main()
