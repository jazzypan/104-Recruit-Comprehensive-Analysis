import numpy as np
import pandas as pd
import requests
import time 
import json
import re
import argparse
import logging

from pathlib import Path
from tqdm import tqdm
from bs4 import BeautifulSoup





job_total_values = []

company_total_values = []

for page in tqdm(range(1,151)):
    url = f'https://www.104.com.tw/jobs/search/?ro=1&kwop=7&keyword=%E6%95%B8%E6%93%9A&order=12&asc=0&page={page}&mode=s&jobsource=2018indexpoc'
    re = requests.get(url)
    doc = BeautifulSoup(re.text, 'html.parser')

     # 擷取工作頁面連結
    content = doc.find_all(['article'])
    for nodes in content:
        hrefs = nodes.find_all(['div','a'], href = True)
        
        if len(hrefs)>0:
            if '104hunter' not in hrefs[0]['href']:

            # 爬蟲：職位相關
                job_values = []

                # 工作描述頁面
                job_page_id = hrefs[0]['href'].split('?')[0].split('/')[-1]

                job_url = 'https://www.104.com.tw/job/ajax/content/' + job_page_id

                    # 0. 公司代碼/工作代碼: str
                job_values.append(hrefs[1]['href'].split('?')[0].split('/')[-1])
                job_values.append(job_page_id)


                # 擷取工作敘述頁面資料
                re_job = requests.get(job_url, headers = {"Referer":"https://www.104.com.tw/job/" + job_page_id})
                job_text = json.loads(re_job.text)['data']


                    # 1. 工作名稱, str
                job_values.append(job_text['header']['jobName']) 

                    # 2. 工資待遇, str/int
                job_values.append(job_text['jobDetail']['salary']) # str: 工資區間
                job_values.append(job_text['jobDetail']['salaryMin']) # int: 最低工資
                job_values.append(job_text['jobDetail']['salaryMax']) # int: 最高工資
            
                    # 3. 工作性質: str
                job_values.append('/'.join(list(map(lambda x: x['description'], job_text['jobDetail']['jobCategory']))))
            
                    # 4. 工作敘述: str
                job_values.append('/'.join([text for text in job_text['jobDetail']['jobDescription'].split('\n') if text!='']))
            
                    # 5. 需求人數: str
                job_values.append(job_text['jobDetail']['needEmp'])
            
                    # 6. 經驗要求: str
                job_values.append(job_text['condition']['workExp'])

                    # 7. 學歷要求: str
                job_values.append(job_text['condition']['edu'])

                    # 8. 科系要求: str
                job_values.append('/'.join(job_text['condition']['major']))

                    # 9. 語文: str / list[str]
                if len(job_text['condition']['language'])>0:
                    job_values.append(job_text['condition']['language'][0]['language']) # 語言條件
                    job_values.append(job_text['condition']['language'][0]['ability']) # 語言能力
                else: 
                    job_values.append('None')
                    job_values.append('None')


                    # 10. 擅長工具: str
                job_values.append('/'.join(list(map(lambda x: x['description'], job_text['condition']['specialty']))))

                    # 11. 工作技能: str
                job_values.append('/'.join(list(map(lambda x: x['description'], job_text['condition']['skill']))))

                    # 12. 其他條件: str
                job_values.append(job_text['condition']['other'].replace('\n', ' ').replace('\r', ''))

                    # 13. 應徵人數: str
                job_values.append(nodes.find_all('a', class_ = ['b-link--gray gtm-list-apply'])[0].text)

                    # 14. 經緯度: float
                job_values.append(job_text['jobDetail']['longitude'])
                job_values.append(job_text['jobDetail']['latitude'])

                job_total_values.append(job_values)


            # 爬蟲：公司相關
                company_values = []


                # 公司資訊頁面
                company_page_id = hrefs[1]['href'].split('?')[0].split('/')[-1]

                company_url = "https://www.104.com.tw/company/ajax/content/" + company_page_id

                # 0. 公司代碼 
                company_values.append(company_page_id)

                # 擷取公司頁面資料
                re_comapany = requests.get(company_url, headers = {"Referer":"https://www.104.com.tw/campany/"+ company_page_id})
                company_text = json.loads(re_comapany.text)['data']

                    # 1. 公司名稱: str
                company_values.append(company_text['custName'])

                    # 2. 公司類別(大): str
                company_values.append(company_text['industryDesc'])

                    # 3. 公司類別(小): str
                company_values.append(company_text['indcat'])

                    # 4. 公司人數: str
                company_values.append(company_text['empNo'])

                    # 5. 公司資本額: str
                company_values.append(company_text['capital'])

            
                company_total_values.append(company_values)
    
        else: pass
    else: pass

    
    time.sleep(1)




job_columns = ['公司代碼','工作代碼','工作名稱','工資待遇','工資待遇(最低)', '工資待遇(最高)','工作性質','工作敘述','需求人數','經驗要求','學歷要求','科系要求','語文條件','語言能力','擅長工具','工作技能','其他條件', '應徵人數', '經度','緯度']
df_job = pd.DataFrame(job_total_values, columns = job_columns)
df_job.to_csv('../Dataset/job.csv', index = False)

company_columns = ['公司代碼','公司名稱','公司類別(大)','公司類別(小)','公司人數','公司資本額']
df_company = pd.DataFrame(company_total_values, columns = company_columns)
df_company.to_csv('../Dataset/company.csv', index = False)
