libdw library
=============

Data structures
~~~~~~~~~~~~~~~
.. c:type:: dw_struct

    .. c:var:: double *data 
    pointer to data representing the spectrogram to be process (data are logically 2D)
    
    .. c:var:: int rows
    number of rows in data matrix
    
    .. c:var:: int cols
    number of rows in data matrix
    
    .. c:var:: char **flag_data
    pointer to array of pointer to 2D (same rows and cols as input) outdata to write flagging results to
    
    .. c:var:: int l_flag
    length of the array of pointers to flagging data
    
    .. c:var:: int *flag_data_ind
    pointer to array of :c:type: int of length l_flag containing flag matrices labels
    
    .. c:var:: int *flag_product
    pointer to array of int identifying the position in the array pointed by \*\*flag_matrix of each available flagging  product. -1 indicates unselected flagging product
    
    .. c:var:: int l_flag_prod
    length of the array pointed by \*flag_product


Functions
~~~~~~~~~

Common init functions
^^^^^^^^^^^^^^^^^^^^^

.. c:function:: int init_dw(dw_struct *data_struct, double *data, int rows, int cols)
    
    inizialize the values of the pointer to input data and its rows and cols values

    * \*data: pointer to data representing the spectrogram to be process (data are logically 2D)
    * rows: number of rows of data matrix
    * cols: number of columns of data matrix


.. c:function:: int dw_alloc_flag_out(dw_struct *data_struct, int l_flag)

    allocate memory for flag_data array of pointer

    * \*data_struct: pointer to a dw_struct
    * l_flag: length of the array of pointers to flagging data

.. c:function:: int dw_set_flag_out(dw_struct *data_struct, char *flag_data, int i_flag)

    set a pointer to a flagging matrix in the proper data_struct's array

    * \*data_struct: pointer to a dw_struct
    * \*flag_data: pointer to flagging matrix
    * i_flag: index of the data_struct's flag_data array to set the value to

.. c:function:: int dw_set_flag_prod(dw_struct *data_struct, int *flag_product, int l_flag_prod, int *flag_data_ind)

    set values in data_struct

	* \*data_struct: pointer to a dw_struct
	* \*flag_product: pointer to array of int identifying the position in the array pointed by \*\*flag_matrix of each available flagging  product. -1 indicates unselected flagging product
    * l_flag_product: length of the array pointed by \*flag_product
    * \*flag_data_ind: pointer to array of int of length l_flag containing flag matrices labels


RFI detection algorithms
^^^^^^^^^^^^^^^^^^^^^^^^
.. c:function:: int dw_single_channel(dw_struct *data_struct, int channel)

    (test function) set to 1 the values of the proper flagging 
	                 matrix in data_struct. 
	                 
    * \*data_struct: pointer to a dw_struct
    * channel: id of channel to flag
 	
    *Avalilable flag products*
    
    0: flag matrix with the selected channel flagged

.. c:function:: int dw_even_odd(dw_struct *data_struct, double channel_start)

    (test function) set to 1 the values of even and odd channels in separate flagging matrices
	                 
    * \*data_struct: pointer to a dw_struct
    * channel_start: unused

    *Avalilable flag products*
	  
    0: flag matrix containing odd channels flagged
    1: flag matrix containing even channels flagged

.. c:function::  int dw_full_dwt (dw_struct *data, double th_k)

    TO BE IMPLEMENTED       
    * \*data_struct: pointer to a dw_struct

Utility functions
^^^^^^^^^^^^^^^^^
.. c:function::  int bootstrap_resample (double *x_in, int len_in, double *x_out, int len_out)

    return a boostrap resample of the input array
	                 
    * \*x_in: pointer to input array
    * len_in: length of the input array
    * \*x_out: pointer to output array
    * len_out: length of the output array



