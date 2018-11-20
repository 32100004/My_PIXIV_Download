# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 10:33:04 2018

@author: HIT
"""

# coding:utf-8
import requests
from bs4 import BeautifulSoup
import re
import http.cookiejar
import os

import urllib

se = requests.Session()

_USERNAME = "userbay"
_PASSWORD = "userpay"

class PixivSubClass:
    def __init__(self):
        self.title = '' # title of an image
        self.pic_id = -1 # pic id of an image
        self.y_rank = -1 # yesterday ranking 
        self.type = 'illust'
        self.multiple_imge = 0
        self.num_of_img = 1
        self.flag = 0
        self.t_rank = -1
		


class PixivPicLoad:
    def __init__(self):
        
        self.session = requests.Session()
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'}
        self.session.headers = self.headers
        self.session.cookies = http.cookiejar.LWPCookieJar(filename='cookies')
        try:
            # 加载cookie
            self.session.cookies.load(filename='cookies', ignore_discard=True)
        except:
            print('cookies不能加载')

        self.params ={
            'lang': 'en',
            'source': 'pc',
            'view_type': 'page',
            'ref': 'wwwtop_accounts_index'
        }
        self.datas = {
            'pixiv_id': '',
            'password': '',
            'captcha': '',
            'g_reaptcha_response': '',
            'post_key': '',
            'source': 'pc',
            'ref': 'wwwtop_accounts_indes',
            'return_to': 'https://www.pixiv.net/'
            }
        self.load_path = 'D:\JiaWork\Picture'
        
        
        
        
    def get_postkey(self):
        login_url = 'https://accounts.pixiv.net/login' # 登陆的URL
        # 获取登录页面
        res = self.session.get(login_url, params=self.params)
        # 获取post_key
        pattern = re.compile(r'name="post_key" value="(.*?)">')
        r = pattern.findall(res.text)
        self.datas['post_key'] = r[0]

    def already_login(self):
        # 请求用户配置界面，来判断是否登录
        url = 'https://www.pixiv.net/setting_user.php'
        login_code = self.session.get(url, allow_redirects=False).status_code
        if login_code == 200:
            return True
        else:
            return False

    def login(self, account, password):
        post_url = 'https://accounts.pixiv.net/api/login?lang=en' # 提交POST请求的URL
        # 设置postkey
        self.get_postkey()
        self.datas['pixiv_id'] = account
        self.datas['password'] = password
        # 发送post请求模拟登录
        result = self.session.post(post_url, data=self.datas)
        print(result.json())
        # 储存cookies
        self.session.cookies.save(ignore_discard=True, ignore_expires=True)
        
    def mkdir(self,path):
        path = path.strip()
        is_exist =os.path.exists(os.path.join(self.load_path,path))
        if not is_exist:
            print('创建一个名字为 '+path+' 的文件夹')
            os.makedirs(os.path.join(self.load_path,path))
            os.chdir(os.path.join(self.load_path,path))
            return True
        else:
            print('名字为 '+path+' 的文件夹已经存在')
            os.chdir(os.path.join(self.load_path,path))
            return False
    
    def download_img(self,pImg,max_num):
        
        download_num = min(pImg.num_of_img,max_num)
        
        for I_DNUM in range(1,download_num+1):
        
            if download_num>1:
                print('Multi Page '+str(I_DNUM)+'-th Downloading ... ')
            
            iurl = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='+str(pImg.pic_id)
            # iurl = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='+str(71486236)
            base_url = 'https://i.pximg.net/img-original/img'
            res = requests.get(iurl)
            html_text = res.text
            indx1 = html_text.find('img-master')+14
            indx2 = html_text.find('_p0',indx1)
            sub_str = html_text[indx1:indx2]
        
            name_suffix1 = '.jpg'
            name_suffix2 = '.png'

            src_headers = self.headers
        
            li_soup = BeautifulSoup(html_text, 'html.parser')
            href = li_soup.find_all('link',attrs={'rel':'canonical'})        
            href = href[0].attrs['href']
            src_headers['Referer']=href
                
            name_suffix=name_suffix1
            img_url = base_url+sub_str+'_p'+str(I_DNUM-1)+name_suffix
        
            html = requests.get(img_url, headers=src_headers)
        
            if html.status_code == 404:
                #debug
                print(pImg.__dict__)
                name_suffix=name_suffix2
                img_url = base_url+sub_str+'_p'+str(I_DNUM-1)+name_suffix
                html = requests.get(img_url, headers=src_headers)
            
            
            img = html.content
            if max_num == 1:
                img_title ='#'+str(pImg.t_rank)+'_'+ pImg.title+'_id:'+str(pImg.pic_id)
            else:
                img_title ='#'+str(pImg.t_rank)+'_'+ pImg.title+'_id:'+str(pImg.pic_id) + '_'+str(I_DNUM)
                
                
        
            img_title = img_title.replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_').replace('|', '_')\
            .replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()
        
        
            with open(img_title + name_suffix, 'ab') as f:
                f.write(img)
        
    
    def download_daily_img(self,date='20181103'):
        
        url_base='https://www.pixiv.net/ranking.php'
        
        max_page = 3 # max_page < 10
        
        num_pic_per_page = 50
        
        multi_page_download_set = 8
        
        if date == "":
            strData=""
        else:
            strData='&date='+date
            
        for iRunIter in range(1,max_page+1):
            url_sub = url_base + '?mode=daily' + strData + '&p='+str(iRunIter)
            print(url_sub)
            
            res = requests.get(url_sub)
            html=res.text
            soup = BeautifulSoup(html,'html.parser')
            
            num_page = min(num_pic_per_page,len(soup.select('section'))-3)
            
            print('The num '+str(iRunIter)+' page is '+str(num_page))
            
            for iImgIter in range(1,num_page+1):
                N = iImgIter + 2

                title=soup.select('section')[N].attrs.get('data-title')
                illus_id=soup.select('section')[N].attrs.get('data-id')

                y_rank = -1
                Info_y_rank = soup.select('p')[N].find('a')
                if Info_y_rank is not None:
                    y_rank = int(re.findall(r"\d+\.?\d*", Info_y_rank.text)[0])


                # 是不是illust
                data_type_raw = soup.select('section')[N].find_all('div')[1].a
                data_type_list = data_type_raw['class']
                img_type_num = 1
                img_mul_num = 0
                img_type = 'illust'
                img_num = 1

                for img_str in data_type_list:
                    if img_str == 'manga':
                        img_type_num = 2
                        img_type = 'manga'
                    if img_str == 'ugoku-illust':
                        img_type_num = -1
                        img_type = 'ugoira'
                    if img_str == 'multiple':
                        img_mul_num = 1
                        img_num = int(data_type_raw.span.text)
                
                pImg=PixivSubClass()
                pImg.title = title
                pImg.t_rank = soup.select('section')[N].attrs.get('id')
                pImg.pic_id = illus_id
                pImg.y_rank = y_rank
                pImg.type = img_type
                pImg.multiple_imge = img_mul_num
                pImg.num_of_img = img_num
                pImg.flag = y_rank < 0 or y_rank > 300
                
                #debug
                #print(pImg.__dict__)
                
                #download image
                # 当图片是插图时
                print('In page '+str(iRunIter)+' No. '+str(iImgIter))
                
                
                if pImg.flag == 0:  # 应该为0
                    print('On yesterday\'s ranking, ignoring...')      
                elif pImg.type == 'illust':
                    # 对于单图保存图片
                    if (pImg.num_of_img ==1) and (pImg.multiple_imge == 0) :
                            self.download_img(pImg,1)
                            print('Successfully downloading '+ str(iImgIter)+' in page '+ str(iRunIter))
                            
                    elif pImg.multiple_imge == 1  :
                        if pImg.num_of_img > multi_page_download_set :
                            print('Multi Page Image Only Download first '+str(multi_page_download_set)+'-th Images')
                        self.download_img(pImg,multi_page_download_set)
                        
                elif pImg.type == 'manga':
                    print('For Images of Type Manga, only download first page')
                    self.download_img(pImg,1)
                    
                else:
                    print('Unable to download GIF, a text file is created...')

                    # 保存图片
                



#################-------MAIN Pro--------######################
# 问 如果有图片被删除 怎么办
spider = PixivPicLoad()
if spider.already_login():
    print('用户已经登录')
else:
#        account = input('请输入用户名\n> ')
#        password = input('请输入密码\n> ')
    account=_USERNAME
    password=_PASSWORD
    spider.login(account, password)

	
iPath = 'D:\MYTMP2DEL'
spider.mkdir(iPath)

spider.download_daily_img(date='20091110')

