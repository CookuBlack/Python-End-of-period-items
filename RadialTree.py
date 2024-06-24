from pyecharts import options as opts
from pyecharts.charts import Tree
from DataProcessing import analyzeDream
# from pyecharts.globals import ThemeType

if __name__ == '__main__':
    total_character_dict = analyzeDream().getMixTotal()
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
    # print(tls1)
    # print(len(tls1))
    data = {'name': '红楼梦', 'children': outlist}
    print(data)

    # # 创建一个初始化配置对象，设置画布大小
    # init_opts = opts.InitOpts(width="100%", height="100%", theme=ThemeType.LIGHT)
    c = (
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
            .render("Chart/RadiaTree.html")
        )

