#@ ImagePlus(label="Binary Image: ", description="Output stack from MiNA macro set.") binImg
#@ ImagePlus(label="Skeleton Image: ", description="Output stack from MiNA macro set.") skelImg
#@ LogService logger

################################################################################
#   Title: MiNA 3D Viewer
#   Contact: valentaj94@gmail.com
################################################################################

#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
Functionality and script for processing a 3 channel MiNA output stack into a
volume/surface render for assessing accuracy of the morphological skeleton. this
script is largely based on the BeanShell script written by Ignacio
Arganda-Carreras and available at http://imagej.net/AnalyzeSkeleton.
'''

from ij import IJ
from ij3d import Image3DUniverse
from org.scijava.vecmath import Point3f
from org.scijava.vecmath import Color3f
from sc.fiji.analyzeSkeleton import AnalyzeSkeleton_
from sc.fiji.analyzeSkeleton import Edge
from sc.fiji.analyzeSkeleton import Point

def MiNA_Render_3D(binary, skeleton):
    '''
    Render a 3D-Viewer visualization of a skeleton and associated binary.

    Parameters
    ----------
    binary : ImagePlus
    The binary image to render as a 50% transparent surface. Must be a single
    channel z-stack.
    skeleton : ImagePlus
    The skeleton image stack to render as a wire frame and points. Must be a
    single channel z-stack.
    '''
    # analyze skeleton
    skel = AnalyzeSkeleton_()
    skel.setup("", skeleton)
    skelResult = skel.run(AnalyzeSkeleton_.NONE, False, False, None, True, False)

    # get calibration
    pixelWidth = skeleton.getCalibration().pixelWidth
    pixelHeight = skeleton.getCalibration().pixelHeight
    pixelDepth = skeleton.getCalibration().pixelDepth

    # get graphs (one per skeleton in the image)
    graph = skelResult.getGraph()

    # create 3d universe
    univ = Image3DUniverse()
    univ.show()

    # list of end-points
    endPoints = skelResult.getListOfEndPoints();
    # store their positions in a list
    endPointList = []
    for p in endPoints:
        endPointList.append(Point3f(
            (p.x * pixelWidth),
            (p.y * pixelHeight),
            (p.z * pixelDepth)))

    # add end-points to the universe as blue spheres
    univ.addIcospheres(endPointList,Color3f(0,0,255), 2, 0.1, "End-points")

    # list of junction voxels
    junctions = skelResult.getListOfJunctionVoxels()
    # store their positions in a list
    junctionList = []
    for p in junctions:
        junctionList.append(Point3f(
            (p.x * pixelWidth),
            (p.y * pixelHeight),
            (p.z * pixelDepth)))

    # add junction voxels to the universe as magenta spheres
    univ.addIcospheres(junctionList, Color3f(0,255,0), 2, 0.1, "Junctions")

    for i in range(len(graph)):

        listEdges = graph[i].getEdges();

        # go through all branches and add slab voxels
        # as orange lines in the 3D universe
        j=0;
        for e in listEdges:
            branchPointList = [];
            for p in e.getSlabs():
                branchPointList.append(Point3f(
                    (float)( p.x * pixelWidth ),
                    (float)( p.y * pixelHeight ),
                    (float)( p.z * pixelDepth ) ) )

            #add slab voxels to the universe as orange lines
            univ.addLineMesh(branchPointList, Color3f(255,0,255), "Branch-"+str(i)+"-"+str(j), True);
            j += 1

    # Add the binary data
    bin = univ.addMesh(binary, Color3f(255,255,255), "Binary", 50, [True, True, True], 2)
    bin.setTransparency(0.5)

if __name__=="__main__" or __name__=="__builtin__":
    #TODO: Process focused image to duplicate the binary and skeleton of the
    #      frame that is currently selected if time series, otherwise take the
    #      only frame available...
    
    # Render the scene
    MiNA_Render_3D(binary=binImg, skeleton=skelImg)
