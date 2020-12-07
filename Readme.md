# 文件结构

实验2-HMM模型拼音转汉字输入法.pdf

实验2-HMM模型拼音转汉字输入法.docx

## src

data_train.py	训练实验所给的语料文件

HMM_Typewriting.py	基于实验所有的语料文件构建的HMM模型和拼音输入法程序

HMM_Typewriting2.py	基于https://github.com/THUzhangga/HMM_shurufa/tree/master/data的语料文件构建的HMM模型和拼音输入法程序

## train_data

toutiao_cat_data.txt 实验所给的语料文件

## data 

###### 基于实验所有的语料文件构建的语料数据库、测试集和训练结果

 my_emission_dic.npy  	发射概率npy

my_hanzi_dict.npy  	汉字编码映射npy

my_hanzi_num.npy  	汉字频次数组npy

my_moving_array.npy  	汉字到汉字转移概率npy

py2hanzi.npy 	拼音映射到汉字npy

my_output_answer.txt  	

my_output_answer_for test_set.txt 	

测试集.txt  老师给的测试集

test_set.txt 	网上找的测试集

## data2

###### 基于https://github.com/THUzhangga/HMM_shurufa/tree/master/data的语料文件构建的语料数据库、测试集和训练结果

emission_dic.npy  

hanzi_num.npy       

py2hanzi.npy hanzi_dict.npy   

moving_array.npy  

output_answer.txt        网上数据集的测试结果  

output_answer_for_测试集.txt 	老师给的数据集测试结果