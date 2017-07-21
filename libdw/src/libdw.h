/*This file is part of
 *
 * Dish Washer - RFI cleaning tool for single dish radiotelescopes data
 *
 * Copyright (C) 2014-2015 - IRA-INAF
 *
 * Author: Federico Cantini <cantini@ira.inaf.it>
 * 
 * Manteiner: Federico Cantini <cantini@ira.inaf.it>
 * 
 * libdw is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * libdw is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along
 * with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/* libdw.h - library of automatic RFI detection algorithms
 *
 * The library is primarily intended as high performance algorithms library for 
 * DishWasher - RFI cleaning tool for single dish radiotelescopes data
 * 
 */

#define OMP		1 // Define wheter to use OpenMP

/******************************************************************************* 
 * Data structures definition
 ******************************************************************************/

/******************************************************************************* 
 dw_struct: store the input data (and pointers to) and output pointers needed
			  by the RFI detection algorithms

	 *data: pointer to data representing the spectrogram to be process
			 (data are logically 2D)
	  rows: number of rows of data matrix
	  cols: number of columns of data matrix
	**flag_data: pointer to array of pointer to 2D (same rows and cols 
	               as input) outdata to write flagging results to
	  l_flag: length of the array of pointers to flagging data
	 *flag_data_ind: pointer to array of int of length l_flag containing
					 flag matrices labels
	 *flag_product: pointer to array of int identifying the position in the 
					array pointed by **flag_matrix of each available flagging 
					product. -1 indicates unselected flagging product
	  l_flag_product: length of the array pointed by *flag_product
 ******************************************************************************/
typedef struct
{	
	double *data;
	int rows;
	int cols;
	char **flag_data;
	int l_flag; 
	int *flag_data_ind;
	int *flag_product;
	int l_flag_prod; 
} dw_struct;


/*******************************************************************************
 ******************************************************************************* 
 * Common init functions
 *******************************************************************************
 ******************************************************************************/

int init_dw(dw_struct *data_struct, double *data, int rows, int cols);

int dw_alloc_flag_out(dw_struct *data_struct, int l_flag);

int dw_set_flag_out(dw_struct *data_struct, char *flag_data, int i_flag);

int dw_set_flag_prod(dw_struct *data_struct, int *flag_product, int l_flag_prod, int *flag_data_ind);

/*******************************************************************************
 *******************************************************************************
 * RFI algorithms
 *******************************************************************************
 ******************************************************************************/
int dw_single_channel(dw_struct *data_struct, int channel);

int dw_even_odd(dw_struct *data_struct, double channel_start);

int dw_full_dwt (dw_struct *data, double th_k);

/*******************************************************************************
 *******************************************************************************
 * Util functions
 *******************************************************************************
 ******************************************************************************/
int bootstrap_resample (double *x_in, int len_in, double *x_out, int len_out);