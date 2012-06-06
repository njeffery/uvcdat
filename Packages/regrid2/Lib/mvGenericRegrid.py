"""
Generic Regrid class.

Copyright (c) 2008-2012, Tech-X Corporation
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the conditions
specified in the license file 'license.txt' are met.

Authors: David Kindig and Alex Pletzer
"""
import regrid2
import re
from distarray import MultiArrayIter
import operator
import numpy

class GenericRegrid:
    """
    Generic Regrid class.
    """
    def __init__(self, srcGrid, dstGrid, regridMethod = 'Linear', 
                 regridTool = 'LibCF',
                 srcGridMask = None, srcBounds = None, srcGridAreas = None,
                 dstGridMask = None, dstBounds = None, dstGridAreas = None,
                 **args):
        """
        Constructor. Grids, [bounds, masks and areas if passed] must be in the 
        correct shape for the selected regridder
        @param srcGrid array
        @param dstGrid array
        @param regridMethod Linear (bi, tri,...) default or Conservative
        @param regridTool LibCF (gsRegrid), ESMP (ESMF)
        @param srcGridMask array of same shape as srcGrid
        @param srcBounds array of same shape as srcGrid
        @param srcGridAreas array of same shape as srcGrid
        @param dstGridMask array of same shape as dstGrid
        @param dstBounds array of same shape as dstGrid
        @param dstGridAreas array of same shape as dstGrid
        """

        self.nGridDims = len(srcGrid)

        if len(srcGrid) != len(dstGrid):
            msg = 'mvGenericRegrid.__init__: mismatch in number of dims'
            msg += ' len(srcGrid) = %d != len(dstGrid) = %d' % \
                (self.nGridDims, len(dstGrid))
            raise regrid2.RegridError, msg

        # parse the options
        if re.search('libcf', regridTool.lower()) or \
           re.search('gsreg', regridTool.lower()):
            self.tool = regrid2.LibCFRegrid(srcGrid, dstGrid, 
                 srcGridMask = srcGridMask, srcBounds = srcBounds)
        elif re.search('esm', regridTool.lower()):
            self.tool = regrid2.ESMFRegrid(srcGrid, dstGrid, 
                 srcGridMask = srcGridMask, srcBounds = srcBounds, srcGridAreas = srcGridAreas,
                 dstGridMask = dstGridMask, dstBounds = dstBounds, dstGridAreas = dstGridAreas,
                 **args)
    
    def computeWeights(self):
        """
        Compute Weights
        """
        self.tool.computeWeights()

    def apply(self, srcData, dstData, srcDataMask = None, 
              **args):
        """
        Regrid source to destination
        @param srcData array (input)
        @param dstData array (output)
        @param srcDataMask array
        """

        nonHorizShape = srcData.shape[: -self.nGridDims]
        if len(nonHorizShape) == 0:

            #
            # no axis... just call apply 
            #

            self.tool.apply(srcData, dstData, **args)

        else:

            nonHorizShape2 = dstData.shape[: -self.nGridDims]
            if not numpy.all(nonHorizShape2 == nonHorizShape):
                msg = 'mvGenericRegrid.apply: axes detected '
                msg += 'but %s != %s ' % (str(nonHorizShape2),
                                          str(nonHorizShape))
                raise regrid2.RegridError, msg

            #
            # iterate over all axes
            #

            # create containers to hold input/output values
            # (a copy is essential here)
            zros = '[' + ('0,'*len(nonHorizShape)) + '...]'
            indata = numpy.array(eval('srcData' + zros))
            outdata = numpy.array(eval('dstData' + zros))

            # now iterate over all non lat/lon coordinates
            for it in MultiArrayIter(nonHorizShape):

                indices = it.getIndices()
                slce = '[' 
                slce += reduce(operator.add, ['%d,'%i for i in indices])
                slce += '...]'
                indata = eval('srcData' + slce)

                # interpolate, using the appropriate tool
                self.tool.apply(indata, outdata, **args)

                # fill in dstData
                exec('dstData' + slce + ' = outdata')
