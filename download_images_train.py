import json
from tqdm import tqdm
import os
from multiprocessing import Pool
import requests

def read_json(file):
    f=open(file,"r",encoding="utf-8").read()
    return json.loads(f)

def write_json(file,data):
    f=open(file,"w",encoding="utf-8")
    json.dump(data,f,indent=2,ensure_ascii=False)
    return

def download_images(train_id_list):
    error_id_list = []
    for item_id in tqdm(train_id_list, ncols=60):
        while(1):
            oss_url=train_id_info[item_id]["oss_url"]
            image_file=f"{image_prefix}/{item_id}.jpg"
            try:
                if not os.path.exists(image_file):
                    response = requests.get(oss_url,timeout=3)
                    if response.status_code == 200: #Heavy access will result in 420 status codes
                        if response.content:
                            with open(image_file,'wb')as f:
                                f.write(response.content)
                                f.close()
                            flag = 1
                        else:
                            error_id_list.append(item_id)
                            flag = 1
                    elif response.status_code == 404:
                        error_id_list.append(item_id)
                        flag = 1
                else:
                    flag = 1
                    break
            except:
                error_id_list.append(item_id)
                flag = 1
                break
            if flag == 1:
                break
        if flag == 0:
            error_id_list.append(item_id)
    return error_id_list

image_prefix="/mnt/data/Product9D/train_images"
data_root='/mnt/data/Product9D/json'
filename = 'train'
train_id_info = read_json("{}/train.json".format(data_root))

if not os.path.exists(image_prefix):
    os.makedirs(image_prefix)


if __name__ == '__main__':
    train_id_list=list(train_id_info.keys())
    print(len(train_id_list))

    filter_data=train_id_list

    thread_num = 50
    chunk_size = int(len(filter_data) / thread_num)
    chunk_data = [filter_data[i:i + chunk_size] for i in range(0, len(filter_data), chunk_size)]

    pool = Pool(thread_num)
    error_img_id_list = pool.map(download_images, chunk_data)
    pool.close()
    error_img_ids = []
    for error_i in range(len(error_img_id_list)):
        error_img_ids = error_img_ids + error_img_id_list[error_i]
    print(f'total download error : {str(len(error_img_ids))}')
    res_name = "download_res_{}.txt".format(filename)
    with open(f"{data_root}/{res_name}", "w", encoding="utf-8") as fp:
        for line in error_img_ids:
            fp.writelines(line)
            fp.write('\n')
    fp.close()







