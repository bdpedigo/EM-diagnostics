# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 10:10:00 2017

@author: benjaminp
"""
import bokeh.plotting as bkp
import diagnostics
import numpy as np

from bokeh.io import output_file, show
from bokeh.layouts import column
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import Title, Range1d, LinearAxis
from bokeh.models import HoverTool, BoxZoomTool, ResetTool, WheelZoomTool, PanTool, SaveTool

plot_cs_pm = False

montaged = {
        "render": {
            "owner":"gayathri",
            "project":"EM_Phase1",
            "host":"http://10.128.124.14",
            "port":8999,
            "client_scripts":"/data/nc-em2/gayathrim/Janelia_Pipeline/render/render-ws-java-client/src/main/scripts"
        },
        
        "matchSource":'Phase1Data_2366_2415_montagePM',
        'sourceStack':'Phase1Data_2366_2415_Montage'
}

simple_mat = np.load('save_simple_mat.npy')
avg_simple_mat = np.mean(simple_mat, axis = 1)
save_all_medians = np.load('save_all_medians.npy')

output_file('test.html')

def simple_plot(title = 'title', x_label = 'Section (z)', y_label = None, width = 800, height = 400, size = 15, tools = []):
    
    if tools != []:
        p = figure(plot_height = height, plot_width = width, tools = tools)
    else:
        p = figure(plot_height = height, plot_width = width)
    p.title.text = title
    p.title.align = "center"
    p.title.text_font_size = "25px"
    p.add_layout(Title(text=x_label, align="center"), "below")
    p.add_layout(Title(text=y_label, align="center"), "left")

    return p

def plot_cs_resids(simple_mat, z_start, z_end):
    rng = range(z_start, z_end+1)
    lvl_1_resids = simple_mat[:,0:2]
    lvl_2_resids = simple_mat[:,2:4]
    lvl_1_means = np.mean(lvl_1_resids, axis = 1)
    lvl_2_means = np.mean(lvl_2_resids, axis = 1)
    #means = np.column_stack((lvl_1_means, lvl_2_means))
    
#    means_means = np.mean()
    
    cs_pm_source = ColumnDataSource(data = dict(xs = rng,
                                                lvl_1_means = lvl_1_means,
                                                lvl_2_means = lvl_2_means,
                                                lvl_1_p = simple_mat[:,0],
                                                lvl_1_q = simple_mat[:,1],
                                                lvl_2_p = simple_mat[:,2],
                                                lvl_2_q = simple_mat[:,3],
                                                ))
    
    cs_hov = HoverTool(tooltips = [
            ('Section', '@xs'),
            ('1 level resid', '@lvl_1_means'),
            ('2 level resid', '@lvl_2_means'),
            ])
    
    wheel_zoom = WheelZoomTool()
    cs_pm_fig = simple_plot('Cross-section residuals for sections %i - %i' %(z_start, z_end), y_label = 'Residual', tools = [cs_hov, BoxZoomTool(), ResetTool(), wheel_zoom, PanTool(), SaveTool()])
    cs_pm_fig.toolbar.active_scroll = wheel_zoom
    cs_pm_fig.circle('xs', 'lvl_1_means', source = cs_pm_source, color = 'red', legend = '1 Section Step', )
    cs_pm_fig.circle('xs', 'lvl_2_means', source = cs_pm_source, legend = '2 Section Steps', )
    cs_pm_fig.legend.click_policy = 'hide'
    cs_pm_fig.toolbar_sticky = False
    cs_pm_fig.toolbar_location = 'below'
    
    show(cs_pm_fig)
    return cs_pm_fig


#==============================================================================
# Cross-section PM Plotting
#==============================================================================

if plot_cs_pm:
    plot_cs_resids(simple_mat, 2268, 2800)
    
#==============================================================================
# Montage PM plotting
#==============================================================================
plot_mont_pm = True
data = np.load('save_dict_mont_out.npy')
if plot_mont_pm:
    starts = range(2266,3416,50)
    ends = range(2315,3465,50)
    # variance, mean, median, outlier counts, outlier percents, unconnected counts
    start = 2266
    end = 3415
    
    #start = 2268
    #end = 3481
    all_sections = range(start,end + 1)
    
    
    current_medians = save_all_medians
    #compare_simple_mat = avg_simple_mat[:1148]

    
    def plot_mont_or_ap(data, z_start, z_end, datatype = None, to_plot = 'all'):
        ''' 
        Plots and returns Bokeh figure handle for a variety of statistics.
        
        Inputs: 
            data - usually a dictionary of the same format output by 
            calculate_montage_pm_residuals or calculate_area_perimeter_ratios. 
            
            z_start/z_end - integer values to make the range for the x axis 
            
            dataype - 'montage', 'area', or 'perimeter'. This specifies the 
            type of data that you are inputting to produce the correct title 
            and labels. 
            
            to_plot - 'all', 'mean and median', 'outliers', or 'variance'. This 
            specifies what stats you want to plot. 'all' displays all of the 
            above all on the same axes, but the different scales will make the 
            data hard to interpret. 'mean and median' plots on the same axis 
            scale. 'outliers' plots both outlier counts and outlier percents, 
            with different scale bars for each. 'variance' plots the variance
            alone. 
        
        Outputs:
            Bokeh figure handle for the specified plot. 
        
        '''
               
        
        if datatype == 'montage':
            title = 'Montage residuals for sections %i - %i' %(z_start, z_end)
            y_ax = 'Residual'
        elif datatype == 'area':
            title = 'Area ratios for sections %i - %i' %(z_start, z_end)
            y_ax = 'Ratio'
        elif datatype == 'perimeter':
            title = 'Perimeter ratios for sections %i - %i' %(z_start, z_end)
            y_ax = 'Ratio'
        else:
            title = 'Sections %i - %i' %(z_start, z_end)
        
        rng = range(z_start, z_end + 1)
        if type(data) == dict:
            dataSource = ColumnDataSource(data = dict(xs = rng,
                                                    means = data['means'],
                                                    medians = data['medians'],
                                                    outlier_counts = data['outlier counts'],
                                                    outlier_percents = data['outlier percent'],
                                                    variances = data['variances'],
                                                    ))
            mont_hov = HoverTool(tooltips = [
                ('Section', '@xs'),
                ('Mean', '@means'),
                ('Median', '@medians'),
                ('Variances', '@variances'),
                ('Outlier Count', '@outlier_counts'),
                ('Outlier Percent', '@outlier_percents'),
                ])
            
            wheel_zoom = WheelZoomTool()
            mont_fig = simple_plot(title, tools = [mont_hov, BoxZoomTool(), ResetTool(), wheel_zoom, PanTool(), SaveTool()])
            mont_fig.toolbar.active_scroll = wheel_zoom
            mont_fig.toolbar_sticky = False
            mont_fig.toolbar_location = 'below'
            
            if to_plot == 'all':
                mont_fig.circle('xs', 'means', source = dataSource, legend = 'Means')
                mont_fig.circle('xs', 'medians', color = 'red', source = dataSource, legend = 'Medians')
                mont_fig.circle('xs', 'outlier_counts', color = 'green', source = dataSource, legend = 'Outlier Counts')
                mont_fig.circle('xs', 'outlier_percents', color = 'orange', source = dataSource, legend = 'Outlier Percents')
                mont_fig.circle('xs', 'variances',color = 'purple', source = dataSource, legend = 'Variances')
            
            elif to_plot == 'mean and median':
                mont_fig.circle('xs', 'means', source = dataSource, legend = 'Means')
                mont_fig.circle('xs', 'medians', color = 'red', source = dataSource, legend = 'Medians')
                mont_fig.add_layout(Title(text=y_ax, align="center"), "left")

            elif to_plot == 'outliers':
                y_label = 'Counts'
                y_label2 = 'Percent'
                left_range = max(data['outlier counts'])
                right_range = max(data['outlier percent'])
                mont_fig.add_layout(Title(text=y_label, align="center"), "left")
                mont_fig.extra_y_ranges = {'extra_y':Range1d(start = -0.05*right_range, end = 1.05*right_range)}
                y2_axis = LinearAxis(y_range_name = 'extra_y', axis_label = y_label2, axis_label_text_font_style = 'bold', axis_label_text_font = 'helvetica')
                mont_fig.circle('xs', 'outlier_counts', color = 'green', source = dataSource, legend = 'Outlier Counts')
                mont_fig.add_layout(y2_axis, 'right')
                mont_fig.circle('xs', 'outlier_percents', color = 'orange', source = dataSource, legend = 'Outlier Percents', y_range_name = 'extra_y')
                mont_fig.y_range = Range1d(-1*left_range*0.05, left_range*1.05)
            
            elif to_plot == 'variance':
                mont_fig.circle('xs', 'variances',color = 'purple', source = dataSource, legend = 'Variances')
                mont_fig.add_layout(Title(text=y_ax, align='center'), 'left')

            mont_fig.legend.click_policy = 'hide'
            
        show(mont_fig)
        return mont_fig
    
    
    
    
    #plot_mont_resid(montage_residuals, 2266, 2315, 'variance')
            
    
    
    
    
    
    
    plot_mont_or_ap(A_P_stats['perimeter'],2266,2315,'area', 'outliers')
    
    
    def plot_composite():
        
    
    #    elif type(data) == numpy.ndarray or type(data) == list:
    #        
    #    else:
    #        print('Incompatible data structure for plotting')
    
    
    
    
    #
    #compare_cs_mont = simple_plot('Compare', x_label = 'montage', y_label = 'cross-section')
    #compare_cs_mont.circle(current_medians, compare_simple_mat)
    #show(compare_cs_mont)
    #corr = np.corrcoef(compare_simple_mat[0:300], current_medians[0:300])