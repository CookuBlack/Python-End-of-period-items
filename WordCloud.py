from pyecharts import options as opts
from pyecharts.charts import WordCloud
from pyecharts.globals import SymbolType
from DataProcessing import analyzeDream


if __name__ == '__main__':
    words = analyzeDream().getTop_N_Figure(N=50)
    wordCloud = (
        WordCloud()
        .add("", words, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
        .set_global_opts(title_opts=opts.TitleOpts(title="DreamOfRed"))
        .render("Chart/WordCloud.html")
    )
