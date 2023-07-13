import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import seaborn as sns
import numbers
import pandas as pd


def lmplot(
        data,
        title=None,
        fig_size=(10, 10),
        annotate_correlation_coef=True,
        annotate_correlation_pos=(0.1, 1.0),
):
    xy_labels = list(data.keys())

    assert len(xy_labels) == 2

    if isinstance(fig_size, numbers.Number):
        fig_size = (fig_size, fig_size)

    plt.figure(figsize=fig_size)

    g = sns.lmplot(data=pd.DataFrame(data, columns=xy_labels), x=xy_labels[0], y=xy_labels[1])
    if title is not None:
        g.fig.subplots_adjust(top=.90)
        # g.ax.set_title(title, y=1.05)
        plt.title(title, pad=15.0 if annotate_correlation_coef else 0)

    if annotate_correlation_coef:
        r, p = stats.pearsonr(x=data[xy_labels[0]], y=data[xy_labels[1]])
        plt.annotate('r = {r:.2f}, p = {p:.3e}'.format(r=r, p=p), xy=annotate_correlation_pos, xycoords='axes fraction')

    plt.show()

def boxplot(
        data,
        title=None,
        fig_size=(10, 10),
        y_label=None,
        line_width=2.0
):
    if isinstance(fig_size, numbers.Number):
        fig_size = (fig_size, fig_size)

    plt.figure(figsize=fig_size)

    labels = list(data.keys())

    g = sns.boxplot(
        data=pd.DataFrame(data, columns=labels),
        linewidth=line_width
    )

    if y_label is not None:
        g.set_ylabel(y_label)

    if title is not None:
        plt.title(
            title,
            # fontdict={
            #     'fontsize': 32
            # }
        )

    plt.show()

if __name__ == "__main__":
    x = np.random.randn(100)
    y = np.random.randn(100)

    lmplot(
        data={'xx': x, 'yy': y},
        title="Nice title here",
        annotate_correlation_coef=True
    )

    boxplot(
        data={'xx': x, 'yy': y},
        title="Awesome boxplot",
        y_label="Metric",
        fig_size=(20,10)
    )
