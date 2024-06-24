import re
import jieba.posseg as pseg
import multiprocessing
from multiprocessing import Pool
# 防止在 Windows 系统上使用 multiprocessing 模块时，由于 Windows 的某些限制，导致多进程程序无法正常运行。
multiprocessing.freeze_support()

'''
任务分析：
对红楼梦文本进行分析，并进行可视化展示
    TODO: 需要实现的任务：
    1. 人物出场的频次
    2. 每章节字数
    3. 人物社交网络关系。
思路：
    1. 通过简单的文件读取得到文本数据，并在读取数据的时候进行处理
    2. 得到每一卷的内容以及每一回的内容数据等，可以使用
    3. 人物出场频次
        1. 可以通过jeiba库来进行处理，由于普通的jieba库处理速度较慢，我们使用多进程来加速分词的速度。
        2. （未实现）通过深度学习算法来训练模型，或者利用他人已经训练好的模型来对文本进行提取人物名称。
    4. 人物的社交网络关系：
        - 最简单的思路是：分析每一回的文本，在每一回的文本中，出现的名字之间可能会有联系，我们将其提取出来作为最初的关系
        - 第二种思路： 我们可以在思路一的基础上，如果某个关系在多个回中重复出现，我们可以认定为这个关系大概率是正确的。
        - （未实现）第三种思路： 利用深度学习算法来分析文本， 从而得到各个人物之间存在的关系。
'''


class analyzeDream():
    '''
    main(): 是调用整个类中方法的封装。
    '''
    def __init__(self):
        self.path = './红楼梦文本.txt'

    # 构建数据
    def Construct(self, flag: int, datas: list, rollTitle: list = None, context_dict: dict = None, context_change_key_dict: dict = None) -> dict:
        '''
        用于构建数据，一个工具函数，构建一共分为三步:
            1. 将文本构建为字典格式的数据， 其键为数字，值为每一回的文本        --> {0: [txt1, txt2, ...], ...}
            2. 将第一步构建的字典的键换名                                 --> {'第一回': [txt1, txt2, ...], ...}
            3. 将卷名进行整合到第二部构建的字典中                           --> {'第1卷': ['第一回': [txt1, txt2, ...], ...], ...}
        :param flag:    标记，值为[1, 2, 3], 表示构建到那一步了
        :param datas:   列表，构建数据需要的列表
        :param rollTitle:       卷标题
        :param context_dict:    第一步构建的文本字典，其键为数字
        :param context_change_key_dict:     第二部构建的换键的字典，其键为每一回的标题
        :return: 构建出来的字典
        '''
        newDict = {}
        idx = -1
        for data in datas:
            if flag == 1 and data == '\t':
                idx += 1
                newDict[idx] = []
            elif flag == 2 and data == '\t':
                continue
            elif flag == 3 and data == '\t':
                idx += 1
                newDict[rollTitle[idx]] = []
            else:
                if flag == 1:
                    newDict[idx].append(data)
                elif flag == 2:
                    idx += 1
                    newDict[data] = context_dict[idx]
                elif flag == 3:
                    newDict[rollTitle[idx]].append({data: context_change_key_dict[data]})
        return newDict

    # 读取文件
    def ReadFileOfTxt(self, path: str) -> tuple:
        '''
        读取红楼梦文本，并且进行初步的数据处理
        :param path: 读取文件的路径
        :return: 完整的文本, 字典格式的分级文本, 带标记的回标题, 每一回的文本(列表格式), 每一卷的文本(列表格式)

        定义的容器，用于存储数据处理后的结果：
            wholeTxt:   字符串格式(str), 存储读取到的所有文本。
            rollTxt:    字符串格式(str), 临时存储每一卷的文本，而后将文本加入到rollTxtList列表中。
            rollTxtList:   列表格式(list[str]), 存放每一卷的文本数据。
            rollTitle:      列表格式(list[str]), 存储卷标题, 【如: 第一卷】。
            intitleList:    列表格式(list[str]), 存储回标题, 带有标记'\t', 用于标记每一卷下的每一回的个数, 【如: 第一回】。
            incontext:  列表格式(list[str]), 存储每一回的文本, 带有标记'\t', 用于标记每一回下的文本行数(按行读取)。
            paragraphTxt:   字符串格式(str), 用于临时存储每一回的文本, 而后将文本加入到paragraphList列表中。
            paragraphList:  列表格式(list[[str]]), 存储每一回的文本, 不带有标记, 列表格式，外层列表中的每一个内层列表表示一回的文本, 【如: [[第一回文本], [第二回文本]...]】。
        '''
        wholeTxt = ''
        rollTxt = ''
        rollTxtList = []
        rollTitle = []
        intitleList = []
        incontext = []
        paragraphTxt = ''
        paragraphList = []
        # 每一卷和每一回的模式匹配格式
        pattern1 = re.compile(r'第\d卷')
        pattern2 = re.compile(r'第.+回')

        with open(path, 'r', encoding='utf-8') as f:
            context = "Begin"       # 开始读取标志
            while context:
                context = f.readline()
                match1 = pattern1.match(context)
                match2 = pattern2.match(context)

                # 匹配到每一卷
                if match1:
                    if match1.group():
                        rollTitle.append(match1.group())    # 将匹配到的'卷标题'添加到rollTitle变量中
                        intitleList.append('\t')                # 每次匹配到'卷'之后都给'标记回标题'列表添加分隔符, 用于分割不同卷下的'回标题'
                        rollTxtList.append(rollTxt)         # 每次匹配到'卷'之后, 都将已经记录的卷文本添加到rollTxtList中, 表示每一卷的文本数据
                        rollTxt = ''                        # 将临时'卷'变量清空, 以便下记录下一卷文本

                # 匹配到每一回
                elif match2:
                    intitleList.append(f'{match2.group()}')     # 将匹配到的'回标题'添加到rollTitle变量中
                    incontext.append('\t')                  # 每次匹配到'回'之后都给'标记回文本'列表添加分隔符, 用于分割不同回下的'回文本'
                    paragraphList.append([paragraphTxt])    # 匹配到每一回时, 将上一回的文本进行记录
                    paragraphTxt = ''                       # 清空上一回的文本, 以便下记录下一回的文本

                # 匹配到普通文本
                else:
                    incontext.append(context)               # 直接将文本添加到'标记回文本'中
                    paragraphTxt += context                 # 将每一行普通文本存入到临时'回文本'变量中
                    rollTxt += context                      # 将每一行普通文本存入到临时'卷文本'变量中
                    wholeTxt += context                     # 将每一行普通文本存入到'整文本'变量中

        paragraphList.append([paragraphTxt])    # 将最后一个没有被记录的'回文本'记录到'回列表'中
        del paragraphList[0]                    # 删除'回列表'的第一个空元素
        rollTxtList.append(rollTxt)             # 将最后一个没有被记录的'卷文本'记录到'卷列表'中
        del rollTxtList[0]                      # 删除'卷列表'的第一个空元素

        # 构造回文本字典
        context_dict = self.Construct(flag=1, datas=incontext)
        # 给回文本字典换键
        context_change_key_dict = self.Construct(flag=2, datas=intitleList, context_dict=context_dict)
        # 构建完整的字典{卷1:[回1: [txt1, txt2, ...]...]...}
        perfect_dict = self.Construct(flag=3, datas=intitleList, rollTitle=rollTitle, context_change_key_dict=context_change_key_dict)
        # print(intitleList)
        return wholeTxt, perfect_dict, intitleList, paragraphList, rollTxtList  # 整个段落， 字典格式的， 内部标题， 段落列表， 每一卷的文本

    def character(self, context: str) -> int:
        '''
        统计出每个文本中中文的个数.
        :param context: 字符串, 表示一个句子.
        :return: 返回该句子中中文的个数.
        '''
        context = ''.join(context)
        # 正则表达式匹配中文字符
        pattern = re.compile(r'[\u4e00-\u9fff]+', re.UNICODE)
        # 使用正则表达式找到所有中文字符
        chinese_characters = pattern.findall(context)
        # 计算中文字符的总数
        chinese_count = sum(len(char) for char in chinese_characters)
        return chinese_count

    def characters(self, contexts: dict):
        '''
        统计出每一回的字数并且统计出每一卷的字数(汉字的字数)
        :param contexts: 字典: {第一卷: [{第一回: [txt], 第二回: [txt], ...}], ...}
        :return: (每一卷字数dict, 每一回字数dict)
        定义容器:
            temp_mix_total: 字典格式{'第1卷': {'第一回': count, ...}, ...}, 用于存放每一卷中的每一回的中文个数
            total: 字典格式, 用于存放每一卷的中文个数
            subtotal: 字典格式, 用于存放每一回的中文个数
            in_title_char_num: 列表格式, 存放每一回的字数
        '''
        temp_mix_total = {}
        total = {}
        subtotal = {}
        in_title_char_num = []

        for title, valueT in contexts.items():
            temp_mix_total[title] = []
            temp_sum = 0

            for subtxt in valueT:
                for subtitle, value in subtxt.items():
                    subtotal[subtitle] = self.character(value)
                    in_title_char_num.append(subtotal[subtitle])  # 只用于统计字数
                    temp_sum += subtotal[subtitle]
                    temp_mix_total[title].append({subtitle: f'{subtotal[subtitle]}字'})
            total[title] = temp_sum

        # print(total)
        # print(subtotal)
        return temp_mix_total, total, subtotal, in_title_char_num

    # 并行处理函数
    def parallel_cut(self, text: str) -> list:
        '''
        工具函数
        :param text: 需要处理的文本
        :return: 处理后的文本
        '''
        return list(pseg.cut(text))

    def analyzeOfFigure(self, context: str, top_n: int = 50) -> tuple:
        '''
        分析人物的出场次数，使用多进程来进行加速处理。
        :param context: 字符串格式
        :param top_n: 得到排名前N的人物数据
        :return: 排名前N的人物及次数(Format：[('name', frequency), ...]), 排名前N的人物列表。
        定义容器：
            init_name: 列表格式(list), 最初的混乱的名字。
            process_name: 字典格式({'name': frequency, 'name': frequency, ...}), 未剔除无关词语的字典。
        '''
        init_name = []
        process_name = {}

        # 得到cpu的进程个数
        num_processes = multiprocessing.cpu_count()
        # print(num_processes)
        # 将文本均分给每一个进程, 每个进程处理文本的长度 = (文本的长度 // 进程个数)
        chunk_size = len(context) // num_processes
        # 得到每个进程带处理的数据
        chunks = [context[i:i + chunk_size] for i in range(0, len(context), chunk_size)]
        # 创建进程池并行处理,定义进程池中进程数量
        pool = Pool(processes=num_processes)
        # 将函数与数据传入到进程池中
        results = pool.map(self.parallel_cut, chunks)
        # 关闭进程池
        pool.close()
        # 等待进程池中其他进程处理完毕
        pool.join()

        # 合并结果
        cut_words = sum(results, [])
        # 处理每个词的属性以及长度
        for word, flag in cut_words:
            if flag == 'nr' and len(word) > 1:
                init_name.append(word)
            # print('%s %s' % (word, flag))

        # 统计人名(别名)次数
        for name in init_name:
            if name in ['宝玉', '贾宝玉', '宝兄弟', '宝二爷', '问宝玉', '向宝玉', '那宝玉']:
                process_name['贾宝玉'] = process_name.get('贾宝玉', 0) + 1
            elif name in ['老太太', '贾母', '贾母笑', '老祖宗', '贾母因', '贾母王']:
                process_name['贾母'] = process_name.get('贾母', 0) + 1
            elif name in ['黛玉', '林黛玉', '林姑娘', '林妹妹', '黛玉笑']:
                process_name['林黛玉'] = process_name.get('林黛玉', 0) + 1
            elif name in ['宝钗', '薛宝钗', '宝姐姐', '宝钗笑']:
                process_name['薛宝钗'] = process_name.get('薛宝钗', 0) + 1
            elif name in ['凤姐儿', '王熙凤', '凤丫头']:
                process_name['王熙凤'] = process_name.get('王熙凤', 0) + 1
            elif name in ['探春', '贾探春']:
                process_name['贾探春'] = process_name.get('贾探春', 0) + 1
            elif name in ['贾政', '贾政道', '贾政笑', '贾政又', '贾政听']:
                process_name['贾探春'] = process_name.get('贾探春', 0) + 1
            elif name in ['周瑞家', '周瑞媳妇']:
                process_name['周瑞媳妇'] = process_name.get('周瑞媳妇', 0) + 1
            elif name in ['惜春', '贾惜春', '惜春笑']:
                process_name['贾惜春'] = process_name.get('贾惜春', 0) + 1
            elif name in ['迎春', '贾迎春']:
                process_name['贾迎春'] = process_name.get('贾迎春', 0) + 1
            elif name in ['贾赦', '大老爷']:
                process_name['贾赦'] = process_name.get('贾赦', 0) + 1
            elif name in ['士隐', '甄士隐']:
                process_name['甄士隐'] = process_name.get('甄士隐', 0) + 1
            elif name in ['宝琴', '薛宝琴']:
                process_name['薛宝琴'] = process_name.get('薛宝琴', 0) + 1
            elif name in ['贾芸', '贾芸道', '贾芸笑', '贾芸来', '贾芸忙', '贾芸见']:
                process_name['贾芸'] = process_name.get('贾芸', 0) + 1
            elif name in ['巧姐', '巧姐儿', '巧宗儿']:
                process_name['贾巧'] = process_name.get('贾巧', 0) + 1
            elif name in ['贾雨村', '雨村']:
                process_name['贾雨村'] = process_name.get('贾雨村', 0) + 1
            elif name in ['北静王', '王爷']:
                process_name['北静王'] = process_name.get('北静王', 0) + 1
            elif name in ['尤氏', '尤氏笑']:
                process_name['尤氏'] = process_name.get('尤氏', 0) + 1
            else:
                process_name[name] = process_name.get(name, 0) + 1
        # 剔除人名
        cull_name = ['小丫头', '明白', '言语', '冷笑', '老婆子', '小姐', '那丫头', '那婆子', '祖宗', '安静', '平儿忙', '从小儿',
                     '老嬷嬷', '何曾', '孙子', '宁府', '贾府', '金陵']
        for cull in cull_name:
            if cull in list(process_name.keys()):
                del process_name[cull]

        # 对人名进行排序, 将字典转换为'[()]'形式
        items_name = list(process_name.items())
        # 按照人物出现的次数进行排序
        items_name.sort(key=lambda x: x[1], reverse=True)

        # 筛选出排名前N的人物：
        top_n_name_count = items_name[:top_n]
        # 找到前N名的名称列表
        top_n_name = [it[0] for it in top_n_name_count]
        # print(Top50_name)
        return top_n_name_count, top_n_name

    def preliminaryRelation(self, temp_relation: dict, newList) -> dict:
        '''
        返回初步的关系，方法是每一回中出现的人都有关系。
        :param temp_relation: 字典格式
        :param newList:  temp_relation的键构成的列表, 也就是存在关系的人物列表
        :return: 返回一个字典, 表示从一关系列表中提取出的可能存在的关系。
        '''
        relation_dict = {}
        for idx, fig in enumerate(temp_relation.keys()):
            relation_element_set = set()
            relation_element_set.update(newList[: idx] + newList[idx + 1:])  # 对键进行切片, 剔除掉自己的名字的其他名字构成集合
            # 不能直接使用get()方法, 原因是调用update方法得到的是方法的返回值None
            relation_dict.setdefault(newList[idx], set()).update(relation_element_set)
        return relation_dict

    def preciseRelation(self, messy_relation: list, figure: list, percent: float = 0.3) -> dict:
        '''
        返回较为精确的关系, 方法:
            每一个回都有一个人物关系(在figure列表中), 如果某两个人物之间的关系连续在多个回出现(回的次数可以自定义, 默认：50), 就判定为这两个人物之间存在关系。
        :param messy_relation: 列表集合格式([{}, {}, ....]), 每一回可能存在的人物关系, 变量名字的意思时混乱的关系。
        :param figure: 列表格式([['name1', 'name2', ...], ...])所有段落的人物关系。
        :param percent: (0.0 - 1.0)之间的浮点数, 表示百分数, 是一个衡量标准, 如果关系的次数占总段落的比率 >= 该百分数, 则认定为有关系。
        :return: 字典格式({'name': ['other_name', ...], ...}), 每一个人与其他人之间的联系。
        '''
        relaton = {}
        _max_len = len(messy_relation)      # 得到所段落的个数
        stand_num = percent * _max_len      # 计算标准
        # print(messy_relation)
        for idx, fig in enumerate(figure):
            for pre_fig in figure:
                if pre_fig == figure[idx]:      # 跳过本身名字继续寻找下一个可能存在关系的名字
                    continue
                else:
                    count = 0                   # 计数, 如果该关系超过了设定的次数就表示存在这个关系
                    for mess in messy_relation:
                        if {fig, pre_fig}.issubset(mess):       # 判断是否是mess的子集，也可使用<=来表示子集关系
                            count += 1
                            if count >= stand_num:
                                # 存在该关系, 就将这个关系添加到字典中, 双向添加, 字典的值是一个集合
                                relaton.setdefault(fig, set()).add(fig)
                                relaton.setdefault(pre_fig, set()).add(fig)
                                break  # 结束内层的循环
        # print(relaton)
        return relaton

    def toFindAllRelationAtOneParagraph(self, sentence: str, figure: list) -> dict:
        '''
        该函数用于找到一回中出现的所有人物,以及出现的次数
        :param sentence: 字符串格式(str), 每一回的文本。
        :param figure: 排名前N的人物列表(list)。
        :return: 字典格式({'name': frequency, ...})
        '''
        result = {}
        for fig in figure:
            count = sentence.count(fig)
            if count > 0:
                result[fig] = count
        return result

    def toFindSpecificRelationMain(self, persent=0.1) -> tuple:
        '''
        :return: 排名前n的人物及出场次数, 排名前n的人物关系。
        relation_dict: 字典格式({'name': {'name1', 'name2', ...}, ...}), 表示所有可能的人物关系, 非精确类型。
        '''
        assert 0 <= persent <= 1, "关系段落占比不能大于1或者小于0"
        # 找到所有段落
        wholeTxt, _, _, paragraphList, _ = self.ReadFileOfTxt(self.path)
        top_n_name_count, top_n_name = self.analyzeOfFigure(wholeTxt)
        messy_relation = []
        relation_dict = {}
        # 从'回列表'中遍历每一回的文本通过toFindAllRelation函数寻找所有可能的关系。
        for paragraph_txt in paragraphList:
            temp_relation = self.toFindAllRelationAtOneParagraph(paragraph_txt[0], top_n_name)
            # 构建关系表,键为每一个人物名称，值为一个关系集合, 由于我们只要得到人名之间的关系, 所以我们对字典的键进行处理。
            newList = list(temp_relation.keys())  # 先将字典的键转换为列表, 以便使用。
            temp_set = set()  # 临时变量, 用于将列表存储为列表形式
            temp_set.update(newList)
            messy_relation.append(newList)  # 将所有可能存在的关系构成集合添加到混乱列表中, 构成二维列表.

            relation_dict_element = self.preliminaryRelation(temp_relation=temp_relation, newList=newList)
            relation_dict.update(relation_dict_element)
        # print(len(relation_dict))
        relations = self.preciseRelation(messy_relation, top_n_name, percent=persent)     # 得到更为精确的关系
        # print(len(relations))
        return top_n_name_count, relations

    def getTop_N_Figure(self, N: int) -> dict:
        '''
        得到排名前N的人物的数据
        :param: 前N名
        :return: 前N名的人物及数量, 前N名的人物名称
        '''
        wholeTxt = self.ReadFileOfTxt(self.path)[0]
        return self.analyzeOfFigure(wholeTxt, top_n=N)[0]

    def getMixTotal(self) -> dict:
        '''
        得到每一卷的每一回的字数
        :return: 返回一个字典格式
        '''
        wholeTxt, dictContxt,  = self.ReadFileOfTxt(self.path)[0: 2]
        temp_mix_total = self.characters(dictContxt)[0]
        # print(temp_mix_total)
        return temp_mix_total

    def getTotal(self) -> dict:
        '''
        得到每一卷的中文个数
        :return: 字典格式
        '''
        perfect_dict = self.ReadFileOfTxt(self.path)[1]
        total = self.characters(perfect_dict)[1]
        return total

    def getInTitleAndNums(self) -> tuple:
        '''
        得到每一回的标题以及数量
        :return: 每一回的标题列表, 每一回的标题及数量字典
        '''
        _, perfect_dict, intitleList, _, _ = self.ReadFileOfTxt(self.path)
        _, _, _, intitleNums = self.characters(perfect_dict)
        return intitleList, intitleNums

    def getRollTopN(self, num: int = 10) -> [[[str, int]]]:
        '''
        得到每一卷出排名前N的人物列表
        :param num: int类型, 表示选取排名前N
        :return: 返回一个列表, 列表中存放排名前N人名
        定义容器：
            top_n_roll_total_list: 三维列表形式[[['name', count], ...]], 提取出每一卷的前N名人物
        '''
        rollTxtList = self.ReadFileOfTxt(self.path)[-1]
        top_n_roll_total_list = []

        for roll in rollTxtList:
            top_n_name_and_count, _ = self.analyzeOfFigure(roll, top_n=50)     # 提取出每一卷文本的前top_n名
            # 将Top50_name_and_count的元素转换为列表
            top_n_name_and_count = [[n, c] for n, c in top_n_name_and_count]
            # 截取每一卷的前N名
            top_n_name_and_count = top_n_name_and_count[: num + 1]
            top_n_roll_total_list.append(top_n_name_and_count)      # 将每一卷的前N名添加到总列表中
        # print(top_n_roll_total_list)
        return top_n_roll_total_list

    def main(self, top_n=50, num=10) -> tuple:
        '''
        主函数, 得到所有的数据
        :return: top_n_name_count, relations, top_n_name_count_T, temp_mix_total, total, intitleList, intitleNums, top_n_roll_total_list
        '''
        top_n = 50
        num = 10
        top_n_name_count, relations = self.toFindSpecificRelationMain()  # --
        top_n_name_count_T = self.getTop_N_Figure(N=top_n) # --
        temp_mix_total = self.getMixTotal()  # --
        total = self.getTotal()   # --
        intitleList, intitleNums = self.getInTitleAndNums()  # --
        top_n_roll_total_list = self.getRollTopN(num=num)  # --
        return top_n_name_count, relations, top_n_name_count_T, temp_mix_total, total, intitleList, intitleNums, top_n_roll_total_list


if __name__ == '__main__':
    # analyzeDream().main()
    path = analyzeDream().path
    An = analyzeDream()
    # top_n_name_count_T = An.getTop_N_Figure(N=50)
    top_n_name_count, relations = An.toFindSpecificRelationMain()  # --
    print(top_n_name_count)
    print(relations)

