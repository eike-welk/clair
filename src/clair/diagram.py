# -*- coding: utf-8 -*-
###############################################################################
#    Clair - Project to discover prices on e-commerce sites.                  #
#                                                                             #
#    Copyright (C) 2013 by Eike Welk                                          #
#    eike.welk@gmx.net                                                        #
#                                                                             #
#    License: GPL Version 3                                                   #
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
###############################################################################
"""
Library for creating diagrams.
"""

from __future__ import division
from __future__ import absolute_import              

from itertools import cycle
from collections import namedtuple
import random

import numpy as np
import pandas as pd
import matplotlib
from matplotlib.colors import colorConverter, rgb_to_hsv, hsv_to_rgb

from clair.coredata import Record



class Filter(Record):
    """
    Base class of filters to select interesting rows (listings or prices) 
    from a (moderately sized) ``DataFrame``. They are useful for creating
    diagrams.
    
    Inherits from record, to get its ``__repr__``. To be consistent, all
    data attributes of ``Filter`` subclasses should be arguments of 
    ``__init__``.
    """
    def filter(self, in_frame):
        """
        Select the interesting rows from the input ``DataFrame``.
        
        Returns ``DataFrame`` that only contains the interesting rows.
        """
        raise NotImplementedError()
    
    

class FilterInterval(Filter):
    """
    Select rows in a ``DataFrame`` if they are inside of outside of a
    half open interval.
    
    Parameters
    ----------
    column : basestring
        The column at which the filter will look. This columns must contain
        *number like* objects, that can be compared against ``intv_start``
        and ``intv_stop``.
    intv_start : number like, for example: ``float``, ``datetime.datetime``.
        Start of interval.
    intv_stop : number like
        End of interval.
    inside : bool
        If ``True`` select rows where the value of ``column`` lies inside the 
        interval. (``intv_start <= column < intv_stop``)
        
        If ``False`` select rows that are outside of the interval.
    """
    def __init__(self, column, intv_start, intv_stop, inside=True):
        super(FilterInterval, self).__init__()
        assert isinstance(column, basestring), \
               "Column name must be string or unicode."
        assert isinstance(inside, bool), \
               "Parameter ``inside`` must be ``bool``."
        msg_bounds = "Start and stop of the interval must be similar " \
                     "to numbers, and have comparison operators."
        assert hasattr(intv_start, "__lt__") or \
               hasattr(intv_start, "__cmp__"), msg_bounds
        assert hasattr(intv_stop, "__lt__") or \
               hasattr(intv_stop, "__cmp__"), msg_bounds
        self.column = column
        self.intv_start = intv_start
        self.intv_stop = intv_stop
        self.inside = inside

    def filter(self, in_frame):
        """
        Select the interesting rows from the input ``DataFrame``.
        
        Returns ``DataFrame`` that only contains the interesting rows.
        """
        assert isinstance(in_frame, pd.DataFrame)
        col = in_frame[self.column]
        if self.inside:
            where = (col >= self.intv_start) & (col < self.intv_stop)
        else:
            where = (col < self.intv_start) | (col >= self.intv_stop)
            
        res_rows = in_frame.ix[where]
        return res_rows
    


class FilterContains(Filter):
    """
    Select rows in a ``DataFrame`` if a field contains a certain string.
    """
    def __init__(self, column, search_word, is_string=False):
        super(FilterContains, self).__init__()
        assert isinstance(column, basestring), \
               "Column name must be string or unicode."
        assert isinstance(search_word, basestring), \
               "Parameter ``search_word`` name must be string or unicode."
        assert isinstance(is_string, bool), \
               "Parameter ``is_string`` must be ``bool``."
        self.column = column
        self.search_word = search_word
        self.is_string = is_string
        
    def filter(self, in_frame):
        """
        Select the interesting rows from the input ``DataFrame``.
        
        Returns ``DataFrame`` that only contains the interesting rows.
        """
        assert isinstance(in_frame, pd.DataFrame)
        
        col = in_frame[self.column]
        if self.is_string:
            #Do a string search for the search word.
            where = col.str.contains(self.search_word, na=False)
        else:
            #Consider  elements of col to be containers (eg. list, set) or None.
            #Test if search word is in container.
            isnull = col.isnull()
            where = np.zeros((len(col),), dtype=bool)
            for i in range(len(col)):
                if isnull[i]:
                    continue
                if self.search_word in col.iget(i):
                    where[i] = True
        
        res_rows = in_frame.ix[where]
        return res_rows



def rgb_to_hsv_tuple(rgb_tuple):
    """
    Convert 3 tuple that represents a RGB color (values between 0..1) 
    to a 3 tuple in HSV color space.
    If you have an array of color values use: ``matplotlib.colors.rgb_to_hsv``.
    """ 
    colarr = rgb_to_hsv(np.array([[rgb_tuple]]))
    return tuple(colarr[0, 0, :])
    
def hsv_to_rgb_tuple(hsv_tuple):
    """
    Convert 3 tuple that represents a HSV color 
    to a 3 tuple in RGB color space (values between 0..1).
    If you have an array of color values use: ``matplotlib.colors.hsv_to_rgb``.
    """ 
    colarr = hsv_to_rgb(np.array([[hsv_tuple]]))
    return tuple(colarr[0, 0, :])



#Meta data about each plot. used for identifying data in pick events
PlotResult = namedtuple("PlotResult", "gid, data_ids, artist")


class PlotterLine(object):
    """
    Plot a line of Y,X values; and optionally a symmetrical 
    confidence band.
    
    Various options can be set in the constructor. The X,Y values are 
    given in the ``plot`` method. 
    
    The confidence band is intended to show the standard deviation. It can be
    shown as a pale, semitransparent area, or as thin additional lines 
    above and below the line.
    
    TODO: Multiple parallel confidence lines or areas; for sigma, 2*sigma;
          or for fancy week/month histograms.
    """
    def __init__(self, label=None,
                 linewidth=2, linestyle='solid', 
                 marker="o", markersize=10,
                 color="blue", saturation=1, opaqcity=1, zorder=0,
                 fill_limits=True, lim_opaqcity=0.2, lim_zorder=-100):
        self.label = label
        
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.marker = marker
        self.markersize = markersize
        
        self.color_rgb = colorConverter.to_rgb(color)
        self.saturation = saturation
        self.opaqcity = opaqcity
        self.zorder = zorder
        
        self.fill_limits = fill_limits
        self.lim_opaqcity = lim_opaqcity
        self.lim_zorder = lim_zorder
    
    
    def plot(self, axes, xvals, yvals, limits=None, data_ids=None):
        """Plot the graph into a ``matplotlib.axes.Axes`` instance."""
#        #Plotting length 0 lines has sometimes undesirable effects on scaling 
#        if len(xvals) == 0:
#            return
        
        #Compute correct RGBA color.
        h, _s, v = rgb_to_hsv_tuple(self.color_rgb)
        color_rgb = hsv_to_rgb_tuple((h, self.saturation, v))
        color_rgba = color_rgb + (self.opaqcity,)
        
        #ID for graphical element, to recognize it in picking events
        gid = "{c}-{m}-{l}-{r}".format(c=self.color_rgb, m=self.marker, 
                                       l=self.label, r=random.randint(0, 9999))
        
        #Plot line
        line = axes.plot(xvals, yvals, label=self.label,
                         color=color_rgba, linestyle=self.linestyle, 
                         linewidth=self.linewidth,
                         marker=self.marker, markerfacecolor=color_rgba, 
                         markersize=self.markersize, zorder=self.zorder,
                         picker=True, gid=gid)
        
        #Plot limits if desired.
        if limits is not None and self.fill_limits:
            #Plot limits as filled area
            axes.fill_between(xvals, yvals + limits, yvals - limits, 
                              color=color_rgb, alpha=self.lim_opaqcity,
                              zorder=self.lim_zorder)
        elif limits is not None:
            #Plot limits as thin lines.
            axes.plot(xvals, yvals + limits, 
                      xvals, yvals - limits, 
                      color=color_rgba, linestyle="solid", linewidth=1, 
                      marker=None, zorder=self.lim_zorder)
        
        return PlotResult(gid=gid, data_ids=np.array(data_ids, dtype=unicode), 
                          artist=line)



class PlotterScatter(object):
    """
    Create a scatter plot of Y,X values.
    
    Various options can be set in the constructor. The X,Y values are 
    given in the ``plot`` method.
    """
    def __init__(self, label=None, marker="o", markersize=10,
                 color="blue", saturation=1, opaqcity=1, zorder=0):
        self.label = label
        self.marker = marker
        self.markersize = markersize
        self.color_rgb = colorConverter.to_rgb(color)
        self.saturation = saturation
        self.opaqcity = opaqcity
        self.zorder = zorder
    
    
    def plot(self, axes, xvals, yvals, data_ids=None):
        """Plot the graph into a ``matplotlib.axes.Axes`` instance."""
#        #Plotting length 0 lines has sometimes undesirable effects on scaling 
#        if len(xvals) == 0:
#            return
        
        #Compute correct RGBA color.
        h, _s, v = rgb_to_hsv_tuple(self.color_rgb)
        color_rgb = hsv_to_rgb_tuple((h, self.saturation, v))
        color_rgba = color_rgb + (self.opaqcity,)
        
        #ID for graphical element, to recognize it in picking events
        gid = "{c}-{m}-{l}-{r}".format(c=self.color_rgb, m=self.marker, 
                                       l=self.label, r=random.randint(0, 9999))
        
        #Create scatter plot
        graph = axes.scatter(xvals, yvals, s=self.markersize**2, 
                             c=color_rgba, marker=self.marker,
                             label=self.label, zorder=self.zorder,
                             picker=True, gid=gid)
        
        return PlotResult(gid=gid, data_ids=np.array(data_ids, dtype=unicode), 
                          artist=graph)



class PlotterPriceSingle(object):
    """
    Complex plot that shows prices of one product versus time.
    
    The features (all optional) are:
    
    * The average or median price is shown by a thick line. Different 
      algorithms can be configured for choice of averaging interval, and 
      data source for averaging.
      
    * Thin lines or semi-transparent areas show the standard deviation.
      Same options as for computation of average.
      
    * Scatter plots for single prices. Different symbols or colors for 
      different types of prices. The types are:
      * Average or median prices: small symbol, saturated color, line(s).
      * Observed prices (sales of a single item): large symbol, saturated
        color, scatter plot.
      * Estimated prices (sales of multiple items): small symbol, saturated 
        color, scatter plot.
      * Listings that were not sold: small symbol, pale color
      * Guessed price by human: large symbol, pale color, special symbol.
      
    * Small, 90° turned histograms of prices. Options for choice of interval
      and data source (which prices to include). (Maybe use candle diagram
      instead.) Pale or semi-transparent color.
      
    * Separate graph for number of items traded, or total amount of money 
      payed. Same interval as.
      
    TODO: Compute average or median from data.  
    TODO: Compute standard deviation.
    TODO: Optionally compute average from "observed", or all sold prices.
    TODO: Generalize: 
          * Use a ``Filter`` instance to select the prices for each 
            component of the plot.
          * Use an attribute ``column_name`` to select the column from which 
            the prices are taken. 
    """
    def __init__(self, color="blue", marker = "o",
                 show_average=True, show_observed=True, show_estimated=True, 
                 show_notsold=True, show_guessed=True):
        self.color = color
        self.marker = marker
        self.show_average = show_average
        self.show_observed = show_observed
        self.show_estimated = show_estimated
        self.show_notsold = show_notsold
        self.show_guessed = show_guessed
        
        #Store the plotters for the components of the graph. 
        self.graph_average = PlotterLine(
                    markersize=7,  opaqcity=1.0, label="average", 
                    color=color, marker=marker, linewidth=2)
        self.graph_observed = PlotterScatter(
                    markersize=12, opaqcity=1.0, label="observed", 
                    color=color, marker=marker)
        self.graph_estimated = PlotterScatter(
                    markersize=7,  opaqcity=1.0, label="estimated", 
                    color=color, marker=marker)
        self.graph_notsold = PlotterScatter(
                    markersize=7,  opaqcity=0.4, label="not sold", 
                    color=color, marker=marker)
        self.graph_guessed = PlotterScatter(
                    markersize=12, opaqcity=0.4, label="guessed", 
                    color=color, marker=marker)
    
    
    def plot(self, axes, prices):
        """
        Plot the diagram into a ``matplotlib.axes.Axes`` instance,
        for example into a subplot.
        """
        assert isinstance(axes, matplotlib.axes.Axes)
        
        avg_res, obs_res, est_res, not_res, guess_res = [None] * 5
        
        if self.show_average:
            avg_prices = prices[prices["type"] == "average"]
            avg_res = self.graph_average.plot(axes, avg_prices["time"], 
                                              avg_prices["price"],
                                              data_ids=list(avg_prices["id"]))
        
        if self.show_observed:
            obs_prices = prices[prices["type"] == "observed"]
            obs_res = self.graph_observed.plot(axes, obs_prices["time"], 
                                               obs_prices["price"],
                                               data_ids=obs_prices["id"])
        
        if self.show_estimated:
            est_prices = prices[prices["type"] == "estimated"]
            est_res = self.graph_estimated.plot(axes, est_prices["time"], 
                                                est_prices["price"],
                                                data_ids=est_prices["id"])
        
        if self.show_notsold:
            not_prices = prices[prices["type"] == "notsold"]
            not_res = self.graph_notsold.plot(axes, not_prices["time"], 
                                              not_prices["price"],
                                              data_ids=not_prices["id"])
        
        if self.show_guessed:
            guess_prices = prices[prices["type"] == "guessed"]
            guess_res = self.graph_guessed.plot(axes, guess_prices["time"], 
                                                guess_prices["price"],
                                                data_ids=guess_prices["id"])
            
        return avg_res, obs_res, est_res, not_res, guess_res


class DiagramProduct(object):
    """
    Compound diagram that can show the time evolution of several prices.
    
    For possible colors see:
    * http://matplotlib.org/api/colors_api.html#module-matplotlib.colors
    * http://www.w3schools.com/tags/ref_colornames.asp
    
    For possible markers see:
    * http://matplotlib.org/api/artist_api.html#matplotlib.lines.Line2D.set_marker
    
    TODO: Two legends: 
            * One explains the different marker sizes and color shades.
            * The other Shows which color and marker represents which product.
    """
    def __init__(self, product_ids=None, #filters=None, #IGNORE:W0102
                 product_names = None, currency="EUR", title=None,
                 colors=["blue", "red", "green", "orange", "magenta", "cyan"], 
                 markers=["o", "^", "s", "*", "d", "p", "D"]):
        self.filters = []
        self.plotters = []
        self.product_names = product_names if product_names is not None \
                             else product_ids
        self.currency = currency
        self.title = title
        
        for prod_id in product_ids:
            self.filters.append(FilterContains("product", prod_id, 
                                               is_string=True))
        for color, marker, _prod_id in zip(cycle(colors), cycle(markers), 
                                            product_ids):
            self.plotters.append(PlotterPriceSingle(color, marker))
            
        
    def plot(self, figure, price_frame, pick_func=None):
        """Plot the diagram."""
        assert isinstance(figure, matplotlib.figure.Figure)
        
        #Create the plot
        pick_data = {}
        axes = figure.add_subplot(1, 1, 1)
        for filter_, plotter in zip(self.filters, self.plotters):
            prices = filter_.filter(price_frame)
            pick_infos = plotter.plot(axes, prices)
            for info in pick_infos:
                pick_data[info.gid] = info
#        print pick_data
        
        #Create the legend
        if len(self.plotters) == 1:
            legend = axes.legend(loc="best")
            legend.get_frame().set_alpha(0.5)
        else:
            dummies = []
            names = []
            for plotter, name in zip(self.plotters, self.product_names):
                dummy = matplotlib.lines.Line2D(
                            [1,2], [1,2], linewidth=2, markersize=10, 
                            color=plotter.color, marker=plotter.marker)
                dummies.append(dummy)
                names.append(name)
                
            legend = axes.legend(dummies, names, loc="best")
            legend.get_frame().set_alpha(0.5)
        
        #Create title
        if self.title is not None:
            axes.set_title(self.title)
#            figure.suptitle(self.title)
            
        axes.set_ylabel("Price [{}]".format(self.currency))
        #Let the dates at the last axis be plot slanted, 
        #remove any dates from other plots.
        figure.autofmt_xdate()
#        figure.tight_layout()

        pick_helper = PickHelper(pick_data, pick_func)
        figure.canvas.mpl_connect('pick_event', pick_helper)
        return pick_helper
        

        
class PickHelper(object):
    """Identifies price or listing IDs in picked objects."""
    def __init__(self, pick_data, handler_func=None):
        self.pick_data = pick_data
        self.handler_func = handler_func
        
    def __call__(self, event):
        """Called by matplotlib when a pick event occurs."""
        pixel_x = event.mouseevent.x
        pixel_y = event.mouseevent.y
        
        gid = event.artist.get_gid()
#        print gid
        ind = event.ind
        plot_res = self.pick_data[gid]
        data_id = plot_res.data_ids[ind]
#        print data_id
        
        if self.handler_func is not None:
            self.handler_func(data_id, pixel_x, pixel_y)

