# -*- coding: utf-8 -*-
"""
This script plots the solutions contained on the LePHARE output .spec files.

Syntax: spec_plotter file.spec

For interactive mode just call the script.

Created on Tue Dec 17 02:48:28 2019

@author: Joao Aguas
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
from os import path
from sys import exit

#If this script is used in a windows machine uncomment the next line!
# import msvcrt as m

argtemp=sys.argv
if len(argtemp) < 2:
    filename = input('Input file: ')
else:
    filename=argtemp[1]

# Verifying the existance of the file, and opening it.

if path.exists(filename) == True:
    file = open(filename, "r")
else:
    print('\n\nI think that you made a mistake, it was not me!!!\nFile not found!!!\n\n\n')
    exit()

# Reading the header

head_buff = []

for i in range(1,14):
    head_buff.append(file.readline())


## Parsing the header and storing the important data.
# Information about the Ident of the object, spectroscopic z (if available),
# and about the photometric z.
    
ident = int(head_buff[1].split()[0])
zspec = float(head_buff[1].split()[1])
zphot = float(head_buff[1].split()[2])


# The number of filters used by LePHARE.

nfilt = int(head_buff[3].split()[1])

# The number of z steps for the PDF plot.

npdf = int(head_buff[5].split()[1])


## Solution detection.
# This next section detects the solutions by searching which
# cases contain a number of lines (magnitude|wavelength) greater than 0.
# Each solution will contain the following information:
# Type,Nline,Model,Library,Nband,Zphot,Zinf,Zsup,Chi2,PDF,Extlaw,EB-V,Lir,Age,
# Mass,SFR,SSFR

solInfo = []
list(solInfo)

for ii in range(6):
    if int(head_buff[7+ii].split()[1]) > 0:
        solInfo.append(head_buff[7+ii])
        
nsol = len(solInfo)


## Filter Information.
# The filter information lines counter is in the header, it was stored in nfilt
# The information stored is:
# Mag,emag,Lbd_mean,Lbd_width,Mag_gal,Mag_FIR,Mag_BCSTOCH
 
filt_buff = []

for ii in range(nfilt):
    filt_buff.append(file.readline())
    filt_buff[ii] = filt_buff[ii].split()
    
filt_buff = np.array(filt_buff,dtype=float)


## The PDF data.
# The number of lines used to construct the PDF is stored in the npdf variable.

pdf_buff= []

for ii in range(npdf):
    pdf_buff.append(file.readline())
    pdf_buff[ii] = pdf_buff[ii].split()
    
pdf_buff = np.array(pdf_buff,dtype=float)


# Compiling string with the information of each solution.

InfoStr = ['']
list(InfoStr)
InfoStr = [(head_buff[6].split())[1:]]

for ii in range(nsol):
    InfoStr.append(solInfo[ii].split())


## Extracting the found solutions.
# Creating an array with the number of lines per solution

sollines = np.zeros(nsol,int)

for sol in range(nsol):
    sollines[sol]=solInfo[sol].split()[1]

solutions = []
buff = []

for sol in range(nsol):
    r=sollines[sol]
    for ii in range(r):
        tmp=(file.readline()).split()
        tmp=np.array(tmp,dtype=float)
        buff.append([tmp[0],tmp[1]])
    solutions.append([buff])
    buff=[]


## Plotting the solutions in a pretty plot. :)
# Plotting the spectrum solutions.
    
col=['black','blue','red','green','gray','lightgray']
titleid='Object ID: '+ str(ident)
fupl=True
fobs=True

fig = plt.figure(figsize=(14,7))
ax = plt.subplot(111)
plt.xscale('log')

for ii in range(nsol):
    tmp = np.array(solutions[ii],float)
    ax.plot(tmp[0,:,0],tmp[0,:,1],color=col[ii],
            label=(solInfo[ii].split())[0])


# Plotting the bands.
    
for ii in range(nfilt):
    if filt_buff[ii,0]!=-99:
        if filt_buff[ii,1]>0:
            if fobs == True:
                ax.scatter(filt_buff[ii,2],filt_buff[ii,0],marker='o',c='black',
                           label='Observation')
                fobs=False
            else:
                ax.scatter(filt_buff[ii,2],filt_buff[ii,0],marker='o',c='black')
            plt.errorbar(filt_buff[ii,2],filt_buff[ii,0],yerr=filt_buff[ii,1],
                         xerr=filt_buff[ii,3]/2,color='black',capsize=5)
        else:
            if fupl == True:
                ax.scatter(filt_buff[ii,2],filt_buff[ii,0],marker='v',c='black',
                           label='Upper Limit')
                fupl=False
            else:
                ax.scatter(filt_buff[ii,2],filt_buff[ii,0],marker='v',c='black')
            plt.errorbar(filt_buff[ii,2],filt_buff[ii,0],xerr=filt_buff[ii,3]/2
                         ,color='black',capsize=5)


plt.gca().invert_yaxis()
ax.set_title(titleid + ', zspec=' + head_buff[1].split()[1] + ', zphot=' + head_buff[1].split()[2])
plt.ylabel(r'Mag')
fig.gca().set_xlabel(r'$\lambda ( \AA )$')
ax.legend()
plt.show()


## Plotting the PDF

if npdf > 0:
    figpdf = plt.figure()
    ax = plt.subplot(111)
    ax.plot(pdf_buff[:,0], pdf_buff[:,1])
    ax.set_title('PDF  ' + titleid)
    ax.set_xlabel('z', fontsize=14)
    ax.set_ylabel('Probability', fontsize=14)
    plt.show()


## Showing the solution details

fig=plt.figure(figsize=(20,3)) 
the_table=plt.table(cellText=InfoStr,loc='center')
the_table.auto_set_font_size=False
the_table.set_fontsize(24)
the_table.scale(1.2,1.2)
plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
for pos in ['right','top','bottom','left']:
    plt.gca().spines[pos].set_visible(False)
plt.show()

print(tabulate(InfoStr))

input('Press enter to exit...')
