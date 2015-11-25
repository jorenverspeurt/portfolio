#!/bin/env python2
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors

arg = sys.argv[1]
f = open(arg,'r')
experiment = json.loads(f.read())
f.close()
#
opacity = 0.7
lighten = 0.3
#
for title in experiment["titles"].iterkeys():
    nr_quest = len(experiment[title].keys())
    nr_probs = len(experiment[title].itervalues().next().keys())
    prob_ind = np.arange(nr_probs)
    spectral = cm.ScalarMappable(norm=colors.Normalize(vmin=-1,
            vmax=nr_quest), cmap='spectral')
    bar_width = 1.0/(nr_quest+1)
    for quest_i, question in enumerate(sorted(experiment[title].iterkeys())):
        for prob_i, probability in enumerate(
                sorted(experiment[title][question].iterkeys())):
            if prob_i == 0:
                label = question
            else:
                label = '_nolegend_'
            plt.bar(prob_i + quest_i*bar_width,
                    experiment[title][question][probability],
                    bar_width,
                    alpha=opacity - prob_i%2 * lighten,
                    color=spectral.to_rgba(quest_i),
                    label=label)
    plt.xlabel(experiment["xlabels"][title])
    plt.ylabel(experiment["ylabels"][title])
    plt.title(experiment["titles"][title])
    plt.xticks(prob_ind + bar_width * nr_quest / 2,
               sorted(experiment[title].itervalues().next().keys()),
               rotation = 30, fontsize = 7)
    plt.legend(loc='upper center',prop={'size' : 10},ncol=4)
    plt.savefig('plot-'+title+'.png')
    plt.clf()

