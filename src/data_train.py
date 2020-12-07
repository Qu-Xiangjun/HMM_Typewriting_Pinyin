"""
Author: quxiangjun 20186471
Created on 2020.11.30 9:00
"""
import numpy as np
import json
import re
import pypinyin
from pypinyin import pinyin

def init_data():
    """
    @describe: 准备训练用的数据文件.npy
    """
    # toutiao_data
    phrase = open('../train_data/toutiao_cat_data.txt', 'r',encoding="utf-8")
    ans = []
    for line in phrase.readlines():
        ls = line.split("_!_")
        # 清洗数据
        ls = ls[3:]
        for item in ls:
            string = ""
            i = 0
            while(i<len(item)):
                res = re.match(r'[\u4E00-\u9FA5]', item[i])
                if(res == None):
                    if(string != ""):
                        ans.append(string)
                    string = ""
                else:
                    string += item[i]
                i+=1
            if(string != ""):
                ans.append(string)
    print(ans[0:100])
    
    # 汉字的拼音添加
    ans_pinyin = []
    for item in ans:
        pinyin_ans = pinyin(u'{0}'.format(item), style=pypinyin.NORMAL)
        if(pinyin_ans == None):
            continue
        string = ""
        for item in pinyin_ans:
            string += item[0]+" "
        string = string[0:-1]
        if(string != ""):
            ans_pinyin.append(string)
    # ['bao li ji tuan', 'ma wei du', 'zhong guo ke xue ji zhu guan',...
    print(ans_pinyin[1:100]) 
    
    # 统计汉字信息 [汉字] [出现次数]一元语料
    hanzi_ls = []
    hanzi_count_ls = []
    for item in ans:
        for chr in item:
            if chr not in hanzi_ls:
                hanzi_ls.append(chr)
                hanzi_count_ls.append(0)
            else: 
                hanzi_count_ls[hanzi_ls.index(chr)] += 1
    np.save("../data/my_hanzi_num", hanzi_count_ls, allow_pickle=True, fix_imports=True)
    total_hanzi_num = len(hanzi_ls)
    print(total_hanzi_num)
    
    # dic 汉字：汉字编码  映射表
    hanzi_dict = {}
    encode_num = 0
    for item in hanzi_ls:
        hanzi_dict[item] = encode_num
        encode_num += 1
    np.save("../data/my_hanzi_dict", hanzi_dict, allow_pickle=True, fix_imports=True)
    
    # 二元语料训练
    # 汉字编码到汉字编码的映射 次数
    hanzi_matrix = np.zeros([total_hanzi_num, total_hanzi_num])
    for item in ans:
        for i in range(1,len(item)):
            chr1 = item[i-1]
            chr2 = item[i]
            code1 = hanzi_dict[chr1]
            code2 = hanzi_dict[chr2]
            hanzi_matrix[code1][code2] += 1
    np.save("../data/my_moving_array", hanzi_matrix, allow_pickle=True, fix_imports=True)
    
    # 汉子拼音字典表数据准备
    py2hanzi = {}
    for i in range(len(ans)):
        pinyin_ls = ans_pinyin[i].split() # 拼音序列
        for pinyin_item in pinyin_ls: # 初始化
            py2hanzi[pinyin_item] = ""
    for i in range(len(ans)):
        str = ans[i]# 汉字串
        pinyin_ls = ans_pinyin[i].split() # 拼音序列
        for j in range(len(str)):
            chr = str[j]
            pinyin_item = pinyin_ls[j]
            if( chr not in py2hanzi[pinyin_item]):
                py2hanzi[pinyin_item] += chr
    np.save("../data/py2hanzi.npy", py2hanzi, allow_pickle=True, fix_imports=True)  
    print(py2hanzi.keys())  
    
    # 汉字 对应的 拼音 频数 eg：{'了':{'le':5, 'liao':10},'屈':{'qu':5}}
    hanzi2pin_dict = {} # {'了':{'le':5, 'liao':10},'屈':{'qu':5}}
    hanzi_str = hanzi_ls  # 已存在拼音的汉字序列
    py_data_ls = [] # 已存在的拼音列表
    # 构建双重字典表结构
    for k,v in py2hanzi.items():
        py_data_ls.append(k)
        if "ü" in k:
            print(k)
        hanzi_str += v
        for chr in v:
            hanzi2pin_dict[chr] = {} # 初始化每一个字对应一个拼音频率字典
    for k,v in py2hanzi.items():
        for chr in v:
            hanzi2pin_dict[chr][k] = 0 # 初始化每一个拼音的频率value

    # phrase = open('../train_data/emission_train.txt', 'r')
    for i in range(len(ans)):
        str = ans[i]# 汉字串
        pinyin_ls = ans_pinyin[i].split() # 拼音序列
        for i in range(len(pinyin_ls)): # 去除音调
            pinyin_ls[i] = pinyin_ls[i][0:-1]
        if(len(str) != len(pinyin_ls)): # 拼音与汉字数不匹配
            continue
        for i in range(len(str)):
            if(str[i] not in hanzi_str): # 该汉字不在有拼音的汉字列表 添加到dic
                hanzi2pin_dict[ str[i] ] = {}
                hanzi2pin_dict[ str[i] ][ pinyin_ls[i] ] = 0
            py_data_ls = hanzi2pin_dict[ str[i] ].keys() # 该汉字所有的拼音列表 
            if(pinyin_ls[i] not in py_data_ls):
                hanzi2pin_dict[ str[i] ][ pinyin_ls[i] ] = 0
            hanzi2pin_dict[str[i]][pinyin_ls[i]] += 1
    phrase.close()
    np.save("../data/my_emission_dic", hanzi2pin_dict, allow_pickle=True, fix_imports=True)



if __name__ == '__main__':
    init_data()