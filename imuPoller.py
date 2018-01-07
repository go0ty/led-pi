#!/usr/bin/python
#
# This class controls the IMU loop that reads the gyro/accel
#
# Adapted from code by https://raw.githubusercontent.com/mwilliams03/BerryIMU @ http://ozzmaker.com/
#

import time
import math
import IMU
import datetime
import os

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070  # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40      # Complementary filter constant

class ImuPoller:
    def __init__(self):
        self.gyroXangle = 0.0
        self.gyroYangle = 0.0
        self.gyroZangle = 0.0
        self.CFangleX = 0.0
        self.CFangleY = 0.0  

        IMU.detectIMU()     # Detect if BerryIMUv1 or BerryIMUv2 is connected.
        IMU.initIMU()       # Initialise the accelerometer, gyroscope and compass

        self.lastReadTime = datetime.datetime.now()

    def getComplimentaryFilter(self):
        # Read the accelerometer,gyroscope and magnetometer values
        ACCx = IMU.readACCx()
        ACCy = IMU.readACCy()
        ACCz = IMU.readACCz()
        GYRx = IMU.readGYRx()
        GYRy = IMU.readGYRy()
        GYRz = IMU.readGYRz()
        MAGx = IMU.readMAGx()
        MAGy = IMU.readMAGy()
        MAGz = IMU.readMAGz()

        # Calculate loop Period(LP). How long between Gyro Reads
        readDelta = datetime.datetime.now() - self.lastReadTime
        self.lastReadTime = datetime.datetime.now()
        LP = readDelta.microseconds/(1000000*1.0)

        # Convert Gyro raw to degrees per second
        rate_gyr_x = GYRx * G_GAIN
        rate_gyr_y = GYRy * G_GAIN
        rate_gyr_z = GYRz * G_GAIN

        # Calculate the angles from the gyro. 
        self.gyroXangle+=rate_gyr_x*LP
        self.gyroYangle+=rate_gyr_y*LP
        self.gyroZangle+=rate_gyr_z*LP

        #Convert Accelerometer values to degrees
        AccXangle = (math.atan2(ACCy,ACCz)+M_PI)*RAD_TO_DEG
        AccYangle = (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG

        # Convert the values to -180 and +180
        AccXangle -= 180.0
        if AccYangle > 90:
            AccYangle -= 270.0
        else:
            AccYangle += 90.0

        # Complementary filter used to combine the accelerometer and gyro values.
        self.CFangleX=AA*(self.CFangleX+rate_gyr_x*LP) +(1 - AA) * AccXangle
        self.CFangleY=AA*(self.CFangleY+rate_gyr_y*LP) +(1 - AA) * AccYangle

        # Calculate heading
        heading = 180 * math.atan2(MAGy,MAGx)/M_PI

        # Only have our heading between 0 and 360
        if heading < 0:
            heading += 360

        # Normalize accelerometer raw values.
        accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
        accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)

        # Calculate pitch and roll
        pitch = math.asin(accXnorm)
        roll = -math.asin(accYnorm/math.cos(pitch))

        # Calculate the new tilt compensated values
        magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)
        magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)

        # Calculate tilt compensated heading
        tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/M_PI
        if tiltCompensatedHeading < 0:
            tiltCompensatedHeading += 360

        if 0:           # showing the angles from the accelerometer
            print ("\033[1;34;40mACCX Angle %5.2f ACCY Angle %5.2f  \033[0m  " % (AccXangle, AccYangle)),

        if 0:           # showing the angles from the gyro
            print ("\033[1;31;40m\tGRYX Angle %5.2f  GYRY Angle %5.2f  GYRZ Angle %5.2f" % (self.gyroXangle,self.gyroYangle,self.gyroZangle)),

        if 0:           # showing the angles from the complementary filter
            print ("\033[1;35;40m   \tCFangleX Angle %5.2f \033[1;36;40m  CFangleY Angle %5.2f \33[1;32;40m" % (self.CFangleX,self.CFangleY)),

        if 0:           # showing the heading
            print ("HEADING  %5.2f \33[1;37;40m tiltCompensatedHeading %5.2f" % (heading,tiltCompensatedHeading))

        return (self.CFangleX, self.CFangleY)

    def getSimpleHeading(self):
        # Get only the Heading
        MAGx = IMU.readMAGx()
        MAGy = IMU.readMAGy()

        # Calculate heading
        heading = 180 * math.atan2(MAGy,MAGx)/M_PI

        # Only have our heading between 0 and 360
        if heading < 0:
            heading += 360

	return heading

    def getAccelZ(self):
	# Detect for jumps
	ACCz = IMU.readACCz()

	return ACCz
