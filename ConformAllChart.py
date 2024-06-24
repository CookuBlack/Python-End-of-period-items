import random
from pyecharts import options as opts
from pyecharts.charts import Bar, Grid, Line, Page, Pie, WordCloud, Tree, Graph, Timeline
from pyecharts.faker import Faker
from pyecharts.globals import SymbolType
from DataProcessing import analyzeDream


def WordCloudChart(top_n_name_count_T) -> WordCloud:
    words = top_n_name_count_T
    wordCloud = (
        WordCloud()
        .add("", words, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
        .set_global_opts(title_opts=opts.TitleOpts(title="红楼梦人物词云图"))
    )
    return wordCloud


def BarLineChart(title, nums_diff, nums, context: str) -> Bar:
    bar = (
        Bar()
        .add_xaxis(title)
        .add_yaxis(
            "章节",
            nums,
            yaxis_index=0,
            color="#d14a61",
        )
        .add_yaxis(
            "章节字数差值（前）",
            nums_diff,
            yaxis_index=1,
            color="#5793f3",
        )
        .extend_axis(
            yaxis=opts.AxisOpts(
                name="字数",
                type_="value",
                min_=0,
                max_=10000,
                position="left",
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#d14a61")
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value} 字"),
            )
        )
        .set_global_opts(
            yaxis_opts=opts.AxisOpts(
                name="字数标准",
                min_=0,
                max_=10000,
                position="right",
                offset=80,
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#5793f3")
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value} 字"),
            ),
            title_opts=opts.TitleOpts(title=context),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        )
    )

    line = (
        Line()
        .add_xaxis(title)
        .add_yaxis(
            "向上取整字数",
            [(round(i / 1000 + 0.5)) * 1000 for i in nums],
            yaxis_index=0,  # 确保这个索引与 Bar 图中的一个 Y 轴索引匹配
            color="#675bba",
            label_opts=opts.LabelOpts(is_show=False),  # 显示标签
        )
    )

    bar.overlap(line)
    grid = Grid()
    grid.add(bar, opts.GridOpts(pos_left="10%", pos_right="20%"), is_control_axis_index=False)
    return grid


def RadialTreeChart(data) -> Tree:
    data = data

    # 创建一个初始化配置对象，设置画布大小
    # init_opts = opts.InitOpts(width="100%", height="100%", theme=ThemeType.LIGHT)
    radialTree = (
        Tree()
        .add(
            series_name="",
            data=[data],
            pos_left="20%",  # 左侧距离
            pos_right="10%",  # 右侧距离
            pos_top="16%",
            pos_bottom="16%",
            layout="radial",
            symbol="emptyCircle",
            symbol_size=8,
        )
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(trigger="item", trigger_on="mousemove")
        )
    )
    return radialTree


def PieChart(total) -> Pie:
    data = total
    pie = (
        Pie()
        .add(
            "",
            [list(z) for z in zip(data.keys(), data.values())],
            radius=["40%", "55%"],
            label_opts=opts.LabelOpts(
                position="outside",
                formatter="{a|{a}}{abg|}\n{hr|}\n {b|{b}: }{c}  {per|{d}%}  ",
                background_color="#eee",
                border_color="#aaa",
                border_width=1,
                border_radius=4,
                rich={
                    "a": {"color": "#999", "lineHeight": 22, "align": "center"},
                    "abg": {
                        "backgroundColor": "#e3e3e3",
                        "width": "100%",
                        "align": "right",
                        "height": 22,
                        "borderRadius": [4, 4, 0, 0],
                    },
                    "hr": {
                        "borderColor": "#aaa",
                        "width": "100%",
                        "borderWidth": 0.5,
                        "height": 0,
                    },
                    "b": {"fontSize": 16, "lineHeight": 33},
                    "per": {
                        "color": "#eee",
                        "backgroundColor": "#334455",
                        "padding": [2, 4],
                        "borderRadius": 2,
                    },
                },
            ),
        )
        .set_global_opts(title_opts=opts.TitleOpts(title="红楼梦卷字数"))
    )
    return pie


def GraphChart(nodes, links) -> Graph:
    graph = (
        Graph()
        .add(series_name="",
             nodes=nodes,
             links=links,
             repulsion=8000,
             itemstyle_opts=opts.ItemStyleOpts(color="#7e6bc4"),  # 节点颜色
             linestyle_opts=opts.LineStyleOpts(color="#d6c8ff"),  # 边颜色
             )
        .set_global_opts(title_opts=opts.TitleOpts(title="人物关系图"))
    )
    return graph


def TimeLineChart(top_n_roll_total_list, num=10) -> Timeline:
    '''
    得到TimeLine表的数据
    :param top_n_roll_total_list: 每一卷的字数
    :return:
    '''
    data = top_n_roll_total_list
    # 构造每一卷的标题
    titles = ['一', '二', '三']
    attr = Faker.choose()
    tl = Timeline()

    print([list(z) for z in zip(attr, Faker.values())])
    for idx, title in enumerate(titles):
        pie = (
            Pie()
            .add(
                f"Top{num}",
                # [list(z) for z in zip(attr, Faker.values())],
                data[idx],
                rosetype="radius",
                radius=["30%", "55%"],
            )
            .set_global_opts(title_opts=opts.TitleOpts("第{}卷的Top{}".format(title, num)))
        )
        tl.add(pie, "第{}卷".format(title))
    return tl


def getAllData(top_n=50, num=10) -> tuple:
    '''
    从DataProcess文件中得到所有的相关的数据。
    :return: 元组类型，包含了与可视化相关的所有数据。
    '''
    all_data = analyzeDream().main(top_n=top_n, num=num)
    return all_data


def graphDataDispose(top_n_name_count, relations) -> tuple:
    relation_count, relation = top_n_name_count, relations
    _min = min([v for k, v in relation_count])
    _max = max([v for k, v in relation_count])

    # print(relation_count)
    # 构造nodes数据, 将数值缩放到0 - 100之间，使用最大最小归一化算法
    def normalizationMaxAndMin(value: int) -> int:
        return ((value - _min) / (_max - _min)) * 100

    nodes = [
        {'name': k, 'symbolSize': normalizationMaxAndMin(v) if normalizationMaxAndMin(v) > 10 else 10} for k, v in
        relation_count
    ]
    # 构造links数组
    links = []
    for k, v in relation.items():
        for fig in v:
            temp_dict = dict()
            temp_dict['source'] = k
            temp_dict['target'] = fig
            # print(temp_dict)
            links.append(temp_dict)
            del temp_dict
    # print(links)
    return nodes, links


def TreeDataDispose(temp_mix_total) -> {}:
    '''
    构造树形图的数据
    :param temp_mix_total: 输入字典类型的混合有卷、回、文本的数据。
    :return: 字典类型的数据
    '''
    total_character_dict = temp_mix_total
    # 从内向外构建
    outlist = []
    for title, value in total_character_dict.items():
        inlist = []
        for v in value:
            td = [{'name': v[t], 'children': 1} for t in v.keys()]
            data1 = [{'name': t, 'children': td} for t in v.keys()]
            inlist.extend(data1)
        data2 = [{'name': title, 'children': inlist}]
        outlist.extend(data2)
    data = {'name': '红楼梦', 'children': outlist}
    return data


def barLineDataDispose(intitleList, intitleNums, count: int = 50, flag: str = 'R'):
    '''
    :param intitleList:
    :param intitleNums:
    :param count: 选取的个数
    :param flag: R:随机选取, O: 按排名进行选取
    :return:
    '''
    count = count
    temp_title, nums = intitleList, intitleNums
    title = []
    context = ''
    # 处理title的分号
    for tit in temp_title:
        if tit == '\t':
            continue
        title.append(tit)

    if flag == "R":
        rand_number = random.sample(range(0, 120), count)
        # print(rand_number)
        title = [title[i] for i in rand_number]
        nums = [nums[i] for i in rand_number]
        context = f'随机选取{count}章节字数展示'
    else:
        # 直接选取前count个数
        title = title[: count]
        nums = nums[: count]
        context = f'按顺序选取{count}章节字数展示'

    # 计算选取的相邻段落的差值赋给变量nums_diff
    nums_diff = [nums[i] - nums[i - 1] for i in range(1, len(nums))]
    nums_diff = [nums[0]] + nums_diff
    # print(max(nums))  # --> 9833
    # print(nums)
    return title, nums_diff, nums, context


def page_simple_layout(top_n_name_count_T,
                       temp_mix_total,
                       total,
                       top_n_roll_total_list,
                       title,
                       nums_diff,
                       nums,
                       nodes,
                       links,
                       data,
                       context) -> None:
    '''
    将所有图表绘制在一张网页上
    :param top_n_name_count_T:
    :param temp_mix_total:
    :param total:
    :param top_n_roll_total_list:
    :param title:
    :param nums_diff:
    :param nums:
    :param nodes:
    :param links:
    :param data:
    :param context:
    :return: None
    '''
    page = Page(layout=Page.SimplePageLayout)
    page.add(
        WordCloudChart(top_n_name_count_T),
        BarLineChart(title, nums_diff, nums, context),
        RadialTreeChart(data),
        PieChart(total),
        GraphChart(nodes, links),
        TimeLineChart(top_n_roll_total_list),
    )
    page.render("Chart/ConformAllChart.html")


if __name__ == "__main__":
    # page_simple_layout()
    top_n = 50
    num = 10
    top_n_name_count, relations, top_n_name_count_T, temp_mix_total, total, intitleList, intitleNums, top_n_roll_total_list = getAllData(top_n=top_n, num=num)
    title, nums_diff, nums, context = barLineDataDispose(intitleList, intitleNums, count=50, flag='R')
    nodes, links = graphDataDispose(top_n_name_count, relations)
    data = TreeDataDispose(temp_mix_total)
    page_simple_layout(top_n_name_count_T, temp_mix_total, total, top_n_roll_total_list, title, nums_diff, nums, nodes,
                       links, data, context)
