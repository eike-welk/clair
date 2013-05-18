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

import numpy as np
import pandas as pd
from matplotlib.colors import colorConverter, rgb_to_hsv, hsv_to_rgb



class Filter(object):
    """
    Base class of filters to select interesting rows (listings or prices) 
    from a (moderately sized) ``DataFrame``. They are useful for creating
    diagrams.
    """
    def filter(self, in_frame):
        """
        Select the interesting rows from the input ``DataFrame``.
        
        Returns ``DataFrame`` that only contains the interesting rows.
        """
        raise NotImplementedError()
    
    

class FilterInterval(Filter):
    """
    Select rows in a ``DataFrame`` based on a half open interval.
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
        where = np.zeros((len(col),), dtype=bool)
        if self.is_string:
            #Convert all elements of ``col`` to strings and 
            #do a string search for the search word
            #TODO: vectorized string operations
            col = col.apply(unicode)
            for i, s in enumerate(col):
                if s.find(self.search_word) >= 0:
                    where[i] = True
        else:
            #Consider all elements of col to be containers (eg. list, set)
            #Test if search word is in container.
            isnull = col.isnull()
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


    
class PlotterXY(object):
    """
    Graph time vs. price. 
    Plot a single relation of X vs. Y. Can create line- and scatter-plots.
    Can plot confidence band, for example for standard deviation.
    Relative trivial class, basically a structured way to store options.
    
    #TODO: Convert into two classes:
           PlotScatter
               Scatter plot with explicit saturation and opacity.
           PlotLine 
               Can plot multiple parallel lines and fill the space
               between the lines.
               Off course with explicit saturation and opacity.
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
    
    def plot(self, axes, xvals, yvals, limits=None):
        """Plot the graph into a ``matplotlib.axes.Axes`` instance."""
        h, _s, v = rgb_to_hsv_tuple(self.color_rgb)
        color_rgb = hsv_to_rgb_tuple((h, self.saturation, v))
        color_rgba = color_rgb + (self.opaqcity,)
        
        #Create line plot or scatter plot?
        if self.linewidth > 0:
            axes.plot(xvals, yvals, label=self.label,
                      color=color_rgba, linestyle=self.linestyle, 
                      linewidth=self.linewidth,
                      marker=self.marker, markerfacecolor=color_rgba, 
                      markersize=self.markersize, zorder=self.zorder)
        else:
            axes.scatter(xvals, yvals, s=self.markersize**2, 
                         c=color_rgba, marker=self.marker, label=self.label,
                         zorder=self.zorder)
        
        #Plot limits? Fill the space between limit lines?
        if limits is not None and self.fill_limits:
            axes.fill_between(xvals, yvals + limits, yvals - limits, 
                              color=color_rgb, alpha=self.lim_opaqcity,
                              zorder=self.lim_zorder)
        elif limits is not None:
            axes.plot(xvals, yvals + limits, 
                      xvals, yvals - limits, 
                      color=color_rgba, linestyle="solid", linewidth=1, 
                      marker=None, zorder=self.lim_zorder)



class DiagramProductTimePrice(object):
    """
    Complex diagram that shows prices of one product versus time.
    
    The features (all optional) are:
    
    * The average or median price is shown by a thick line. Different 
      algorithms can be configured for choice of averaging interval, and 
      data source for averaging.
      
    * Thin lines and semi-transparent areas show the standard deviation.
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
      
    TODO: Compute standard deviation.
    TODO: Legend: single product / multiple products
    TODO: Axis labels
    TODO: Title
    TODO: Show details about price in pop up window.
    TODO: Clicking on price brings user to listing (or price record).
    """
    def __init__(self, color="blue", 
                 show_average=True, show_observed=True, show_estimated=True, 
                 show_notsold=True, show_guessed=True):
        self.show_average = show_average
        self.show_observed = show_observed
        self.show_estimated = show_estimated
        self.show_notsold = show_notsold
        self.show_guessed = show_guessed
        
        self.graph_average = PlotterXY(
                        linewidth=2, markersize=7,  opaqcity=1.0, color=color)
        self.graph_observed = PlotterXY(
                        linewidth=0, markersize=12, opaqcity=1.0, color=color)
        self.graph_estimated = PlotterXY(
                        linewidth=0, markersize=7,  opaqcity=1.0, color=color)
        self.graph_notsold = PlotterXY(
                        linewidth=0, markersize=7,  opaqcity=0.4, color=color)
        self.graph_guessed = PlotterXY(
                        linewidth=0, markersize=12, opaqcity=0.4, color=color)
    
    
    def plot(self, axes, prices):
        """
        Plot the diagram into a ``matplotlib.axes.Axes`` instance,
        for example into a subplot.
        """
        if self.show_average:
            avg_prices = prices[prices["type"] == "average"]
            if len(avg_prices) > 0:
                self.graph_average.plot(axes, avg_prices["time"], 
                                        avg_prices["price"])
        
        if self.show_observed:
            obs_prices = prices[prices["type"] == "observed"]
            if len(obs_prices) > 0:
                self.graph_observed.plot(axes, obs_prices["time"], 
                                         obs_prices["price"])
        
        if self.show_estimated:
            est_prices = prices[prices["type"] == "estimated"]
            if len(est_prices) > 0:
                self.graph_estimated.plot(axes, est_prices["time"], 
                                          est_prices["price"])
        
        if self.show_notsold:
            not_prices = prices[prices["type"] == "notsold"]
            if len(not_prices) > 0:
                self.graph_notsold.plot(axes, not_prices["time"], 
                                        not_prices["price"])
        
        if self.show_guessed:
            guess_prices = prices[prices["type"] == "guessed"]
            if len(guess_prices) > 0:
                self.graph_guessed.plot(axes, guess_prices["time"], 
                                        guess_prices["price"])
        
