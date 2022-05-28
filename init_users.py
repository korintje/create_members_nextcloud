# -*- coding: utf_8 -*-
import json
import requests
from getpass import getpass

USRS_URL = "ocs/v1.php/cloud/users"
WDAV_URL = "remote.php/dav/files"
SHARE_URL = "ocs/v2.php/apps/files_sharing/api/v1/shares"
NEW_USERS_FNAME = "new_users.txt"
with open("domain.txt", "r") as f:
    BASE_URL = f.read().splitlines()[0]


# ユーザー名とパスワードの入力を受け付ける
ADMIN_ID = input('Admin ID: ')
ADMIN_PASS = getpass('Admin password: ')

# ユーザーの追加
def create_user(user_id, password, group_id, display_name, mail=""):
    res = requests.post(
            f"http://{ADMIN_ID}:{ADMIN_PASS}@{BASE_URL}{USRS_URL}",
            params={
                "format": "json",
                "userid": user_id,
                "password": password,
                "groups[]": [group_id],
                "displayName": display_name,
                "email": mail,
            },
            headers={
                "OCS-APIRequest": "true",
            },
        )
    print(res.status_code)
    print(res.text)


# ユーザーをグループに追加
def add_to_group(user_id, group_id):
    res = requests.post(
            f"http://{ADMIN_ID}:{ADMIN_PASS}@{BASE_URL}{USRS_URL}/{user_id}/groups",
            params={
                "format": "json",
                "groupid": group_id,
            },
            headers={
                "OCS-APIRequest": "true",
            },
        )
    print(res.status_code)
    print(res.text)


# ユーザーディレクトリの作成
def create_homedir(user_id, password, dirname):
    res = requests.request(
            "MKCOL",
            f"http://{user_id}:{password}@{BASE_URL}{WDAV_URL}/{user_id}/{dirname}",            
            params={},
            headers={
                "OCS-APIRequest": "true",
            },
        )
    print(res.status_code)
    print(res.text)


# ユーザーディレクトリをシェア
def share_homedir(user_id, password, dirname, shared_user_id, shareType):
    res = requests.post(
            f"http://{user_id}:{password}@{BASE_URL}{SHARE_URL}",            
            params={
                "format": "json",
                "path": dirname,
                "shareType": shareType,
                "shareWith": shared_user_id,
                "permissions": 2,
            },
            headers={
                "OCS-APIRequest": "true",
            },
        )
    print(res.status_code)
    print(res.text)
    res_data = json.loads(res.text)
    id = res_data["ocs"]["data"]["id"]
    return id


# シェアURLを取得
def get_share_url(user_id, password, share_id):
    res = requests.get(
            f"http://{user_id}:{password}@{BASE_URL}{SHARE_URL}/{share_id}",
            params={
                "format": "json",
            },
            headers={
                "OCS-APIRequest": "true",
            },
        )
    print(res.status_code)
    print(res.text)   
    res_data = json.loads(res.text)
    url = res_data["ocs"]["data"][0]["url"]
    return url


# ユーザーのプロフィールにメールアドレスと共有URLを追加
def set_url_to_profile(user_id, password, mail, share_url):
    res = requests.put(
            f"http://{user_id}:{password}@{BASE_URL}{USRS_URL}/{user_id}",
            params={
                "format": "json",
                "website": share_url,
                "email": mail,
            },
            headers={
                "OCS-APIRequest": "true",
            },
        )
    print(res.status_code)
    print(res.text)   


if __name__ == "__main__":

    common_password = "Nanowire7621"

    # 追加ユーザーリスト
    with open(NEW_USERS_FNAME, "r") as f:
        new_users = [line.split(",") for line in f.read().splitlines()]
    
    # ユーザーごとに実行
    for user in new_users:
        new_id = user[0]
        display_name = user[1]
        mail = user[2]
        create_user(new_id, common_password, "members", display_name, mail=mail)
        # add_to_group(new_id, "members")
        create_homedir(new_id, common_password, new_id)
        share_id = share_homedir(new_id, common_password, new_id, "member", 0) #shareType = 0: user-sharing
        share_id = share_homedir(new_id, common_password, new_id, "member", 3) #shareType = 3: public link-sharing
        share_url = get_share_url(new_id, common_password, share_id)
        print(share_url)
        set_url_to_profile(new_id, common_password, mail, share_url)

