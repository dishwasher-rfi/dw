/*This file is part of
 *
 * Dish Washer - RFI cleaning tool for single dish radiotelescopes data
 *
 * Copyright (C) 2014-2015 - IRA-INAF
 *
 * Authors: Federico Cantini <cantini@ira.inaf.it>
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


/* libdw.c - library of automatic RFI detection algorithms
 *
 * The library is primarily intended as high performance algorithms library for 
 * DishWasher - RFI cleaning tool for single dish radiotelescopes data
 * 
 */

#include <stdio.h>
#include <math.h>
#include <gsl/gsl_wavelet.h>
#include <time.h>

#include "libdw.h"
#if OMP == 1
#include <omp.h>
#endif

/*******************************************************************************
 ******************************************************************************* 
 * Common INIT functions
 *******************************************************************************
 ******************************************************************************/

int init_dw(dw_struct *data_struct, double *data, int rows, int cols)
/******************************************************************************* 
  init_dw: inizialize the values of the pointer to input data and its rows and
		   cols values

 	 *data: pointer to data representing the spectrogram to be process
			 (data are logically 2D)
	  rows: number of rows of data matrix
	  cols: number of columns of data matrix
*******************************************************************************/
{
	data_struct->data = data;
	data_struct->rows = rows;
	data_struct->cols = cols;

	return 0;
}

int dw_alloc_flag_out(dw_struct *data_struct, int l_flag)
/******************************************************************************* 
  dw_alloc_flag_out: allocate memory for flag_data array of pointers

 	 *data_struct: pointer to a dw_struct
	  l_flag: length of the array of pointers to flagging data
*******************************************************************************/
{
	free(data_struct->flag_data);
	data_struct->flag_data = malloc(l_flag * sizeof(char *));
	data_struct->l_flag = l_flag;
	
	return 0;
}

int dw_set_flag_out(dw_struct *data_struct, char *flag_data, int i_flag)
/******************************************************************************* 
  dw_set_flag_out: set a pointer to a flagging matrix in the proper data_struct's array

 	 *data_struct: pointer to a dw_struct
	 *flag_data: pointer to flagging matrix
	  i_flag: index of the data_struct's flag_data array to set the value to
*******************************************************************************/
{
	if (i_flag >= data_struct->l_flag)
		return -1;

	data_struct->flag_data[i_flag] = flag_data;
	
	return 0;
}

int dw_set_flag_prod(dw_struct *data_struct, int *flag_product, int l_flag_prod, int *flag_data_ind)
/******************************************************************************* 
  dw_set_flag_prod: set values in data_struct

 	 *data_struct: pointer to a dw_struct
	 *flag_product: pointer to array of int identifying the position in the 
					array pointed by **flag_matrix of each available flagging 
					product. -1 indicates unselected flagging product
	  l_flag_product: length of the array pointed by *flag_product
	  *flag_data_ind: pointer to array of int of length l_flag containing
					  flag matrices labels
*******************************************************************************/
{
	free(data_struct->flag_product);
	data_struct->flag_product = malloc(l_flag_prod * sizeof(int));
	int ii;
	for (ii = 0; ii<l_flag_prod; ii++)
	{
		data_struct->flag_product[ii] = flag_product[ii];
	}	 
	data_struct->l_flag_prod = l_flag_prod;

	free(data_struct->flag_data_ind);
	data_struct->flag_data_ind = malloc(data_struct->l_flag * sizeof(int));
	for (ii = 0; ii<data_struct->l_flag; ii++)
	{
		data_struct->flag_data_ind[ii] = flag_data_ind[ii];
	}	 

	return 0;
}
/*******************************************************************************
 *******************************************************************************
 * RFI algorithms
 *******************************************************************************
 ******************************************************************************/
int dw_single_channel(dw_struct *data_struct, int channel)
/******************************************************************************* 
  dw_single_channel: (test function) set to 1 the values of the proper flagging 
	                 matrix in data_struct. 
	                 
 	 *data_struct: pointer to a dw_struct
	  channel: id of channel to flag

	  Availilable flag products
	  -------------------------
	  0: flag matrix with the selected channel flagged
*******************************************************************************/
{
	int row;
	for (row = 0; row < data_struct->rows; row++)
	{
		data_struct->flag_data[0][row*(data_struct->cols)+channel] = 1;
	}

	return 0;
}

int dw_even_odd(dw_struct *data_struct, double channel_start)
/******************************************************************************* 
  dw_even_odd: (test function) set to 1 the values of even and odd channels in
	           separate flagging matrices
	                 
 	 *data_struct: pointer to a dw_struct
	  channel_start: unused

	  Availilable flag products
	  -------------------------
	  0: flag matrix containing odd channels flagged
	  1: flag matrix containing even channels flagged
*******************************************************************************/
{
#if OMP == 1
	double start, end;
#else
	clock_t start, end;
#endif
	double elapsed;
#if OMP == 1
	start = omp_get_wtime();
#else
	start = clock();
#endif
	
	int ii, row;
	if (data_struct->flag_product[0] > -1) //check if flag_product[0] (odd channels) is requested 
	{
#if OMP == 1 
#pragma omp parallel for private (ii, row)
#endif
		for (ii=0; ii<data_struct->cols; ii+=2)
			for (row = 0; row < data_struct->rows; row++)
				data_struct->flag_data[data_struct->flag_product[0]][row*(data_struct->cols)+ii] = 1; //data_struct->flag_product[0]: index of the array flag_data 
																									  //where the pointer to odd channels flag data is located 
	}

	if (data_struct->flag_product[1] > -1) //check if flag_product[1] (even channels) is requested
	{
#if OMP == 1
#pragma omp parallel for private (ii, row)			
#endif
		for (ii=1; ii<data_struct->cols; ii+=2)
			for (row = 0; row < data_struct->rows; row++)
				data_struct->flag_data[data_struct->flag_product[1]][row*(data_struct->cols)+ii] = 1;
	}

#if OMP == 1
	end = omp_get_wtime();
	elapsed = ((double) (end - start));
#else
	end = clock();
	elapsed = ((double) (end - start)) / CLOCKS_PER_SEC;
#endif
    printf("Elapsed time: %g \n", elapsed);				
	return 0;
}

int dw_full_dwt (dw_struct *data, double th_k)
/******************************************************************************* 
  dw_full_dwt: TO BE IMPLEMENTED       
 	 *data_struct: pointer to a dw_struct
	  

	  Availilable flag products
	  -------------------------
*******************************************************************************/
{
	return 0;
}

/*******************************************************************************
 *******************************************************************************
 * UTIL functions
 *******************************************************************************
 ******************************************************************************/

int bootstrap_resample (double *x_in, int len_in, double *x_out, int len_out)
/******************************************************************************* 
  bootstrap_resample: return a boostrap resample of the input array
	                 
 	 *x_in: pointer to input array
	  len_in: length of the input array
	 *x_out: pointer to output array
	  len_out: length of the output array
*******************************************************************************/
{
	int ii;
	for (ii = 0; ii < len_out; ii++)
	{
		x_out[ii] = rand() % len_in;
	}

	return 0;
}
