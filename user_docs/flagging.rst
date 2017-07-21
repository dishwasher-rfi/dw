==========================
Flagging
==========================


Manual flagging
~~~~~~~~~~~~~~~~~~

To mannually flag an area of the waterfall plot there are two tools:

* *Channel range flagging*
* *Area flagging*

They will create an element in the data list. 

One or more of these elements can be selected and saved as a flagset with the command *Flag* found in the flag toolbar or in the flag menu.

Auto RFI detection
~~~~~~~~~~~~~~~~~~

To run the *automatic RFI detection*:

* select *Flagging -> Auto RFI detection*.
* choose the detection algorithm to use and press *OK*
* change the default parameters if necessary, then press *OK*
* choose the flagging matrices to calculate.

Automatic detected RFI matrices are added to the data structure.

To see the available algorithms refer to next Section. 


Automatic RFI Detection Algorithms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Currently only one automatic algorithm for RFI detection is implemented.




Simple Threshold Algorithm
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Method: sigma-clipping.

Parameters: number of r.m.s. above the median data value.

The user defines the flagging threshold as a multiple of the data r.m.s. To help
in this choice, the mean, median and r.m.s. for each data type (L, R, Q, U) are displayed.
The user may chose to apply the flagging to one or more data types. In case more data
types are to be flagged simultaneously, the proper threshold for each type is computed
wit the related r.m.s.
The algorithm identifies all the data above the threshold, creating a number of rectangular
regions defining the flagged areas. These regions are displayed on the image and listed as
a single item in the item list.

