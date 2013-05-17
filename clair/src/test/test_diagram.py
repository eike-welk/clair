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
Test the diagram library.
"""

from __future__ import division
from __future__ import absolute_import              

#import pytest #contains `skip`, `fail`, `raises`, `config`

import time
import os.path as path
from datetime import timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from clair.coredata import make_price_frame


#Set up logging fore useful debug output, and time stamps in UTC.
import logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.DEBUG)
#Time stamps must be in UTC
logging.Formatter.converter = time.gmtime



def relative(*path_comps):
    "Create file paths that are relative to the location of this file."
    return path.abspath(path.join(path.dirname(__file__), *path_comps))


def create_test_prices():
    """
    Create data frame with pseudo random prices for testing.
    The function always generates the same random sequence.
    """
    n_prices = 100
    #Generate the same random numbers every time
    np.random.seed(1234)
    rand = np.random.normal(size=(n_prices,))
    #Random times, frequency approximately daily.
    delta = np.array([timedelta(r * 5) for r in rand])
    times = pd.date_range(start="2000-1-1", periods=n_prices, freq="d")
    #TODO: Report Pandas bug "Very odd behavior" ``times + times == times``
    times = np.array([pd.Timestamp(t) for t in times]) + delta
    #ID string, based on time.
    index = [str(t)+"-foo" for t in times]
    #Random prices that don't follow the normal distribution
    prices = 3 * rand + 20 + np.sin(rand * 3) * 5
    #Types, a small amount are observed prices
    types = np.where(np.random.uniform(size=n_prices) < 0.2, 
                     "observed", "estimated")
    
    price_frame = make_price_frame(index=index)
    price_frame["id"] = index
    price_frame["time"] = times
    price_frame["price"] = prices
    price_frame["type"] = types
    price_frame["product"] = "foo"
    
    #Create mean prices
    monthly = pd.TimeGrouper(freq="M")
    prices_t = price_frame.set_index("time")
    stats = prices_t.groupby(monthly).aggregate(np.mean)
    stats["time"] = stats.index - timedelta(15)
    stats["id"] = [str(t)+"-mean-foo" for t in stats["time"]]
    stats["product"] = "foo"
    stats.set_index("id", drop=False, inplace=True)
#    print stat
    price_frame = price_frame.append(stats)
    
#    print price_frame
    return price_frame
    
    
    
def test_filters():
    """Test the Filter* classes."""
    from clair.diagram import FilterInterval, FilterContains
    print "Start"
    
    #Create a test data frame
    data = pd.DataFrame({"id": ["foo-" + str(i) for i in range(10)],
                         "str_list": None,
                         "float_val": np.linspace(2.1, 21, 10), 
                         "time": pd.date_range(start="2000-1-1", periods=10, 
                                              freq="D")})
    str_lists =[["foo"], ["bar"], ["foo", "bar"], ["baz"], None,
                ["foo"], ["bar"], ["foo", "bar"], ["baz"], ["boum"]]
    for i, l in enumerate(str_lists):
        data["str_list"][i] = l
    data.set_index("id", drop=False, inplace=True)
    print data
    
    print "\nSelect string lists that contain string 'foo'."
    contains_foo = FilterContains("str_list", "foo")
    data_foo = contains_foo.filter(data)
    print data_foo
    assert all(data_foo["id"] == ["foo-0", "foo-2", "foo-5", "foo-7"])
    
    print "\nSelect strings that contain the substring '2'."
    contains_2 = FilterContains("id", "2")
    data_2 = contains_2.filter(data)
    print data_2
    assert all(data_2["id"] == ["foo-2"])
    
    print "\nSelect values between 3 and 9."
    between_3_9 = FilterInterval("float_val", 3, 9)
    data_3_9 = between_3_9.filter(data)
    print data_3_9
    #TODO: Bug report to Pandas because of inconsistent behavior.
#    print data_3_9["float_val"] == [4.2, 6.3, 8.4]
#    print data_3_9["id"] == ["foo-1", "foo-2", "foo-3"]
#    print data_3_9["float_val"]
#    assert all(data_3_9["float_val"] == [4.2, 6.3, 8.4])
    assert all(data_3_9["id"] == ["foo-1", "foo-2", "foo-3"])
    
    print "\nExclude values between 3 and 9."
    exclude_3_9 = FilterInterval("float_val", 3., 9., inside=False)
    data_no_3_9 = exclude_3_9.filter(data)
    print data_no_3_9
    #Parameter ``inside``: 
    #    * True vs. False must partition data frame into disjoint sets.
    #    * Both options together must cover all elements of data frame.
    assert len(data_no_3_9) == 7
    assert len(data_3_9) == 3
    all_data = data_3_9.combine_first(data_no_3_9)
    assert all(all_data["float_val"] == data["float_val"])
    
    print "\nSelect select dates between 2000-1-3 and 2000-1-6 " \
          "(excluding last date)."
    contains_3dates = FilterInterval("time", 
                                     pd.Timestamp("2000-1-3"), 
                                     pd.Timestamp("2000-1-6"))
    data_3dates = contains_3dates.filter(data)
    print data_3dates
    assert all(data_3dates["id"] == ["foo-2", "foo-3", "foo-4"])
    
    
def test_GraphTimePrice():
    """
    Test class GraphTimePrice.
    
    TODO: assertions. Look at Matplotlib tests.
          http://matplotlib.org/devel/testing.html
    """
    from clair.diagram import GraphTimePrice
    
    print("Start")
    
    #Create a data frame with random prices and times
    prices = create_test_prices()
    prices = prices.sort("time")
    
    #Create the objects for Matplotlib
    fig = plt.figure()
    
    #Test line plot
    ax = fig.add_subplot(2, 2, 1)
    graph = GraphTimePrice(prices["time"], prices["price"])
    graph.plot(ax)
    
    #Test scatter plot
    ax = fig.add_subplot(2, 2, 2)
    graph = GraphTimePrice(prices["time"], prices["price"], 
                           linewidth=0, saturation=0.5)
    graph.plot(ax)
    
    #Compute average and standard deviation
    monthly = pd.TimeGrouper(freq="M")
    prices_t = prices.set_index("time")
    month_stats = prices_t.groupby(monthly).aggregate([np.mean, np.std])
#    print month_stats
    
    #Test limit display: filled
    ax = fig.add_subplot(2, 2, 3)
    graph_mean = GraphTimePrice(month_stats.index, 
                                month_stats["price"]["mean"], 
                                month_stats["price"]["std"], markersize=7)
    graph_mean.plot(ax)
    graph.plot(ax) #Scatter plot on top, to see how they look together
    
    #Test limit display: lines
    ax = fig.add_subplot(2, 2, 4)
    graph_mean = GraphTimePrice(month_stats.index, 
                                month_stats["price"]["mean"], 
                                month_stats["price"]["std"], markersize=7,
                                fill_limits=False)
    graph_mean.plot(ax)
    graph.plot(ax) #Scatter plot on top, to see how they look together
    
    fig.autofmt_xdate()
    plt.show()
    print("End")
    
    
    
if __name__ == "__main__":
#    test_filters()
    test_GraphTimePrice()
    
    pass #IGNORE:W0107