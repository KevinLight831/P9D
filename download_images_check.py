import json
from tqdm import tqdm
import os
from multiprocessing import Pool
import requests
from PIL import Image
import warnings
warnings.filterwarnings('ignore')
Image.MAX_IMAGE_PIXELS = None

def read_json(file):
    f=open(file,"r",encoding="utf-8").read()
    return json.loads(f)

def write_json(file,data):
    f=open(file,"w",encoding="utf-8")
    json.dump(data,f,indent=2,ensure_ascii=False)
    return

def filter_download_images(train_id_list):
    unopen_id_list = []
    error_id_list = []
    for item_id in tqdm(train_id_list, ncols=0):
        try:
            image_file=f"{image_prefix}/{item_id}.jpg"
            img = Image.open(image_file)
        except:
            unopen_id_list.append(item_id)
            while(1):
                oss_url=train_id_info[item_id]["image_link"]
                image_file=f"{image_prefix}/{item_id}.jpg"
                flag = 0
                try:
                    response = requests.get(oss_url,timeout=3)
                    if response.status_code == 200: #Heavy access will result in 420 status codes
                        if response.content:
                            print(response.status_code)
                            with open(image_file,'wb')as f:
                                f.write(response.content)
                                f.close()
                            flag = 1
                        else:
                            print('ok')
                            error_id_list.append(item_id)
                            flag = 1
                    elif response.status_code == 404:
                        print(response.status_code)
                        error_id_list.append(item_id)
                        flag = 1
                except:
                    print('ohno')
                    error_id_list.append(item_id)
                    flag = 1
                    break
                if flag == 1:
                    break
    return [unopen_id_list, error_id_list]

#check test, query and gallery
image_prefix="/mnt/data/Product9D/gallery_images"
data_root='/mnt/data/Product9D/json'
filename = 'test' # 'query', 'gallery'
train_id_info = read_json("{}/{}.json".format(data_root,filename))

# #check train
# image_prefix="/mnt/data/Product9D/train_images"
# data_root='/mnt/data/Product9D/json'
# filename = 'train'
# train_id_info = read_json("{}/train.json".format(data_root))

if not os.path.exists(image_prefix):
    os.makedirs(image_prefix)


if __name__ == '__main__':
    train_id_list=list(train_id_info.keys())
    print(len(train_id_list))
    
    # #check train
    # train_id_list = []
    # for industry in list(train_id_info.keys()):
    #     train_id_list+=list(train_id_info[industry])
    # print(len(train_id_list))

    thread_num = 50
    chunk_size = int(len(train_id_list) / thread_num)
    chunk_data = [train_id_list[i:i + chunk_size] for i in range(0, len(train_id_list), chunk_size)]

    pool = Pool(thread_num)
    unopen_error_img_id_list = pool.map(filter_download_images, chunk_data)
    pool.close()
    error_img_ids = []
    unopen_img_ids = []
    for error_i in range(len(unopen_error_img_id_list)):
        error_img_ids = error_img_ids + unopen_error_img_id_list[error_i][1]
        unopen_img_ids = unopen_img_ids + unopen_error_img_id_list[error_i][0]
    print(f'total download error : {str(len(error_img_ids))}')
    res_name = "download_res_{}.txt".format(filename)
    with open(f"{data_root}/{res_name}", "w", encoding="utf-8") as fp:
        for line in error_img_ids:
            fp.writelines(line)
            fp.write('\n')
    fp.close()
    print(unopen_img_ids)







