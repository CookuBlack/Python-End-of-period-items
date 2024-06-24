from pyecharts import options as opts
from pyecharts.charts import Pie, Timeline
from pyecharts.faker import Faker
from DataProcessing import analyzeDream

if __name__ == '__main__':
    num = 10
    data = analyzeDream().getRollTopN(num=num)
    print(data)
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
    # tl.render(f"Chart/{'timeline_pie'.upper()}.html")
    tl.render(f"Chart/TimeLine.html")
