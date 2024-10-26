import json
import os
import requests
import re

pretend = False
downloaded = set()
cdn = 'http://cdn.assets.scratch.mit.edu'
# 这里替换成你的代理服务器
proxies = {
    'https': 'socks5h://184.170.248.5:4145',
    'http': 'socks5h://184.170.248.5:4145',
}
#proxies = None

def download_file(url, path):
    if os.path.exists(path):
        print("skip:" + path)
        return
    floder = "/".join(path.split("/")[0:-1])
    if not os.path.exists(floder):
        os.makedirs(floder)
    print(url)
    try:
        res = requests.get(url, proxies=proxies, verify=False)
    except requests.exceptions.ConnectionError as e:
      try:
        res = requests.get(url, proxies=proxies, verify=False)
      except requests.exceptions.ConnectionError as e:
        print(e)
        return None
        
    if path in downloaded:
        return None
    if res.status_code == 200:
        print(path)
        with open(path, "wb") as f:
            f.write(res.content)
            downloaded.add(path)
            return res.content
    else:
        return None


def download_media(json_path):
    if not json_path: return None
    media_url = "https://cdn.assets.scratch.mit.edu/internalapi/asset/%s/get/"
    thumbnails_url = "https://cdn.scratch.mit.edu/scratchr2/static/__628c3a81fae8e782363c36921a30b614__/medialibrarythumbnails/8d508770c1991fe05959c9b3b5167036.gif"
    download_path = "scratch3/internalapi/asset/"
    json_name = json_path.split("/")[-1]

    with open(json_path, "r", encoding="utf8") as f:
        media = json.load(f)
        for m in media:
            if json_name == "sprites.json":
                # download sprite
                # with open(download_path + m['md5'], "r") as s:
                #     sprite = json.load(s)
                sprite = m
                for sound in sprite.get('sounds', []):
                    if "md5" in sound:
                        md5 = sound['md5']
                    else:
                        md5 = sound['md5ext']
                    download_file(media_url % md5, download_path + md5)
                for costume in sprite.get('costumes', []):
                    if "baseLayerMD5" in sound:
                        md5 = costume['baseLayerMD5']
                    else:
                        md5 = costume['md5ext']
                    download_file(media_url % md5, download_path + md5)
                print(m['name'])
            else:
                res = download_file(media_url % m['md5'], download_path + m['md5'])

def scratchJsonStrFromJs(libminjsfile, json_path):
    """从js文件中抽取文件到jsonfile中"""
    json_name = json_path.split("/")[-1]
    pat = f'\/\*\*\*\/\s\"\.\/src\/lib\/libraries\/{json_name}.*?module.exports = JSON.parse\(([^\n]*)\);'
    with open(libminjsfile, 'r', encoding='utf8') as rf, open(json_path, 'w', encoding='utf8') as wf:
        mo = re.search(pat, rf.read(), re.DOTALL)
        jsonobj = json.loads(eval(mo.group(1)))
        json.dump(jsonobj, wf)

libminjsfile = 'scratch3/lib.min.js'
# 下载背景
scratchJsonStrFromJs(libminjsfile,"scratch3/json_index/backdrops.json")
download_media("scratch3/json_index/backdrops.json")
# 下载造型
scratchJsonStrFromJs(libminjsfile,"scratch3/json_index/costumes.json")
download_media("scratch3/json_index/costumes.json")
# 下载声音
scratchJsonStrFromJs(libminjsfile,"scratch3/json_index/sounds.json")
download_media("scratch3/json_index/sounds.json")
# 下载角色
scratchJsonStrFromJs(libminjsfile,"scratch3/json_index/sprites.json")
download_media("scratch3/json_index/sprites.json")