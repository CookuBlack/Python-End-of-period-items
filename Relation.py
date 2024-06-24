from pyecharts import options as opts
from pyecharts.charts import Graph
from DataProcessing import analyzeDream


if __name__ == '__main__':

    relation_count, relation = analyzeDream().toFindSpecificRelationMain()
    _min = min([v for k, v in relation_count])
    _max = max([v for k, v in relation_count])
    # print(relation_count)
    # 构造nodes数据, 将数值缩放到0 - 100之间，使用最大最小归一化算法
    def normalizationMaxAndMin(value: int) -> int:
        return ((value - _min) / (_max - _min)) * 100
    nodes = [
        {'name': k, 'symbolSize': normalizationMaxAndMin(v) if normalizationMaxAndMin(v) > 10 else 10} for k, v in relation_count
    ]
    # print(nodes)
    # 构造link数组
    # print(relation)
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

    c = (
        Graph()
        .add(series_name="",
             nodes=nodes,
             links=links,
             repulsion=8000,
             itemstyle_opts=opts.ItemStyleOpts(color="#7e6bc4"),  # 节点颜色
             linestyle_opts=opts.LineStyleOpts(color="#d6c8ff"),  # 边颜色
             )
        .set_global_opts(title_opts=opts.TitleOpts(title="人物关系图"))
        .render("Chart/Relation.html")
    )