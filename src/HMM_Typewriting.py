"""
Author: quxiangjun 20186471
Created on 2020.11.30 9:00
"""
import numpy as np

# init数据
# dic 从写好的npy文件中读取字典如 'a':'阿啊呵锕吖腌嗄'
py2hanzi = np.load('../data/py2hanzi.npy', allow_pickle=True).item()
# dic 汉字：汉字编码  映射表
hanzi_dict = np.load('../data/my_hanzi_dict.npy', allow_pickle=True).item()
# array 汉字到汉字的二维表，填充出现次数
hanzi_matrix = np.load('../data/my_moving_array.npy', allow_pickle=True)  # 汉字出现次数
# array 汉字编码：汉字出现次数
hanzi_num = np.load('../data/my_hanzi_num.npy', allow_pickle=True)  # 汉字出现次数
total_num = sum(hanzi_num)
# 汉字 对应的 拼音 频数 eg：{'了':{'le':5, 'liao':10},'屈':{'qu':5}}
hanzi2pin_dict = np.load('../data/my_emission_dic.npy', allow_pickle=True).item()


class GraphNode(object):
    def __init__(self, hanzi, count, express):
        """
        @describe: 生成有向图节点
        @hanzi: 汉字与编码映射表
        @count: 汉字出现次数
        @express
        """
        # 当前节点所代表的汉字（即状态）
        self.hanzi = hanzi
        # 当前汉字的出现次数
        self.count = count
        # 当前汉字与其他汉字共同出现的次数（词组数列）
        self.express = express
        # 最优路径时，从起点到该节点的最高分， 维特比变量的值
        self.max_prob = 0.0
        # 最优路径时，该节点的前一个节点，用来输出路径的时候使用
        self.prev_node = None


class Graph(object):  # 有向图
    def __init__(self, pinyins):
        """
        @describe: 根据拼音所对应的所有汉字组合，构造有向图
        @pinyins: 预测的拼音输入
        """
        self.bp_array = []  # 存储不同的拼音的汉字列表 [[],[],[]...]
        self.pinyins = pinyins  # 存储此HMM模型的可见拼音序列
        for py in pinyins:
            level = []  # 存储同一拼音下的多个汉字节点
            # 从拼音、汉字的映射表中读取汉字的出现次数以及汉字的词组数列
            hanzi_list = py2hanzi.get(py, "NONE")
            if(hanzi_list == "NONE"):
                print("[ERROR] Don't find the pinyin for:", py)
                continue
            for hanzi in hanzi_list:
                code = hanzi_dict[hanzi]  # 汉字与编码映射表
                count = hanzi_num[code]  # 汉字出现次数
                express = hanzi_matrix[code][:]  # 该汉字编码到所有汉字编码的出现次数
                node = GraphNode(hanzi, count, express)  # 生成有向图节点
                level.append(node)
            self.bp_array.append(level)


def find_P_emission(hanzi, pinyin):
    """
    @describe: 计算此汉字到拼音的发射概率
    @hanzi: 汉字
    @pinyin: 拼音
    @return: P_emission 发射概率
    """
    num_dic = hanzi2pin_dict.get(hanzi, "NO")
    if(num_dic == "NO"):
        print("[ERROR] Don't find the hanzi for:", hanzi)
    total_num = 0  # 目标汉字所有拼音的总频数
    goal_num = 0  # 目标拼音的出现次数
    count = 0  # 总拼音数
    for k, v in num_dic.items():
        if k == pinyin:
            goal_num = v
        total_num += v
        count += 1
    # 计算发射频率 加一平滑
    P_emission = (goal_num + 1) / (total_num + count)
    return P_emission


def viterbi_i(i, graph):
    """
    @describe: 计算每一个可见值对应所有状态的维特比变量值
    @i: 表示第几个可见的值，graph二维数组的第一层index
    @graph: 二维节点数组,HMM模型的有向图，存储bp_array背包二维数组
    """
    # 初始化
    # 对于有向图，在第i层求所有节点的到该节点的最大概率
    if i == 0:  # 如果为第0层
        for state_node in graph.bp_array[i]:  # 遍历该拼音对应的所有状态（中文字符） 计算概率
            code_j = hanzi_dict[state_node.hanzi]  # 第i个状态的j节点的编码
            num_j = hanzi_num[code_j]  # 获得此汉字的一元语言模型的出现次数
            # 计算此模型节点的一元语言模型概率，加一平滑
            P_start = (1 + num_j) / (total_num + len(hanzi_num))
            # 计算此汉字到拼音i的发射概率
            # = find_P_emission(state_node.hanzi, graph.pinyins[i])
            P_emission = 1
            state_node.max_prob = P_start * P_emission
        return

    for state_node in graph.bp_array[i]:
        # 对于第j个节点，需要与前面第i-1层的所有节点匹配，求最大概率
        prob = []
        code_j = hanzi_dict[state_node.hanzi]  # i层j节点的编码
        num_j = hanzi_num[code_j]

        # 此汉字到拼音i的发射概率
        P_emission = 1  # = find_P_emission(state_node.hanzi, graph.pinyins[i])

        for node_k in graph.bp_array[i-1]:  # 对于第i-1层的k节点
            code_k = hanzi_dict[node_k.hanzi]  # 上一层节点的编码
            num_k = hanzi_num[code_k]  # 获得上一层节点汉字的频数（次数）
            a = (node_k.express[code_j] + 1) / \
                (num_k + len(hanzi_num))  # 转移概率 加一平滑
            P_moving = a * node_k.max_prob  # 转移概率 * 前节点的维特比算子值
            prob.append(P_moving)

        # 获取最大概率在i-1层的位置
        max_k = prob.index(max(prob))
        state_node.max_prob = prob[max_k] * P_emission  # 前驱最大的概率 * 发射概率
        state_node.prev_node = graph.bp_array[i-1][max_k]  # 此状态节点的前驱状态节点
    return


def Viterbi(graph):
    symbol_num = len(graph.bp_array)  # 有n个拼音符号
    for i in range(symbol_num):  # 遍历每一个观测值————拼音
        viterbi_i(i, graph)  # 计算每一个状态（中文字符）的实现概率


def bestpath(graph):  # 获取最佳路径
    symbol_num = len(graph.bp_array)
    max_prob = []
    for node in graph.bp_array[symbol_num-1]:
        max_prob.append(node.max_prob)
    max_index = max_prob.index(max(max_prob))
    node = graph.bp_array[symbol_num-1][max_index]
    result = []
    real_result = ''
    while True:
        result.append(node.hanzi)
        node = node.prev_node
        if node is None:
            break
        if node.prev_node is None:
            result.append(node.hanzi)
            break
    while len(result) > 0:
        hz = result.pop()
        real_result += hz
    return real_result


def Correct_ratio(s, s_true):
    """
    @describe: 单次输入获取正确率
    @s: 预测结果
    @s_true: 正确结果
    @return count,n,ratio 正确个数，总字数，正确率
    """
    n = len(s)
    count = 0
    for x, y in zip(s, s_true):
        if x == y:
            count += 1
    return count,n,count / n


def Typewriting():
    """
    @describe: 输入法程序
    """
    # 输入的拼音和答案啊
    input_py = open('../data/test_set.txt', 'r')
    input_pinyin = [] # 测试拼音
    input_answer = [] # 测试答案
    count = 0
    for line in input_py.readlines():
        if(count == 1): # 答案
            count = 0 
            input_answer.append(line)
        else: # 拼音
            count = 1
            input_pinyin.append(line)
            
    # 输出的文件
    input_py.close()
    output_hz = open('../data/my_output_answer_for test_set.txt', 'w')
    
    # 测试开始
    correct_count = 0 # 正确个数
    total_count = 0 # 总个数
    
    for i in range(len(input_pinyin)):
        line = input_pinyin[i]
        answer = input_answer[i][0:-1]
        
        pinyins = line.lower().split()
        new_pys = []
        for py in pinyins:  # 转换固定的字母到对应的拼音
            # if 'nv' in py:
            #     py = py.replace("nv",'nü')
            # elif 'lv' in py :
            #     py = py.replace('lv','lü')
            # elif 'qv' in py:
            #     py = py.replace('qv','qu')
            # elif 'xv' in py:
            #     py = py.replace('xv','xu')
            new_pys.append(py)
        # 构建HMM_Graph 模型
        HMM_graph = Graph(new_pys)
        # 维特比算法计算每个状态节点的维特比变量
        Viterbi(HMM_graph)
        # 找到最优状态序列
        result = bestpath(HMM_graph)
        # 正确率计算
        (c_count,n_count,ratio) = Correct_ratio(result, answer)
        correct_count += c_count
        total_count += n_count
        print("result: {} correct_ratio: {}".format(result,ratio))
        output_hz.write('%s\n' % result)
    print("total correct ratio:{:.2%}".format(correct_count/total_count))
    output_hz.close()


if __name__ == '__main__':
    Typewriting()
