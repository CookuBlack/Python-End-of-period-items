import random

from pyecharts import options as opts
from pyecharts.charts import Bar, Grid, Line
from DataProcessing import analyzeDream

temp_title, nums = analyzeDream().getInTitleAndNums()
title = []
# 处理title的分号
for tit in temp_title:
    if tit == '\t':
        continue
    title.append(tit)
count = 50
if True:
    rand_number = random.sample(range(0, 120), count)
    # print(rand_number)
    title = [title[i] for i in rand_number]
    nums = [nums[i] for i in rand_number]
# 直接选取前count个数, 自己修改
if 1 < 0:
    title = title[: count]
    nums = nums[: count]

# 计算差值nums_diff
nums_diff = [nums[i] - nums[i - 1] for i in range(1, len(nums))]
nums_diff = [nums[0]] + nums_diff
# print(nums_diff)
# print(len(nums_diff))
# 计算奇数章节与偶数章节, 按需求使用
if 0 > 1:
    title_odd = title[0: -1: 2]
    title_even = title_odd[1: -1: 2]
    nums_odd = nums[0: -1: 2]  # 奇数章节
    nums_even = nums[1: -1: 2]
# print(max(nums))  # --> 9833
# print(nums)
if __name__ == '__main__':
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
            title_opts=opts.TitleOpts(title="随机选取50章节字数展示"),
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
    grid.render("Chart/BarLine.html")
