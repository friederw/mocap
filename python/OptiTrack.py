#!/usr/bin/python

import os
import csv
import numpy as np

LEFT_HANDED = 0
RIGHT_HANDED = 1
TSL = 11            #Trackable state vector length
MSL = 3 #Marker state vector length

class Run():
    """Represents an experimental run as a collection of frames"""

    def __init__(self):
        self.trackables = []
        self.frames = []
        self.trackable_frames = []
        self.coord_type = RIGHT_HANDED
        self.framecount = 0
        self.trackablecount = 0

    def ReadFile(self, data_dir, filename):
        """Create a Run from a data file

        Args:
            data_dir: string directory name
            filename: string name of the file to load
        """

        filename = os.path.join(data_dir, filename)
        fp = csv.reader(open(filename, "rU"))
        try:
            while(1):
                fields = fp.next()
                if fields[0].lower() == "comment":
                    pass
                elif fields[0].lower() == "righthanded":
                    self.coord_type = RIGHT_HANDED
                else:
                    self.coord_type = LEFT_HANDED
                    if fields[0].lower() == "info":
                        if fields[1].lower() == "framecount":
                            self.framecount = int(fields[2])
                        elif fields[1].lower() == "trackablecount":
                            self.trackablecount = int(fields[2])
                            if self.trackablecount > 0:
                                for i in range(self.trackablecount):
                                    self.trackables.append(Trackable(fp.next()))
                    elif fields[0].lower() == "frame":
                        self.frames.append(Frame(fields))
                    elif fields[0].lower() == "trackable":
                        self.trackable_frames.append(TrackableFrame(fields))
        except StopIteration:
            pass

class Frame():
    """Represents one frame of motion capture data"""
    def __init__(self, fields):
        """Constructor for a frame object"""
        if fields[0].lower() != "frame":
            raise Exception("You attempted to make a frame from something " +\
                            "that is not frame data.")

        self.trackable_states = []
        self.markers = []

        self.index = int(fields[1])
        self.timestamp = float(fields[2])
        self.trackable_count = int(fields[3])
        idx = 4
        if self.trackable_count > 0:
            for i in range(self.trackable_count):
                self.trackable_states.append(TrackableState(fields[idx:idx+TSL]))
                idx += TSL
        self.marker_count = int(fields[idx])
        idx += 1
        for i in range(self.marker_count):
            self.markers.append(Marker(fields[idx+MSL], fields[idx:idx+MSL]))
            idx += 4

class TrackableFrame():
    """Represents extended frame information for frames containing
    trackables."""

    def __init__(self, fields):
        """Constructor for a frame of extended trackable information"""
        self.markers = []
        self.ptcld_markers = []
        self.index = int(fields[1])
        self.timestamp = float(fields[2])
        self.name = fields[3]
        self.id = int(fields[4])
        self.last_tracked = int(fields[5])
        self.marker_count = int(fields[6])
        idx = 7
        #Store the trackable markers
        for i in range(self.marker_count):
            tracked = fields[idx + (self.marker_count-i)*MSL + self.marker_count*MSL +
                             i]
            quality = fields[idx + (self.marker_count-i)*MSL +
                             self.marker_count*MSL + self.marker_count + i]
            self.markers.append(TrackableMarker(None, fields[idx:idx+MSL], tracked, quality))
            idx += MSL
        #Store the point cloud markers
        for i in range(self.marker_count):
            self.ptcld_markers.append(Marker(None,
                                             fields[idx:idx+MSL]))
            idx += MSL

        self.mean_error = float(fields[idx + 2*self.marker_count])

class Marker():
    """Represents a marker"""

    def __init__(self, id, pos):
        """Constructor for a marker object"""
        self.id = id
        self.pos = Position(pos)

class TrackableMarker(Marker):
    """An extended marker with some data related to tracking"""

    def __init__(self, id, pos, tracked, quality):
        """Constructor for a trackable marker"""
        Marker.__init__(self, id, pos)
        self.tracked = tracked
        self.quality = quality

class TrackableState():
    """Represents the dynamic state of a trackable object"""

    def __init__(self, fields):
        """Constructor for a trackable state object"""
        self.id = int(fields[0])
        self.pos = Position(fields[1:4])
        self.qrot = QRot(fields[4:8])
        self.erot = ERot(fields[8:11])

class Trackable():
    """Represents a trackable object"""

    def __init__(self, fields):
        """Constructor for a trackable object"""
        if fields[0].lower() != "trackable":
            raise Exception("You attempted to make a trackable object from " +\
                            "data that does not represent a trackable.")

        self.name = fields[1]
        self.id = int(fields[2])
        self.num_markers = int(fields[3])
        self.markers = []
        idx = 4
        for i in range(self.num_markers):
            self.markers.append(Position(fields[idx:idx+MSL]))
            idx += MSL

class Position():
    """A class representing the x,y,z position of a point in space"""

    def __init__(self, fields):
        """Constructor of for a position object"""

        self.x = float(fields[0])
        self.y = float(fields[1])
        self.z = float(fields[2])

    def toArray(self):
        return np.array([self.x, self.y, self.z])

class QRot():
    """A class representing a rotation using Quaternions"""

    def __init__(self, fields):
        """Constructor for a quaternion-based rotation"""
        self.qx = float(fields[0])
        self.qy = float(fields[1])
        self.qz = float(fields[2])
        self.qw = float(fields[3])

    def toArray(self):
        return np.array([self.qx, self.qy, self.qz, self.qw])

class ERot():
    """A class representing a rotation using Euler angles"""

    def __init__(self, fields):
        """Constructor for an Euler angle-based rotation using the 3-2-1 or
        yaw, pitch, roll sequence"""
        self.yaw = float(fields[0])
        self.pitch = float(fields[1])
        self.roll = float(fields[2])

    def toArray():
        return np.array([self.yaw, self.pitch, self.roll])
