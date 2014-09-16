import roslib; roslib.load_manifest('cob_teacher')
import rospy
import tf
import math
import sys

import os

import tf_conversions.posemath as pm
import PyKDL

from tf.msg import tfMessage
from std_msgs.msg import String 
from geometry_msgs.msg import PoseStamped
from multiprocessing import Process, Lock
import actionlib

from prace_ps_move_controller.msg import move_ps_controller
from prace_moveit_interface.msg import *
from actionlib.msg import *
from frida_driver.msg import *
from moveit_msgs.srv import *

import numpy as np
import copy

from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtGui import QWidget
from PyQt4 import QtGui, QtCore

tflistener = None

class TeacherPlugin():
    def __init__(self):
        raise NotImplementedError( "Should have implemented this" )

    # Returns name of the teaching routine
    def getName(self):
        raise NotImplementedError( "Should have implemented this" )

    # Returns the type this teacher implements
    def getType(self):
        raise NotImplementedError( "Should have implemented this" )
    
    # The actual teachin routine. Returns data of the type this teacher implements, when run as a terminal application.
    def getData(self, name, current_data):
        raise NotImplementedError( "Should have implemented this" )

    # The actual teachin routine. Returns data of the type this teacher implements, when run as a rqt application.
    def getRQTData(self, name):
        raise NotImplementedError( "Should have implemented this" )

    # Returns the qtwidget that should be shown for an instance of this teacher
    def getRQTWidget(self, name):
        raise NotImplementedError( "Should have implemented this" )

    # Optional way to vizualize data (doen't know if this will be ever used) ;)
    def vizualizeData(self):
        raise NotImplementedError( "Should have implemented this" )


class StringInputTeacher(TeacherPlugin):
    def __init__(self):
        pass

    def getType(self):
        return "string"
    
    def getData(self, name):
        datastr = input('Please enter a value for ' + name +  ' :')
        return datastr
    
    def getRQTData(self, name):
        return self.le_edit.text()
    
    def getRQTWidget(self, name, current_data):
        self.le = QtGui.QWidget()
        group_layout = QtGui.QVBoxLayout()
        self.le.setLayout(group_layout)

        self.le_edit = QtGui.QLineEdit()
        self.le_edit.setObjectName(name)
        self.le_edit.setText(str(current_data))
        group_layout.addWidget(self.le_edit)
        return self.le
    
    def getName(self):
        return 'StringInputTeacher'

    def vizualizeData(self):
        print "halloWelt"

class StdStringInputTeacher(TeacherPlugin):
    def __init__(self):
        pass

    def getType(self):
        return "std_msgs/String"
    
    def getData(self, name):
        newstr = String()
        newstr.data = input('Please enter a value for ' + name +  ' :')
        return newstr
    
    def getRQTData(self, name):
        newstr = String()
        newstr.data =  self.le_edit.text()
        return newstr
    
    def getRQTWidget(self, name, current_data):
        self.le = QtGui.QWidget()
        group_layout = QtGui.QVBoxLayout()
        self.le.setLayout(group_layout)

        self.le_edit = QtGui.QLineEdit()
        self.le_edit.setObjectName(name)
        self.le_edit.setText(str(current_data["data"]))
        group_layout.addWidget(self.le_edit)
        return self.le
    
    def getName(self):
        return 'StdStringInputTeacher'

    def vizualizeData(self):
        print "halloWelt"


class FloatInputTeacher(TeacherPlugin):
    def __init__(self):
        pass

    def getName(self):
        return "FloatInputTeacher"

    def getType(self):
        return "float"

    def getData(self, name):
        data_float = float(input("Please enter a value for " + name + " :"))
        return data_float

    def getRQTWidget(self, name, current_data):
        self.le = QtGui.QWidget()
        group_layout = QtGui.QVBoxLayout()
        self.le.setLayout(group_layout)

        self.le_edit = QtGui.QLineEdit()
        self.le_edit.setObjectName(name)
        self.le_edit.setText(str(current_data))
        group_layout.addWidget(self.le_edit)
        return self.le

    def getRQTData(self, name):
        return self.le_edit.text()

class IntInputTeacher(TeacherPlugin):
    def __init__(self):
        pass

    def getName(self):
        return "IntInputTeacher"

    def getType(self):
        return "int"

    def getData(self, name):
        data_int = int(input("Please enter a value for " + name + " :"))
        return data_int

    def getRQTWidget(self, name, current_data):
        self.le = QtGui.QWidget()
        group_layout = QtGui.QVBoxLayout()
        self.le.setLayout(group_layout)

        self.le_edit = QtGui.QLineEdit()
        self.le_edit.setObjectName(name)
        self.le_edit.setText(str(current_data))
        group_layout.addWidget(self.le_edit)
        return self.le

    def getRQTData(self, name):
        return self.le_edit.text()

class BoolInputTeacher(TeacherPlugin):
    def __init__(self):
        pass

    def getName(self):
        return "BoolInputTeacher"

    def getType(self):
        return "bool"

    def getData(self, name):
        data_int = bool(input("Please enter a value for " + name + " :"))
        return data_int

    def getRQTWidget(self, name, current_data):
        self.le = QtGui.QWidget()
        group_layout = QtGui.QVBoxLayout()
        self.le.setLayout(group_layout)

        self.le_edit = QtGui.QLineEdit()
        self.le_edit.setObjectName(name)
        self.le_edit.setText(str(current_data))
        group_layout.addWidget(self.le_edit)
        return self.le

    def getRQTData(self, name):
        return self.le_edit.text()

class PoseInputTeacher(TeacherPlugin):
    def __init__(self):
        pass
    
    def getType(self):
        return "geometry_msgs/PoseStamped"

    def getName(self):
        return "PoseInputTeacher"
    
    def getData(self, name):
        p = PoseStamped()   
        
        xval_pos = float(input('Please enter a position x value for ' + name +  ' :'))
        yval_pos = float(input('Please enter a position y value for ' + name +  ' :'))
        zval_pos = float(input('Please enter a position z value for ' + name +  ' :'))
        
        p.pose.position.x = xval_pos
        p.pose.position.y = yval_pos
        p.pose.position.z = zval_pos
        
        print " "
        
        xval_ori = float(input('Please enter a orientation x value for ' + name +  ' :'))
        yval_ori = float(input('Please enter a orientation y value for ' + name +  ' :'))
        zval_ori = float(input('Please enter a orientation z value for ' + name +  ' :'))
        wval_ori = float(input('Please enter a orientation w value for ' + name +  ' :'))
        
        p.pose.orientation.x = xval_ori
        p.pose.orientation.y = yval_ori
        p.pose.orientation.z = zval_ori
        p.pose.orientation.w = wval_ori

        return p

    def getRQTData(self, name):
        p = PoseStamped()
        p.header.frame_id = self.le_edit_frame_id.text()
        p.pose.position.x = float(self.le_editx.text())
        p.pose.position.y = float(self.le_edity.text())
        p.pose.position.z = float(self.le_editz.text())

        [x,y,z,w] = tf.transformations.quaternion_from_euler(float(self.le_editroll.text()), float(self.le_editpitch.text()), float(self.le_edityaw.text()))

        p.pose.orientation.x = x
        p.pose.orientation.y = y
        p.pose.orientation.z = z
        p.pose.orientation.w = w

        return p
    
    def getRQTWidget(self, name, current_data):
        self.le = QtGui.QWidget()
        grid_layout = QtGui.QGridLayout()
        self.le.setLayout(grid_layout)

        self.le_label_frame_id = QtGui.QLabel("frame_id:")
        self.le_edit_frame_id = QtGui.QLineEdit()
        self.le_edit_frame_id.setObjectName(name)
        #self.le_edit_frame_id.setReadOnly(True)
        self.le_edit_frame_id.setText(str(current_data['header']['frame_id']))
        grid_layout.addWidget(self.le_label_frame_id, 0,0)
        grid_layout.addWidget(self.le_edit_frame_id, 0,1)

        self.le_labelx = QtGui.QLabel("Position X:")
        self.le_editx = QtGui.QLineEdit()
        self.le_editx.setObjectName(name)
        #self.le_editx.setReadOnly(True)
        self.le_editx.setText(str(current_data['pose']['position']['x']))
        grid_layout.addWidget(self.le_labelx, 1,0)
        grid_layout.addWidget(self.le_editx, 1,1)
        
        self.le_labely = QtGui.QLabel("Position Y:")
        self.le_edity = QtGui.QLineEdit()
        self.le_edity.setObjectName(name)
        #self.le_edity.setReadOnly(True)
        self.le_edity.setText(str(current_data['pose']['position']['y']))
        grid_layout.addWidget(self.le_labely, 2,0)
        grid_layout.addWidget(self.le_edity, 2,1)

        self.le_labelz = QtGui.QLabel("Position Z:")
        self.le_editz = QtGui.QLineEdit()
        self.le_editz.setObjectName(name)
        #self.le_editz.setReadOnly(True)
        self.le_editz.setText(str(current_data['pose']['position']['z']))
        grid_layout.addWidget(self.le_labelz, 3,0)
        grid_layout.addWidget(self.le_editz, 3,1)


        quat =  ( current_data['pose']['orientation']['x'],
                current_data['pose']['orientation']['y'],
                current_data['pose']['orientation']['z'],
                current_data['pose']['orientation']['w'])
        [r,p,y] = tf.transformations.euler_from_quaternion(quat)

        self.le_labelroll = QtGui.QLabel("Orientation R:")
        self.le_editroll = QtGui.QLineEdit()
        self.le_editroll.setObjectName(name)
        #self.le_editroll.setReadOnly(True)
        self.le_editroll.setText(str(r))
        grid_layout.addWidget(self.le_labelroll, 1,2)
        grid_layout.addWidget(self.le_editroll, 1,3)

        self.le_labelpitch = QtGui.QLabel("Orientation P:")
        self.le_editpitch = QtGui.QLineEdit()
        self.le_editpitch.setObjectName(name)
        self.le_editpitch.setText(str(p))
        #self.le_editpitch.setReadOnly(True)
        grid_layout.addWidget(self.le_labelpitch, 2,2)
        grid_layout.addWidget(self.le_editpitch, 2,3)

        self.le_labelyaw = QtGui.QLabel("Orientation Y:")
        self.le_edityaw = QtGui.QLineEdit()
        self.le_edityaw.setObjectName(name)
        self.le_edityaw.setText(str(y))
        #self.le_edityaw.setReadOnly(True)
        grid_layout.addWidget(self.le_labelyaw, 3,2)
        grid_layout.addWidget(self.le_edityaw, 3,3)

        return self.le


class PoseTouchupTeacher(TeacherPlugin):
    current_pose = PoseStamped()
    def __init__(self):
        global tflistener
        if tflistener is None:
            tflistener = tf.TransformListener()
        self.lr = tflistener
        pass

    def callback(self, data):
        self.current_pose = data

    def getName(self):
        return "PoseTouchupTeacher"

    def getType(self):
        return "geometry_msgs/PoseStamped"

    def getData(self, name):
        return self.current_pose

    def getRQTData(self, name):
        p = PoseStamped()
        p.header.frame_id = str(self.le_edit_frame_id.text())

        p.pose.position.x = float(self.le_editx.text())
        p.pose.position.y = float(self.le_edity.text())
        p.pose.position.z = float(self.le_editz.text())

        p.pose.orientation.x = float(self.le_editori_x.text())
        p.pose.orientation.y = float(self.le_editori_y.text())
        p.pose.orientation.z = float(self.le_editori_z.text())
        p.pose.orientation.w = float(self.le_editori_w.text())

        return p
        
    def getRQTWidget(self, name, current_data, target_frame):
        self.target_frame = str(target_frame)

        self.le = QtGui.QWidget()
        grid_layout = QtGui.QGridLayout()
        self.le.setLayout(grid_layout)

        self.le_label_frame_id = QtGui.QLabel("frame_id:")
        self.le_edit_frame_id = QtGui.QLineEdit()
        self.le_edit_frame_id.setObjectName(name)
        self.le_edit_frame_id.setReadOnly(False)
        self.le_edit_frame_id.setText("")
        grid_layout.addWidget(self.le_label_frame_id, 2,0)
        grid_layout.addWidget(self.le_edit_frame_id, 2,1)

        self.le_labelx = QtGui.QLabel("Position X:")
        self.le_editx = QtGui.QLineEdit()
        self.le_editx.setObjectName(name)
        self.le_editx.setReadOnly(True)
        #self.le_editx.setText(str(current_data['pose']['position']['x']))
        self.le_editx.setText(str(""))
        grid_layout.addWidget(self.le_labelx, 3,0)
        grid_layout.addWidget(self.le_editx, 3,1)
        
        self.le_labely = QtGui.QLabel("Position Y:")
        self.le_edity = QtGui.QLineEdit()
        self.le_edity.setObjectName(name)
        self.le_edity.setReadOnly(True)
        #self.le_edity.setText(str(current_data['pose']['position']['y']))
        self.le_edity.setText(str(""))
        grid_layout.addWidget(self.le_labely, 4,0)
        grid_layout.addWidget(self.le_edity, 4,1)

        self.le_labelz = QtGui.QLabel("Position Z:")
        self.le_editz = QtGui.QLineEdit()
        self.le_editz.setObjectName(name)
        self.le_editz.setReadOnly(True)
        #self.le_editz.setText(str(current_data['pose']['position']['z']))
        self.le_editz.setText(str(""))
        grid_layout.addWidget(self.le_labelz, 5,0)
        grid_layout.addWidget(self.le_editz, 5,1)

        [x,y,z,w] = current_data['pose']['orientation'].values()

        self.le_labelori_x = QtGui.QLabel("Orientation X:")
        self.le_editori_x = QtGui.QLineEdit()
        self.le_editori_x.setObjectName(name)
        self.le_editori_x.setReadOnly(True)
        #self.le_editori_x.setText(str(x))
        self.le_editori_x.setText(str(""))
        grid_layout.addWidget(self.le_labelori_x, 2,2)
        grid_layout.addWidget(self.le_editori_x, 2,3)

        self.le_labelori_y = QtGui.QLabel("Orientation Y:")
        self.le_editori_y = QtGui.QLineEdit()
        self.le_editori_y.setObjectName(name)
        #self.le_editori_y.setText(str(y))
        self.le_editori_y.setText(str(""))
        self.le_editori_y.setReadOnly(True)
        grid_layout.addWidget(self.le_labelori_y, 3,2)
        grid_layout.addWidget(self.le_editori_y, 3,3)

        self.le_labelori_z = QtGui.QLabel("Orientation Z:")
        self.le_editori_z = QtGui.QLineEdit()
        self.le_editori_z.setObjectName(name)
        #self.le_editori_z.setText(str(z))
        self.le_editori_z.setText(str(""))
        self.le_editori_z.setReadOnly(True)
        grid_layout.addWidget(self.le_labelori_z, 4,2)
        grid_layout.addWidget(self.le_editori_z, 4,3)

        self.le_labelori_w = QtGui.QLabel("Orientation W:")
        self.le_editori_w = QtGui.QLineEdit()
        self.le_editori_w.setObjectName(name)
        #self.le_editori_w.setText(str(w))
        self.le_editori_w.setText(str(""))
        self.le_editori_w.setReadOnly(True)
        grid_layout.addWidget(self.le_labelori_w, 5,2)
        grid_layout.addWidget(self.le_editori_w, 5,3)

        self.le_teach_button = QtGui.QPushButton("Teach Now")
        grid_layout.addWidget(self.le_teach_button, 6,3)
        self.le_teach_button.connect(self.le_teach_button, QtCore.SIGNAL('clicked()'), self.updateRQTValues)

        return self.le

    def updateRQTValues(self):
        current_time = rospy.Time.now()
        try:
            print "wait for transform from: ", str(self.le_edit_frame_id.text()), " to: ", self.target_frame
            self.lr.waitForTransform(str(self.le_edit_frame_id.text()), self.target_frame, current_time, rospy.Duration(2.0))
            (trans, rot) = self.lr.lookupTransform(str(self.le_edit_frame_id.text()), self.target_frame, current_time)

            self.le_editx.setText(str( trans[0]))
            self.le_edity.setText(str( trans[1]))
            self.le_editz.setText(str( trans[2]))

            self.le_editori_x.setText(str(rot[0]))
            self.le_editori_y.setText(str(rot[1]))
            self.le_editori_z.setText(str(rot[2]))
            self.le_editori_w.setText(str(rot[3]))
        except tf.Exception as e:
            print "Execption: ", e
            pass

class PositionTouchupTeacher(TeacherPlugin):
    current_pose = PoseStamped()
    def __init__(self):
        global tflistener
        if tflistener is None:
            tflistener = tf.TransformListener()
        self.lr = tflistener
        pass

    def callback(self, data):
        self.current_pose = data

    def getName(self):
        return "PositionTouchupTeacher"

    def getType(self):
        return "geometry_msgs/PoseStamped"

    def getData(self, name):
        return self.current_pose

    def getRQTData(self, name):
        p = PoseStamped()
        p.header.frame_id = str(self.le_edit_frame_id.text())

        p.pose.position.x = float(self.le_editx.text())
        p.pose.position.y = float(self.le_edity.text())
        p.pose.position.z = float(self.le_editz.text())

        p.pose.orientation.x = 0.0
        p.pose.orientation.y = 0.0
        p.pose.orientation.z = 0.0
        p.pose.orientation.w = 1.0

        return p
        
    def getRQTWidget(self, name, current_data, target_frame):
        self.target_frame = str(target_frame)

        self.le = QtGui.QWidget()
        grid_layout = QtGui.QGridLayout()
        self.le.setLayout(grid_layout)

        self.le_label_frame_id = QtGui.QLabel("frame_id:")
        self.le_edit_frame_id = QtGui.QLineEdit()
        self.le_edit_frame_id.setObjectName(name)
        self.le_edit_frame_id.setReadOnly(False)
        self.le_edit_frame_id.setText("")
        grid_layout.addWidget(self.le_label_frame_id, 2,0)
        grid_layout.addWidget(self.le_edit_frame_id, 2,1)

        self.le_labelx = QtGui.QLabel("Position X:")
        self.le_editx = QtGui.QLineEdit()
        self.le_editx.setObjectName(name)
        self.le_editx.setReadOnly(True)
        #self.le_editx.setText(str(current_data['pose']['position']['x']))
        self.le_editx.setText(str(""))
        grid_layout.addWidget(self.le_labelx, 3,0)
        grid_layout.addWidget(self.le_editx, 3,1)
        
        self.le_labely = QtGui.QLabel("Position Y:")
        self.le_edity = QtGui.QLineEdit()
        self.le_edity.setObjectName(name)
        self.le_edity.setReadOnly(True)
        #self.le_edity.setText(str(current_data['pose']['position']['y']))
        self.le_edity.setText(str(""))
        grid_layout.addWidget(self.le_labely, 4,0)
        grid_layout.addWidget(self.le_edity, 4,1)

        self.le_labelz = QtGui.QLabel("Position Z:")
        self.le_editz = QtGui.QLineEdit()
        self.le_editz.setObjectName(name)
        self.le_editz.setReadOnly(True)
        #self.le_editz.setText(str(current_data['pose']['position']['z']))
        self.le_editz.setText(str(""))
        grid_layout.addWidget(self.le_labelz, 5,0)
        grid_layout.addWidget(self.le_editz, 5,1)

        # [x,y,z,w] = current_data['pose']['orientation'].values()

        # self.le_labelori_x = QtGui.QLabel("Orientation X:")
        # self.le_editori_x = QtGui.QLineEdit()
        # self.le_editori_x.setObjectName(name)
        # self.le_editori_x.setReadOnly(True)
        # #self.le_editori_x.setText(str(x))
        # self.le_editori_x.setText(str(""))
        # grid_layout.addWidget(self.le_labelori_x, 2,2)
        # grid_layout.addWidget(self.le_editori_x, 2,3)

        # self.le_labelori_y = QtGui.QLabel("Orientation Y:")
        # self.le_editori_y = QtGui.QLineEdit()
        # self.le_editori_y.setObjectName(name)
        # #self.le_editori_y.setText(str(y))
        # self.le_editori_y.setText(str(""))
        # self.le_editori_y.setReadOnly(True)
        # grid_layout.addWidget(self.le_labelori_y, 3,2)
        # grid_layout.addWidget(self.le_editori_y, 3,3)

        # self.le_labelori_z = QtGui.QLabel("Orientation Z:")
        # self.le_editori_z = QtGui.QLineEdit()
        # self.le_editori_z.setObjectName(name)
        # #self.le_editori_z.setText(str(z))
        # self.le_editori_z.setText(str(""))
        # self.le_editori_z.setReadOnly(True)
        # grid_layout.addWidget(self.le_labelori_z, 4,2)
        # grid_layout.addWidget(self.le_editori_z, 4,3)

        # self.le_labelori_w = QtGui.QLabel("Orientation W:")
        # self.le_editori_w = QtGui.QLineEdit()
        # self.le_editori_w.setObjectName(name)
        # #self.le_editori_w.setText(str(w))
        # self.le_editori_w.setText(str(""))
        # self.le_editori_w.setReadOnly(True)
        # grid_layout.addWidget(self.le_labelori_w, 5,2)
        # grid_layout.addWidget(self.le_editori_w, 5,3)

        self.le_teach_button = QtGui.QPushButton("Teach Now")
        grid_layout.addWidget(self.le_teach_button, 6,2)
        self.le_teach_button.connect(self.le_teach_button, QtCore.SIGNAL('clicked()'), self.updateRQTValues)

        return self.le

    def updateRQTValues(self):
        current_time = rospy.Time.now()
        try:
            print "wait for transform from: ", str(self.le_edit_frame_id.text()), " to: ", self.target_frame
            self.lr.waitForTransform(str(self.le_edit_frame_id.text()), self.target_frame, current_time, rospy.Duration(2.0))
            (trans, rot) = self.lr.lookupTransform(str(self.le_edit_frame_id.text()), self.target_frame, current_time)

            self.le_editx.setText(str( trans[0]))
            self.le_edity.setText(str( trans[1]))
            self.le_editz.setText(str( trans[2]))

            #self.le_editori_x.setText(str(rot[0]))
            #self.le_editori_y.setText(str(rot[1]))
            #self.le_editori_z.setText(str(rot[2]))
            #self.le_editori_w.setText(str(rot[3]))
        except tf.Exception as e:
            print "Execption: ", e
            pass

class PoseTeachInHandleTeacher(TeacherPlugin):
    current_pose_gripper = PoseStamped()
    current_pose_raspberry = PoseStamped()
    ps_move_triangle_pressed = False 
    ps_move_circle_pressed = False 

    def __init__(self):
        # start listener for pose 
        self.listener_gripper_pose = rospy.Subscriber("/corrected_handle_pose_gripper", PoseStamped, self.callback_gripper)
        self.listener_rasperry_pose = rospy.Subscriber("/corrected_handle_pose_raspberry", PoseStamped, self.callback_raspberry)
        self.ps_move_listener = rospy.Subscriber("/button_value_ps_move_controller", move_ps_controller, self.callback_ps_move_button)
        pass

    def callback_gripper(self, data):
        self.current_pose_gripper = data

    def callback_raspberry(self, data):
        self.current_pose_raspberry = data

    def callback_ps_move_button(self, data):
        if(data.button_value == 16):
            self.ps_move_triangle_pressed = True
        elif(self.ps_move_triangle_pressed == True):
            # get current handle gripper pose
            self.ps_move_triangle_pressed = False     
            self.updateRQTValues_gripper()
        
        if(data.button_value == 32):
            self.ps_move_circle_pressed = True
        elif(self.ps_move_circle_pressed == True):
            # get current handle raspberry pose
            self.ps_move_circle_pressed = False     
            self.updateRQTValues_raspberry()

    def getName(self):
        return "PoseTeachInHandleTeacher"

    def getType(self):
        return "geometry_msgs/PoseStamped"

    def getData(self, name):
        #any_number = input('Please enter any # to stamp current pose: ')
        raw_input('Press any key to stamp current pose:')
        print self.current_pose 
        return self.current_pose

    def getRQTData(self, name):
        p = PoseStamped()
        p.header.frame_id = str(self.le_edit_frame_id.text())

        p.pose.orientation.x = float(self.le_editori_x.text())
        p.pose.orientation.y = float(self.le_editori_y.text())
        p.pose.orientation.z = float(self.le_editori_z.text())
        p.pose.orientation.w = float(self.le_editori_w.text())

        p.pose.position.x = float(self.le_editx.text())
        p.pose.position.y = float(self.le_edity.text())
        p.pose.position.z = float(self.le_editz.text())

        return p;
        
    def getRQTWidget(self, name, current_data):    
        
        self.le = QtGui.QWidget()
        grid_layout = QtGui.QGridLayout()
        self.le.setLayout(grid_layout)

        #if(rospy.get_param('scene_already_calibrated') == False):
        #    print "We need to calibrate this scene first"
        #    # build calibration button
        #    self.calibration_info = QtGui.QLabel("Calibrate scene first: ")
        #    grid_layout.addWidget(self.calibration_info, 0,0)

        #    self.le_calibration_button = QtGui.QPushButton("Calibrate Scene Now")
        #    grid_layout.addWidget(self.le_calibration_button, 0,3)
        #    self.le_calibration_button.connect(self.le_calibration_button, QtCore.SIGNAL('clicked()'), self.calibrateScene)
    
        self.le_label_frame_id = QtGui.QLabel("frame_id:")
        self.le_edit_frame_id = QtGui.QLineEdit()
        self.le_edit_frame_id.setObjectName(name)
        self.le_edit_frame_id.setReadOnly(True)
        #self.le_edit_frame_id.setText(str(current_data['header']['frame_id']))
        self.le_edit_frame_id.setText(str(""))
        grid_layout.addWidget(self.le_label_frame_id, 2,0)
        grid_layout.addWidget(self.le_edit_frame_id, 2,1)

        self.le_labelx = QtGui.QLabel("Position X:")
        self.le_editx = QtGui.QLineEdit()
        self.le_editx.setObjectName(name)
        self.le_editx.setReadOnly(True)
        #self.le_editx.setText(str(current_data['pose']['position']['x']))
        self.le_editx.setText(str(""))
        grid_layout.addWidget(self.le_labelx, 3,0)
        grid_layout.addWidget(self.le_editx, 3,1)
        
        self.le_labely = QtGui.QLabel("Position Y:")
        self.le_edity = QtGui.QLineEdit()
        self.le_edity.setObjectName(name)
        self.le_edity.setReadOnly(True)
        #self.le_edity.setText(str(current_data['pose']['position']['y']))
        self.le_edity.setText(str(""))
        grid_layout.addWidget(self.le_labely, 4,0)
        grid_layout.addWidget(self.le_edity, 4,1)

        self.le_labelz = QtGui.QLabel("Position Z:")
        self.le_editz = QtGui.QLineEdit()
        self.le_editz.setObjectName(name)
        self.le_editz.setReadOnly(True)
        #self.le_editz.setText(str(current_data['pose']['position']['z']))
        self.le_editz.setText(str(""))
        grid_layout.addWidget(self.le_labelz, 5,0)
        grid_layout.addWidget(self.le_editz, 5,1)


        [x,y,z,w] = current_data['pose']['orientation'].values()

        self.le_labelori_x = QtGui.QLabel("Orientation X:")
        self.le_editori_x = QtGui.QLineEdit()
        self.le_editori_x.setObjectName(name)
        self.le_editori_x.setReadOnly(True)
        #self.le_editori_x.setText(str(x))
        self.le_editori_x.setText(str(""))
        grid_layout.addWidget(self.le_labelori_x, 2,2)
        grid_layout.addWidget(self.le_editori_x, 2,3)

        self.le_labelori_y = QtGui.QLabel("Orientation Y:")
        self.le_editori_y = QtGui.QLineEdit()
        self.le_editori_y.setObjectName(name)
        #self.le_editori_y.setText(str(y))
        self.le_editori_y.setText(str(""))
        self.le_editori_y.setReadOnly(True)
        grid_layout.addWidget(self.le_labelori_y, 3,2)
        grid_layout.addWidget(self.le_editori_y, 3,3)

        self.le_labelori_z = QtGui.QLabel("Orientation Z:")
        self.le_editori_z = QtGui.QLineEdit()
        self.le_editori_z.setObjectName(name)
        #self.le_editori_z.setText(str(z))
        self.le_editori_z.setText(str(""))
        self.le_editori_z.setReadOnly(True)
        grid_layout.addWidget(self.le_labelori_z, 4,2)
        grid_layout.addWidget(self.le_editori_z, 4,3)

        self.le_labelori_w = QtGui.QLabel("Orientation W:")
        self.le_editori_w = QtGui.QLineEdit()
        self.le_editori_w.setObjectName(name)
        #self.le_editori_w.setText(str(w))
        self.le_editori_w.setText(str(""))
        self.le_editori_w.setReadOnly(True)
        grid_layout.addWidget(self.le_labelori_w, 5,2)
        grid_layout.addWidget(self.le_editori_w, 5,3)

        self.le_teach_button = QtGui.QPushButton("Teach Gripper Pose")
        grid_layout.addWidget(self.le_teach_button, 6,3)
        self.le_teach_button.connect(self.le_teach_button, QtCore.SIGNAL('clicked()'), self.updateRQTValues_gripper)

        self.le_teach_button = QtGui.QPushButton("Teach Raspberry Pose")
        grid_layout.addWidget(self.le_teach_button, 7,3)
        self.le_teach_button.connect(self.le_teach_button, QtCore.SIGNAL('clicked()'), self.updateRQTValues_raspberry)

        return self.le

    def updateRQTValues_gripper(self):

        self.le_edit_frame_id.setText(str(self.current_pose_gripper.header.frame_id))
        self.le_editx.setText(str( self.current_pose_gripper.pose.position.x))
        self.le_edity.setText(str( self.current_pose_gripper.pose.position.y))
        self.le_editz.setText(str( self.current_pose_gripper.pose.position.z))

        self.le_editori_x.setText(str(self.current_pose_gripper.pose.orientation.x))
        self.le_editori_y.setText(str(self.current_pose_gripper.pose.orientation.y))
        self.le_editori_z.setText(str(self.current_pose_gripper.pose.orientation.z))
        self.le_editori_w.setText(str(self.current_pose_gripper.pose.orientation.w))

    def updateRQTValues_raspberry(self):

        self.le_edit_frame_id.setText(str(self.current_pose_raspberry.header.frame_id))
        self.le_editx.setText(str( self.current_pose_raspberry.pose.position.x))
        self.le_edity.setText(str( self.current_pose_raspberry.pose.position.y))
        self.le_editz.setText(str( self.current_pose_raspberry.pose.position.z))

        self.le_editori_x.setText(str(self.current_pose_raspberry.pose.orientation.x))
        self.le_editori_y.setText(str(self.current_pose_raspberry.pose.orientation.y))
        self.le_editori_z.setText(str(self.current_pose_raspberry.pose.orientation.z))
        self.le_editori_w.setText(str(self.current_pose_raspberry.pose.orientation.w))


class PalettePoseTeacher(TeacherPlugin):
    current_handle_pose = PoseStamped()
    first_pose = PoseStamped()
    second_pose = PoseStamped() 
    third_pose = PoseStamped()
    current_iterate = 0
    ps_move_button_pressed = False
    calls = 0

    def __init__(self):
        # start listener for pose 
        self.handle_listener = rospy.Subscriber("/corrected_handle_pose_gripper", PoseStamped, self.callback_handle_pose)
        self.ps_move_listener = rospy.Subscriber("/button_value_ps_move_controller", move_ps_controller, self.callback_ps_move_button)
        global tflistener
        if tflistener is None:
            tflistener = tf.TransformListener()
        self.lr = tflistener
        rospy.sleep(0.1)
        pass

    def callback_handle_pose(self, data):
        self.current_handle_pose = data

    def callback_ps_move_button(self, data):
	if(data.button_value == 16):
		self.ps_move_button_pressed = True
	elif(self.ps_move_button_pressed == True):
		self.ps_move_button_pressed = False		
		self.updateRQTValues(0, True)
		#self.calls = self.calls + 1
		#self.dummy()	

    def dummy(self):
	print "called" + str(self.calls)
			
    def getName(self):
        return "PalettePoseTeacher"

    def getType(self):
        return "geometry_msgs/PoseStamped"

    def getData(self, name):
        pass

    def getRQTData(self, name):
        result = PoseStamped()
        ################ Compute Pallete Pose ##################################
        result = self.getPaletteFrameFromThreePoses(self.first_pose, self.second_pose, self.third_pose)
        ########################
        return result

    def getRQTWidget(self, name, current_data):    
        
        row_start = 0 
        column_start = 0

        self.le = QtGui.QWidget()
        grid_layout = QtGui.QGridLayout()
        self.le.setLayout(grid_layout)

        self.le_label_title = QtGui.QLabel("Teaching Palette Poses")
        grid_layout.addWidget(self.le_label_title, row_start + 1,0)
##############################################################################################
#First Pose Widget:
##############################################################################################
        clicked = QtCore.pyqtSignal()

        self.le_teach_button_first = QtGui.QPushButton("Teach First Pose")
        grid_layout.addWidget(self.le_teach_button_first, row_start + 2, column_start + 1)
        self.le_teach_button_first.clicked.connect(lambda: self.updateRQTValues(1, False))
        #self.le_teach_button_first.connect(self.le_teach_button_first, QtCore.SIGNAL('clicked()'), self.updateRQTValues)

        self.le_label_frame_id_first = QtGui.QLabel("frame_id:")
        self.le_edit_frame_id_first = QtGui.QLineEdit()
        self.le_edit_frame_id_first.setObjectName(name)
        self.le_edit_frame_id_first.setReadOnly(True)
        #self.le_edit_frame_id.setText(str(current_data['header']['frame_id']))
        self.le_edit_frame_id_first.setText(str(""))
        grid_layout.addWidget(self.le_label_frame_id_first, row_start + 3, column_start + 0)
        grid_layout.addWidget(self.le_edit_frame_id_first, row_start + 3, column_start + 1)

        self.le_labelx_first = QtGui.QLabel("Position X:")
        self.le_editx_first = QtGui.QLineEdit()
        self.le_editx_first.setObjectName(name)
        self.le_editx_first.setReadOnly(True)
        #self.le_editx.setText(str(current_data['pose']['position']['x']))
        self.le_editx_first.setText(str(""))
        grid_layout.addWidget(self.le_labelx_first, row_start + 4, column_start +  0)
        grid_layout.addWidget(self.le_editx_first, row_start + 4, column_start + 1)
        
        self.le_labely_first = QtGui.QLabel("Position Y:")
        self.le_edity_first = QtGui.QLineEdit()
        self.le_edity_first.setObjectName(name)
        self.le_edity_first.setReadOnly(True)
        #self.le_edity.setText(str(current_data['pose']['position']['y']))
        self.le_edity_first.setText(str(""))
        grid_layout.addWidget(self.le_labely_first, row_start + 5, column_start + 0)
        grid_layout.addWidget(self.le_edity_first, row_start + 5, column_start + 1 )

        self.le_labelz_first = QtGui.QLabel("Position Z:")
        self.le_editz_first = QtGui.QLineEdit()
        self.le_editz_first.setObjectName(name)
        self.le_editz_first.setReadOnly(True)
        #self.le_editz.setText(str(current_data['pose']['position']['z']))
        self.le_editz_first.setText(str(""))
        grid_layout.addWidget(self.le_labelz_first, row_start + 6, column_start + 0)
        grid_layout.addWidget(self.le_editz_first, row_start + 6, column_start + 1)

        [x,y,z,w] = current_data['pose']['orientation'].values()

        #self.le_labelori_x_first = QtGui.QLabel("Orientation X:")
        #self.le_editori_x_first = QtGui.QLineEdit()
        #self.le_editori_x_first.setObjectName(name)
        #self.le_editori_x_first.setReadOnly(True)
        ##self.le_editori_x.setText(str(x))
        #self.le_editori_x_first.setText(str(""))
        #grid_layout.addWidget(self.le_labelori_x_first, row_start + 7, column_start + 0)
        #grid_layout.addWidget(self.le_editori_x_first, row_start + 7, column_start + 1)

        #self.le_labelori_y_first = QtGui.QLabel("Orientation Y:")
        #self.le_editori_y_first = QtGui.QLineEdit()
        #self.le_editori_y_first.setObjectName(name)
        ##self.le_editori_y.setText(str(y))
        #self.le_editori_y_first.setText(str(""))
        #self.le_editori_y_first.setReadOnly(True)
        #grid_layout.addWidget(self.le_labelori_y_first, row_start + 8, column_start + 0)
        #grid_layout.addWidget(self.le_editori_y_first, row_start + 8, column_start + 1)

        #self.le_labelori_z_first = QtGui.QLabel("Orientation Z:")
        #self.le_editori_z_first = QtGui.QLineEdit()
        #self.le_editori_z_first.setObjectName(name)
        ##self.le_editori_z.setText(str(z))
        #self.le_editori_z_first.setText(str(""))
        #self.le_editori_z_first.setReadOnly(True)
        #grid_layout.addWidget(self.le_labelori_z_first, row_start + 9,column_start + 0)
        #grid_layout.addWidget(self.le_editori_z_first, row_start + 9,column_start + 1)

        #self.le_labelori_w_first = QtGui.QLabel("Orientation W:")
        #self.le_editori_w_first = QtGui.QLineEdit()
        #self.le_editori_w_first.setObjectName(name)
        ##self.le_editori_w.setText(str(w))
        #self.le_editori_w_first.setText(str(""))
        #self.le_editori_w_first.setReadOnly(True)
        #grid_layout.addWidget(self.le_labelori_w_first, row_start + 10, column_start + 0)
        #grid_layout.addWidget(self.le_editori_w_first, row_start + 10,column_start + 1)

##############################################################################################
#Second Pose Widget:
##############################################################################################
        column_start = 2
        self.le_teach_button_second = QtGui.QPushButton("Teach Second Pose")
        grid_layout.addWidget(self.le_teach_button_second, row_start + 2, column_start + 1)
        self.le_teach_button_second.clicked.connect(lambda: self.updateRQTValues(2, False))
        #self.le_teach_button_second.connect(self.le_teach_button_second, QtCore.SIGNAL('clicked()'), self.updateRQTValues)
   
        self.le_label_frame_id_second = QtGui.QLabel("frame_id:")
        self.le_edit_frame_id_second = QtGui.QLineEdit()
        self.le_edit_frame_id_second.setObjectName(name)
        self.le_edit_frame_id_second.setReadOnly(True)
        #self.le_edit_frame_id.setText(str(current_data['header']['frame_id']))
        self.le_edit_frame_id_second.setText(str(""))
        grid_layout.addWidget(self.le_label_frame_id_second, row_start + 3, column_start + 0)
        grid_layout.addWidget(self.le_edit_frame_id_second, row_start + 3, column_start + 1)

        self.le_labelx_second = QtGui.QLabel("Position X:")
        self.le_editx_second = QtGui.QLineEdit()
        self.le_editx_second.setObjectName(name)
        self.le_editx_second.setReadOnly(True)
        #self.le_editx.setText(str(current_data['pose']['position']['x']))
        self.le_editx_second.setText(str(""))
        grid_layout.addWidget(self.le_labelx_second, row_start + 4, column_start + 0)
        grid_layout.addWidget(self.le_editx_second, row_start + 4, column_start + 1)
        
        self.le_labely_second = QtGui.QLabel("Position Y:")
        self.le_edity_second = QtGui.QLineEdit()
        self.le_edity_second.setObjectName(name)
        self.le_edity_second.setReadOnly(True)
        #self.le_edity.setText(str(current_data['pose']['position']['y']))
        self.le_edity_second.setText(str(""))
        grid_layout.addWidget(self.le_labely_second, row_start + 5, column_start + 0)
        grid_layout.addWidget(self.le_edity_second, row_start + 5, column_start + 1 )

        self.le_labelz_second = QtGui.QLabel("Position Z:")
        self.le_editz_second = QtGui.QLineEdit()
        self.le_editz_second.setObjectName(name)
        self.le_editz_second.setReadOnly(True)
        #self.le_editz.setText(str(current_data['pose']['position']['z']))
        self.le_editz_second.setText(str(""))
        grid_layout.addWidget(self.le_labelz_second, row_start + 6, column_start + 0)
        grid_layout.addWidget(self.le_editz_second, row_start + 6, column_start + 1)

        [x,y,z,w] = current_data['pose']['orientation'].values()

        #self.le_labelori_x_second = QtGui.QLabel("Orientation X:")
        #self.le_editori_x_second = QtGui.QLineEdit()
        #self.le_editori_x_second.setObjectName(name)
        #self.le_editori_x_second.setReadOnly(True)
        ##self.le_editori_x.setText(str(x))
        #self.le_editori_x_second.setText(str(""))
        #grid_layout.addWidget(self.le_labelori_x_second, row_start + 7, column_start + 0)
        #grid_layout.addWidget(self.le_editori_x_second, row_start + 7, column_start + 1)

        #self.le_labelori_y_second = QtGui.QLabel("Orientation Y:")
        #self.le_editori_y_second = QtGui.QLineEdit()
        #self.le_editori_y_second.setObjectName(name)
        ##self.le_editori_y.setText(str(y))
        #self.le_editori_y_second.setText(str(""))
        #self.le_editori_y_second.setReadOnly(True)
        #grid_layout.addWidget(self.le_labelori_y_second, row_start + 8, column_start + 0)
        #grid_layout.addWidget(self.le_editori_y_second, row_start + 8, column_start + 1)

        #self.le_labelori_z_second = QtGui.QLabel("Orientation Z:")
        #self.le_editori_z_second = QtGui.QLineEdit()
        #self.le_editori_z_second.setObjectName(name)
        ##self.le_editori_z.setText(str(z))
        #self.le_editori_z_second.setText(str(""))
        #self.le_editori_z_second.setReadOnly(True)
        #grid_layout.addWidget(self.le_labelori_z_second, row_start + 9,column_start + 0)
        #grid_layout.addWidget(self.le_editori_z_second, row_start + 9,column_start + 1)

        #self.le_labelori_w_second = QtGui.QLabel("Orientation W:")
        #self.le_editori_w_second = QtGui.QLineEdit()
        #self.le_editori_w_second.setObjectName(name)
        ##self.le_editori_w.setText(str(w))
        #self.le_editori_w_second.setText(str(""))
        #self.le_editori_w_second.setReadOnly(True)
        #grid_layout.addWidget(self.le_labelori_w_second, row_start + 10, column_start + 0)
        #grid_layout.addWidget(self.le_editori_w_second, row_start + 10,column_start + 1)
          
##############################################################################################
#Third Pose Widget:
##############################################################################################
        column_start = 4
        self.le_teach_button_third = QtGui.QPushButton("Teach Third Pose")
        grid_layout.addWidget(self.le_teach_button_third, row_start + 2, column_start + 1)
        self.le_teach_button_third.clicked.connect(lambda: self.updateRQTValues(3, False))
        #self.le_teach_button_third.connect(self.le_teach_button_third, QtCore.SIGNAL('clicked()'), self.updateRQTValues)
   
        self.le_label_frame_id_third = QtGui.QLabel("frame_id:")
        self.le_edit_frame_id_third = QtGui.QLineEdit()
        self.le_edit_frame_id_third.setObjectName(name)
        self.le_edit_frame_id_third.setReadOnly(True)
        #self.le_edit_frame_id.setText(str(current_data['header']['frame_id']))
        self.le_edit_frame_id_third.setText(str(""))
        grid_layout.addWidget(self.le_label_frame_id_third, row_start + 3, column_start + 0)
        grid_layout.addWidget(self.le_edit_frame_id_third, row_start + 3, column_start + 1)

        self.le_labelx_third = QtGui.QLabel("Position X:")
        self.le_editx_third = QtGui.QLineEdit()
        self.le_editx_third.setObjectName(name)
        self.le_editx_third.setReadOnly(True)
        #self.le_editx.setText(str(current_data['pose']['position']['x']))
        self.le_editx_third.setText(str(""))
        grid_layout.addWidget(self.le_labelx_third, row_start + 4, column_start + 0)
        grid_layout.addWidget(self.le_editx_third, row_start + 4, column_start + 1)
        
        self.le_labely_third = QtGui.QLabel("Position Y:")
        self.le_edity_third = QtGui.QLineEdit()
        self.le_edity_third.setObjectName(name)
        self.le_edity_third.setReadOnly(True)
        #self.le_edity.setText(str(current_data['pose']['position']['y']))
        self.le_edity_third.setText(str(""))
        grid_layout.addWidget(self.le_labely_third, row_start + 5, column_start + 0)
        grid_layout.addWidget(self.le_edity_third, row_start + 5, column_start + 1 )

        self.le_labelz_third = QtGui.QLabel("Position Z:")
        self.le_editz_third = QtGui.QLineEdit()
        self.le_editz_third.setObjectName(name)
        self.le_editz_third.setReadOnly(True)
        #self.le_editz.setText(str(current_data['pose']['position']['z']))
        self.le_editz_third.setText(str(""))
        grid_layout.addWidget(self.le_labelz_third, row_start + 6, column_start + 0)
        grid_layout.addWidget(self.le_editz_third, row_start + 6, column_start + 1)

        [x,y,z,w] = current_data['pose']['orientation'].values()

        #self.le_labelori_x_third = QtGui.QLabel("Orientation X:")
        #self.le_editori_x_third = QtGui.QLineEdit()
        #self.le_editori_x_third.setObjectName(name)
        #self.le_editori_x_third.setReadOnly(True)
        ##self.le_editori_x.setText(str(x))
        #self.le_editori_x_third.setText(str(""))
        #grid_layout.addWidget(self.le_labelori_x_third, row_start + 7, column_start + 0)
        #grid_layout.addWidget(self.le_editori_x_third, row_start + 7, column_start + 1)

        #self.le_labelori_y_third = QtGui.QLabel("Orientation Y:")
        #self.le_editori_y_third = QtGui.QLineEdit()
        #self.le_editori_y_third.setObjectName(name)
        ##self.le_editori_y.setText(str(y))
        #self.le_editori_y_third.setText(str(""))
        #self.le_editori_y_third.setReadOnly(True)
        #grid_layout.addWidget(self.le_labelori_y_third, row_start + 8, column_start + 0)
        #grid_layout.addWidget(self.le_editori_y_third, row_start + 8, column_start + 1)

        #self.le_labelori_z_third = QtGui.QLabel("Orientation Z:")
        #self.le_editori_z_third = QtGui.QLineEdit()
        #self.le_editori_z_third.setObjectName(name)
        ##self.le_editori_z.setText(str(z))
        #self.le_editori_z_third.setText(str(""))
        #self.le_editori_z_third.setReadOnly(True)
        #grid_layout.addWidget(self.le_labelori_z_third, row_start + 9,column_start + 0)
        #grid_layout.addWidget(self.le_editori_z_third, row_start + 9,column_start + 1)

        #self.le_labelori_w_third = QtGui.QLabel("Orientation W:")
        #self.le_editori_w_third = QtGui.QLineEdit()
        #self.le_editori_w_third.setObjectName(name)
        ##self.le_editori_w.setText(str(w))
        #self.le_editori_w_third.setText(str(""))
        #self.le_editori_w_third.setReadOnly(True)
        #grid_layout.addWidget(self.le_labelori_w_third, row_start + 10, column_start + 0)
        #grid_layout.addWidget(self.le_editori_w_third, row_start + 10,column_start + 1)

##############################################################################################
#Clear buttons:
##############################################################################################
        self.le_clear_button_first = QtGui.QPushButton("Clear First Pose")
        grid_layout.addWidget(self.le_clear_button_first, 11, 1)
        self.le_clear_button_first.clicked.connect(lambda: self.clearRQTValues(1))

        self.le_clear_button_second = QtGui.QPushButton("Clear Second Pose")
        grid_layout.addWidget(self.le_clear_button_second, 11, 3)
        self.le_clear_button_second.clicked.connect(lambda: self.clearRQTValues(2))

        self.le_clear_button_third = QtGui.QPushButton("Clear Third Pose")
        grid_layout.addWidget(self.le_clear_button_third, 11, 5)
        self.le_clear_button_third.clicked.connect(lambda: self.clearRQTValues(3))
        #self.le_clear_button_third.connect(self.le_clear_button_third, QtCore.SIGNAL('clicked()'), self.updateRQTValues)
##############################################################################################

        return self.le

    def updateRQTValues(self, current_pose_iter, send_by_ps_move):
        # get current handle pose in "base_link": ############################################	
    	current_pose = PoseStamped()
        current_pose = self.lr.transformPose("base_link", self.current_handle_pose)

        if(send_by_ps_move):
            if(self.current_iterate <= 1):
               	self.le_edit_frame_id_first.setText(str( current_pose.header.frame_id))
                self.le_editx_first.setText(str( current_pose.pose.position.x))
                self.le_edity_first.setText(str( current_pose.pose.position.y))
                self.le_editz_first.setText(str( current_pose.pose.position.z))
                ########################################################################
                self.current_iterate = 2
            
                self.first_pose.header.frame_id = current_pose.header.frame_id
                self.first_pose.pose.position.x = current_pose.pose.position.x
                self.first_pose.pose.position.y = current_pose.pose.position.y
                self.first_pose.pose.position.z = current_pose.pose.position.z
                self.first_pose.pose.orientation.x = current_pose.pose.orientation.x
                self.first_pose.pose.orientation.y = current_pose.pose.orientation.y
                self.first_pose.pose.orientation.z = current_pose.pose.orientation.z
                self.first_pose.pose.orientation.w = current_pose.pose.orientation.w

            elif(self.current_iterate == 2):
                self.le_edit_frame_id_second.setText(str( current_pose.header.frame_id))
                self.le_editx_second.setText(str( current_pose.pose.position.x))
                self.le_edity_second.setText(str( current_pose.pose.position.y))
                self.le_editz_second.setText(str( current_pose.pose.position.z))
                ########################################################################
                self.current_iterate = 3

                self.second_pose.header.frame_id = current_pose.header.frame_id
                self.second_pose.pose.position.x = current_pose.pose.position.x
                self.second_pose.pose.position.y = current_pose.pose.position.y
                self.second_pose.pose.position.z = current_pose.pose.position.z
                self.second_pose.pose.orientation.x = current_pose.pose.orientation.x
                self.second_pose.pose.orientation.y = current_pose.pose.orientation.y
                self.second_pose.pose.orientation.z = current_pose.pose.orientation.z
                self.second_pose.pose.orientation.w = current_pose.pose.orientation.w
            else:
                self.le_edit_frame_id_third.setText(str( current_pose.header.frame_id))
                self.le_editx_third.setText(str( current_pose.pose.position.x))
                self.le_edity_third.setText(str( current_pose.pose.position.y))
                self.le_editz_third.setText(str( current_pose.pose.position.z))

                self.current_iterate = 1
                ########################################################################
                self.third_pose.header.frame_id = current_pose.header.frame_id
                self.third_pose.pose.position.x = current_pose.pose.position.x
                self.third_pose.pose.position.y = current_pose.pose.position.y
                self.third_pose.pose.position.z = current_pose.pose.position.z
                self.third_pose.pose.orientation.x = current_pose.pose.orientation.x
                self.third_pose.pose.orientation.y = current_pose.pose.orientation.y
                self.third_pose.pose.orientation.z = current_pose.pose.orientation.z
                self.third_pose.pose.orientation.w = current_pose.pose.orientation.w
        else:
            if(current_pose_iter == 1):
                self.le_edit_frame_id_first.setText(str( current_pose.header.frame_id))
                self.le_editx_first.setText(str( current_pose.pose.position.x))
                self.le_edity_first.setText(str( current_pose.pose.position.y))
                self.le_editz_first.setText(str( current_pose.pose.position.z))
                ########################################################################
                self.first_pose.header.frame_id = current_pose.header.frame_id
                self.first_pose.pose.position.x = current_pose.pose.position.x
                self.first_pose.pose.position.y = current_pose.pose.position.y
                self.first_pose.pose.position.z = current_pose.pose.position.z
                self.first_pose.pose.orientation.x = current_pose.pose.orientation.x
                self.first_pose.pose.orientation.y = current_pose.pose.orientation.y
                self.first_pose.pose.orientation.z = current_pose.pose.orientation.z
                self.first_pose.pose.orientation.w = current_pose.pose.orientation.w

            elif(current_pose_iter == 2):
                self.le_edit_frame_id_second.setText(str( current_pose.header.frame_id))
                self.le_editx_second.setText(str( current_pose.pose.position.x))
                self.le_edity_second.setText(str( current_pose.pose.position.y))
                self.le_editz_second.setText(str( current_pose.pose.position.z))
                ########################################################################
                self.second_pose.header.frame_id = current_pose.header.frame_id
                self.second_pose.pose.position.x = current_pose.pose.position.x
                self.second_pose.pose.position.y = current_pose.pose.position.y
                self.second_pose.pose.position.z = current_pose.pose.position.z
                self.second_pose.pose.orientation.x = current_pose.pose.orientation.x
                self.second_pose.pose.orientation.y = current_pose.pose.orientation.y
                self.second_pose.pose.orientation.z = current_pose.pose.orientation.z
                self.second_pose.pose.orientation.w = current_pose.pose.orientation.w

            elif(current_pose_iter == 3):
                self.le_edit_frame_id_third.setText(str( current_pose.header.frame_id))
                self.le_editx_third.setText(str( current_pose.pose.position.x))
                self.le_edity_third.setText(str( current_pose.pose.position.y))
                self.le_editz_third.setText(str( current_pose.pose.position.z))
                ########################################################################
                self.third_pose.header.frame_id = current_pose.header.frame_id
                self.third_pose.pose.position.x = current_pose.pose.position.x
                self.third_pose.pose.position.y = current_pose.pose.position.y
                self.third_pose.pose.position.z = current_pose.pose.position.z
                self.third_pose.pose.orientation.x = current_pose.pose.orientation.x
                self.third_pose.pose.orientation.y = current_pose.pose.orientation.y
                self.third_pose.pose.orientation.z = current_pose.pose.orientation.z
                self.third_pose.pose.orientation.w = current_pose.pose.orientation.w

    def clearRQTValues(self, current_iterate):
        if(current_iterate == 1):
            self.le_edit_frame_id_first.setText(str(""))
            self.le_editx_first.setText(str(""))
            self.le_edity_first.setText(str(""))
            self.le_editz_first.setText(str(""))

        elif(current_iterate == 2):
            self.le_edit_frame_id_second.setText(str(""))
            self.le_editx_second.setText(str(""))
            self.le_edity_second.setText(str(""))
            self.le_editz_second.setText(str(""))

        else:
            self.le_edit_frame_id_third.setText(str(""))
            self.le_editx_third.setText(str(""))
            self.le_edity_third.setText(str(""))
            self.le_editz_third.setText(str(""))


    def getPaletteFrameFromThreePoses(self, poseStamped_first, poseStamped_mid, poseStamped_last):

        def normalize(v):
            norm=np.linalg.norm(v)
            if norm==0: 
               return v
            return v/norm

        if (not (poseStamped_first.header.frame_id == poseStamped_mid.header.frame_id and
                poseStamped_mid.header.frame_id == poseStamped_last.header.frame_id and
                poseStamped_last.header.frame_id == poseStamped_first.header.frame_id)):
            return "Invalid input data"
        posePallet = copy.deepcopy(poseStamped_first)

        pose_first = np.array([poseStamped_first.pose.position.x, poseStamped_first.pose.position.y, poseStamped_first.pose.position.z])
        pose_mid = np.array([poseStamped_mid.pose.position.x, poseStamped_mid.pose.position.y, poseStamped_mid.pose.position.z])
        pose_last = np.array([poseStamped_last.pose.position.x, poseStamped_last.pose.position.y, poseStamped_last.pose.position.z])

        x_axis = normalize(pose_mid - pose_first)
        rospy.logdebug("x_axis: %s", x_axis)

        intersection_point = pose_first + np.dot((pose_last-pose_first), x_axis)*x_axis
        
        width = np.linalg.norm(pose_first - intersection_point)
        depth = np.linalg.norm(pose_last - intersection_point)

        y_axis = normalize(pose_last - intersection_point)
        rospy.logdebug("y_axis: %s", y_axis)

        z_axis = np.cross(x_axis, y_axis)
        z_axis = normalize(z_axis)
        rospy.logdebug("z_axis: %s", z_axis)

        rot_mat = np.identity(4)
        rot_mat[0][0:3]=x_axis[:]
        rot_mat[1][0:3]=y_axis[:]
        rot_mat[2][0:3]=z_axis[:]
        rot_mat = rot_mat.transpose()

        rospy.logdebug("Rotation Matrix: \n %s", rot_mat)
        ori = tf.transformations.quaternion_from_matrix(rot_mat)
    
        posePallet.header.frame_id = poseStamped_first.header.frame_id
        posePallet.pose.orientation.x = ori[0]
        posePallet.pose.orientation.y = ori[1]
        posePallet.pose.orientation.z = ori[2]
        posePallet.pose.orientation.w = ori[3]

        #return (posePallet, width, depth)
        return posePallet



class CamPoseTeacher(TeacherPlugin):
        
    def __init__(self):
        # start listener for pose
        global tflistener
        if tflistener is None:
            tflistener = tf.TransformListener()
        self.lr = tflistener
        self.current_pose = PoseStamped()
        self.detect_client = actionlib.SimpleActionClient("needle_detect", actionlib.msg.TestAction)
        self.ext_ctrl_client = actionlib.SimpleActionClient("/arm_controller/QueueExtCtrl", frida_driver.msg.ExtCtrlAction)
        self.queue_lin_client = actionlib.SimpleActionClient("/arm_controller/QueueLin", prace_moveit_interface.msg.LinAction)
        self.exec_queue = actionlib.SimpleActionClient("/arm_controller/ExecQueue", prace_moveit_interface.msg.ExecPlanAction)
        pass

    def callback_Left(self):
        frame_id = str(self.le_edit_frame_id.text())
        ext_goal = ExtCtrlGoal()
        ext_goal.task.task_num=450
        ext_goal.execute = 1.0
        self.ext_ctrl_client.send_goal(ext_goal)
        print "Wait for ExtCtrl"
        self.ext_ctrl_client.wait_for_result(timeout=rospy.Duration(60))
        print "Done"
        trans = None
        rot = None
        rospy.sleep(0.5)
        now = rospy.Time.now()
        try:
            self.lr.waitForTransform("base_link", "raspberry_left_tip_link", now, rospy.Duration(4.0))
            (trans, rot) = self.lr.lookupTransform("base_link", "raspberry_left_tip_link", now)     
        except tf.Exception as e:
            print "Execption: ", e
            return
        movelin_goal = LinGoal()
        movelin_goal.move_group="left_arm_raspberry"
        movelin_goal.target_frame="raspberry_left_tip_link"
        movelin_goal.goal_pose.header.frame_id="base_link"
        movelin_goal.goal_pose.header.stamp = now
        movelin_goal.goal_pose.pose.position.x = trans[0]
        movelin_goal.goal_pose.pose.position.y = trans[1]
        movelin_goal.goal_pose.pose.position.z = 1.085
        movelin_goal.goal_pose.pose.orientation.w = 0.0
        movelin_goal.goal_pose.pose.orientation.x = 0.0
        movelin_goal.goal_pose.pose.orientation.y = 1.0
        movelin_goal.goal_pose.pose.orientation.z = 0.0
        movelin_goal.linVel=1.0

        self.queue_lin_client.send_goal(movelin_goal)
        self.queue_lin_client.wait_for_result()
        exec_goal = ExecPlanGoal()
        self.exec_queue.send_goal(exec_goal)
        self.exec_queue.wait_for_result(timeout=rospy.Duration(60))
        rospy.sleep(0.35)

        detect_goal = TestGoal()
        detect_goal.goal = 1
        self.detect_client.send_goal(detect_goal)
        self.detect_client.wait_for_result(timeout=rospy.Duration(10))

        rospy.sleep(0.75)
        now = rospy.Time.now()
        try:
            self.lr.waitForTransform(frame_id, "needle_detect_pickup_left_frame", now, rospy.Duration(2.0))
            (trans, rot) = self.lr.lookupTransform(frame_id, "needle_detect_pickup_left_frame", now)
        except tf.Exception as e:
            print "Execption: ", e
            return
        self.current_pose.header.frame_id = frame_id
        self.current_pose.pose.position.x = trans[0]
        self.current_pose.pose.position.y = trans[1]
        self.current_pose.pose.position.z = trans[2]

        self.current_pose.pose.orientation.x = rot[0]
        self.current_pose.pose.orientation.y = rot[1]
        self.current_pose.pose.orientation.z = rot[2]
        self.current_pose.pose.orientation.w = rot[3]

        now = rospy.Time.now()
        movelin_goal2 = LinGoal()
        movelin_goal2.move_group="left_arm_gripper"
        movelin_goal2.target_frame="gripper_left_tip_link"
        movelin_goal2.goal_pose = copy.deepcopy(self.current_pose)
        movelin_goal2.goal_pose.header.stamp = now
        movelin_goal2.goal_pose.pose.position.z += 0.02
        movelin_goal2.goal_pose.pose.orientation.w = 0.0
        movelin_goal2.goal_pose.pose.orientation.x = 0.0
        movelin_goal2.goal_pose.pose.orientation.y = 1.0
        movelin_goal2.goal_pose.pose.orientation.z = 0.0
        movelin_goal2.linVel=1.0

        self.queue_lin_client.send_goal(movelin_goal2)
        self.queue_lin_client.wait_for_result()

        now = rospy.Time.now()
        movelin_goal3 = LinGoal()
        movelin_goal3.move_group="left_arm_gripper"
        movelin_goal3.target_frame="gripper_left_tip_link"
        movelin_goal3.goal_pose = copy.deepcopy(self.current_pose)
        movelin_goal3.goal_pose.header.stamp = now
        movelin_goal3.goal_pose.pose.orientation.w = 0.0
        movelin_goal3.goal_pose.pose.orientation.x = 0.0
        movelin_goal3.goal_pose.pose.orientation.y = 1.0
        movelin_goal3.goal_pose.pose.orientation.z = 0.0
        movelin_goal3.linVel=1.0

        self.queue_lin_client.send_goal(movelin_goal3)
        self.queue_lin_client.wait_for_result()

        now = rospy.Time.now()
        movelin_goal4 = LinGoal()
        movelin_goal4.move_group="left_arm_gripper"
        movelin_goal4.target_frame="gripper_left_tip_link"
        movelin_goal4.goal_pose = copy.deepcopy(self.current_pose)
        movelin_goal4.goal_pose.header.stamp = now
        movelin_goal4.goal_pose.pose.position.z += 0.06
        movelin_goal4.goal_pose.pose.orientation.w = 0.0
        movelin_goal4.goal_pose.pose.orientation.x = 0.0
        movelin_goal4.goal_pose.pose.orientation.y = 1.0
        movelin_goal4.goal_pose.pose.orientation.z = 0.0
        movelin_goal4.linVel=1.0

        self.queue_lin_client.send_goal(movelin_goal4)
        self.queue_lin_client.wait_for_result()


        exec_goal = ExecPlanGoal()
        self.exec_queue.send_goal(exec_goal)
        self.exec_queue.wait_for_result(timeout=rospy.Duration(60))

        self.updateRQTValues()

    def callback_Right(self):
        frame_id = str(self.le_edit_frame_id.text())
        ext_goal = ExtCtrlGoal()
        ext_goal.task.task_num=150
        ext_goal.execute = 1.0
        self.ext_ctrl_client.send_goal(ext_goal)
        print "Wait for ExtCtrl"
        self.ext_ctrl_client.wait_for_result(timeout=rospy.Duration(60))
        print "Done"
        trans = None
        rot = None
        rospy.sleep(0.5)
        now = rospy.Time.now()
        try:
            self.lr.waitForTransform("base_link", "raspberry_right_tip_link", now, rospy.Duration(4.0))
            (trans, rot) = self.lr.lookupTransform("base_link", "raspberry_right_tip_link", now)     
        except tf.Exception as e:
            print "Execption: ", e
            return
        movelin_goal = LinGoal()
        movelin_goal.move_group="right_arm_raspberry"
        movelin_goal.target_frame="raspberry_right_tip_link"
        movelin_goal.goal_pose.header.frame_id="base_link"
        movelin_goal.goal_pose.header.stamp = now
        movelin_goal.goal_pose.pose.position.x = trans[0]
        movelin_goal.goal_pose.pose.position.y = trans[1]
        movelin_goal.goal_pose.pose.position.z = 1.085
        movelin_goal.goal_pose.pose.orientation.w = 0.0
        movelin_goal.goal_pose.pose.orientation.x = 0.0
        movelin_goal.goal_pose.pose.orientation.y = 1.0
        movelin_goal.goal_pose.pose.orientation.z = 0.0
        movelin_goal.linVel=1.0

        self.queue_lin_client.send_goal(movelin_goal)
        self.queue_lin_client.wait_for_result()
        exec_goal = ExecPlanGoal()
        self.exec_queue.send_goal(exec_goal)
        self.exec_queue.wait_for_result(timeout=rospy.Duration(60))
        rospy.sleep(0.35)

        detect_goal = TestGoal()
        detect_goal.goal = 0
        self.detect_client.send_goal(detect_goal)
        self.detect_client.wait_for_result(timeout=rospy.Duration(10))

        rospy.sleep(0.75)
        now = rospy.Time.now()
        try:
            self.lr.waitForTransform(frame_id, "needle_detect_pickup_right_frame", now, rospy.Duration(2.0))
            (trans, rot) = self.lr.lookupTransform(frame_id, "needle_detect_pickup_right_frame", now)
        except tf.Exception as e:
            print "Execption: ", e
            return
        self.current_pose.header.frame_id = frame_id
        self.current_pose.pose.position.x = trans[0]
        self.current_pose.pose.position.y = trans[1]
        self.current_pose.pose.position.z = trans[2] - 0.0015

        self.current_pose.pose.orientation.x = rot[0]
        self.current_pose.pose.orientation.y = rot[1]
        self.current_pose.pose.orientation.z = rot[2]
        self.current_pose.pose.orientation.w = rot[3]

        now = rospy.Time.now()
        movelin_goal2 = LinGoal()
        movelin_goal2.move_group="right_arm_gripper"
        movelin_goal2.target_frame="gripper_right_tip_link"
        movelin_goal2.goal_pose = copy.deepcopy(self.current_pose)
        movelin_goal2.goal_pose.header.stamp = now
        movelin_goal2.goal_pose.pose.position.z += 0.02
        movelin_goal2.goal_pose.pose.orientation.w = 0.0
        movelin_goal2.goal_pose.pose.orientation.x = 0.0
        movelin_goal2.goal_pose.pose.orientation.y = 1.0
        movelin_goal2.goal_pose.pose.orientation.z = 0.0
        movelin_goal2.linVel=1.0

        self.queue_lin_client.send_goal(movelin_goal2)
        self.queue_lin_client.wait_for_result()

        now = rospy.Time.now()
        movelin_goal3 = LinGoal()
        movelin_goal3.move_group="right_arm_gripper"
        movelin_goal3.target_frame="gripper_right_tip_link"
        movelin_goal3.goal_pose = copy.deepcopy(self.current_pose)
        movelin_goal3.goal_pose.header.stamp = now
        movelin_goal3.goal_pose.pose.orientation.w = 0.0
        movelin_goal3.goal_pose.pose.orientation.x = 0.0
        movelin_goal3.goal_pose.pose.orientation.y = 1.0
        movelin_goal3.goal_pose.pose.orientation.z = 0.0
        movelin_goal3.linVel=1.0

        self.queue_lin_client.send_goal(movelin_goal3)
        self.queue_lin_client.wait_for_result()

        now = rospy.Time.now()
        movelin_goal4 = LinGoal()
        movelin_goal4.move_group="right_arm_gripper"
        movelin_goal4.target_frame="gripper_right_tip_link"
        movelin_goal4.goal_pose = copy.deepcopy(self.current_pose)
        movelin_goal4.goal_pose.header.stamp = now
        movelin_goal4.goal_pose.pose.position.z += 0.06
        movelin_goal4.goal_pose.pose.orientation.w = 0.0
        movelin_goal4.goal_pose.pose.orientation.x = 0.0
        movelin_goal4.goal_pose.pose.orientation.y = 1.0
        movelin_goal4.goal_pose.pose.orientation.z = 0.0
        movelin_goal4.linVel=1.0

        self.queue_lin_client.send_goal(movelin_goal4)
        self.queue_lin_client.wait_for_result()


        exec_goal = ExecPlanGoal()
        self.exec_queue.send_goal(exec_goal)
        self.exec_queue.wait_for_result(timeout=rospy.Duration(60))

        self.updateRQTValues()

    def getName(self):
        return "CamPoseTeacher"

    def getType(self):
        return "geometry_msgs/PoseStamped"

    def getData(self, name):
        #any_number = input('Please enter any # to stamp current pose: ')
        raw_input('Press any key to stamp current pose:')
        print self.current_pose 
        return self.current_pose

    def getRQTData(self, name):
        p = PoseStamped()
        p.header.frame_id = str(self.le_edit_frame_id.text())

        p.pose.orientation.x = float(self.le_editori_x.text())
        p.pose.orientation.y = float(self.le_editori_y.text())
        p.pose.orientation.z = float(self.le_editori_z.text())
        p.pose.orientation.w = float(self.le_editori_w.text())

        p.pose.position.x = float(self.le_editx.text())
        p.pose.position.y = float(self.le_edity.text())
        p.pose.position.z = float(self.le_editz.text())

        return p;
        
    def getRQTWidget(self, name, current_data):    
        
        self.le = QtGui.QWidget()
        grid_layout = QtGui.QGridLayout()
        self.le.setLayout(grid_layout)

        #if(rospy.get_param('scene_already_calibrated') == False):
        #    print "We need to calibrate this scene first"
        #    # build calibration button
        #    self.calibration_info = QtGui.QLabel("Calibrate scene first: ")
        #    grid_layout.addWidget(self.calibration_info, 0,0)

        #    self.le_calibration_button = QtGui.QPushButton("Calibrate Scene Now")
        #    grid_layout.addWidget(self.le_calibration_button, 0,3)
        #    self.le_calibration_button.connect(self.le_calibration_button, QtCore.SIGNAL('clicked()'), self.calibrateScene)
    
        self.le_label_frame_id = QtGui.QLabel("frame_id:")
        self.le_edit_frame_id = QtGui.QLineEdit()
        self.le_edit_frame_id.setObjectName(name)
        self.le_edit_frame_id.setReadOnly(False)
        #self.le_edit_frame_id.setText(str(current_data['header']['frame_id']))
        self.le_edit_frame_id.setText(str(""))
        grid_layout.addWidget(self.le_label_frame_id, 2,0)
        grid_layout.addWidget(self.le_edit_frame_id, 2,1)

        self.le_labelx = QtGui.QLabel("Position X:")
        self.le_editx = QtGui.QLineEdit()
        self.le_editx.setObjectName(name)
        self.le_editx.setReadOnly(True)
        #self.le_editx.setText(str(current_data['pose']['position']['x']))
        self.le_editx.setText(str(""))
        grid_layout.addWidget(self.le_labelx, 3,0)
        grid_layout.addWidget(self.le_editx, 3,1)
        
        self.le_labely = QtGui.QLabel("Position Y:")
        self.le_edity = QtGui.QLineEdit()
        self.le_edity.setObjectName(name)
        self.le_edity.setReadOnly(True)
        #self.le_edity.setText(str(current_data['pose']['position']['y']))
        self.le_edity.setText(str(""))
        grid_layout.addWidget(self.le_labely, 4,0)
        grid_layout.addWidget(self.le_edity, 4,1)

        self.le_labelz = QtGui.QLabel("Position Z:")
        self.le_editz = QtGui.QLineEdit()
        self.le_editz.setObjectName(name)
        self.le_editz.setReadOnly(True)
        #self.le_editz.setText(str(current_data['pose']['position']['z']))
        self.le_editz.setText(str(""))
        grid_layout.addWidget(self.le_labelz, 5,0)
        grid_layout.addWidget(self.le_editz, 5,1)


        [x,y,z,w] = current_data['pose']['orientation'].values()

        self.le_labelori_x = QtGui.QLabel("Orientation X:")
        self.le_editori_x = QtGui.QLineEdit()
        self.le_editori_x.setObjectName(name)
        self.le_editori_x.setReadOnly(True)
        #self.le_editori_x.setText(str(x))
        self.le_editori_x.setText(str(""))
        grid_layout.addWidget(self.le_labelori_x, 2,2)
        grid_layout.addWidget(self.le_editori_x, 2,3)

        self.le_labelori_y = QtGui.QLabel("Orientation Y:")
        self.le_editori_y = QtGui.QLineEdit()
        self.le_editori_y.setObjectName(name)
        #self.le_editori_y.setText(str(y))
        self.le_editori_y.setText(str(""))
        self.le_editori_y.setReadOnly(True)
        grid_layout.addWidget(self.le_labelori_y, 3,2)
        grid_layout.addWidget(self.le_editori_y, 3,3)

        self.le_labelori_z = QtGui.QLabel("Orientation Z:")
        self.le_editori_z = QtGui.QLineEdit()
        self.le_editori_z.setObjectName(name)
        #self.le_editori_z.setText(str(z))
        self.le_editori_z.setText(str(""))
        self.le_editori_z.setReadOnly(True)
        grid_layout.addWidget(self.le_labelori_z, 4,2)
        grid_layout.addWidget(self.le_editori_z, 4,3)

        self.le_labelori_w = QtGui.QLabel("Orientation W:")
        self.le_editori_w = QtGui.QLineEdit()
        self.le_editori_w.setObjectName(name)
        #self.le_editori_w.setText(str(w))
        self.le_editori_w.setText(str(""))
        self.le_editori_w.setReadOnly(True)
        grid_layout.addWidget(self.le_labelori_w, 5,2)
        grid_layout.addWidget(self.le_editori_w, 5,3)

        self.le_teach_button = QtGui.QPushButton("Teach Left")
        grid_layout.addWidget(self.le_teach_button, 6,3)
        self.le_teach_button.connect(self.le_teach_button, QtCore.SIGNAL('clicked()'), self.callback_Left)

        self.le_teach_button = QtGui.QPushButton("Teach Right")
        grid_layout.addWidget(self.le_teach_button, 7,3)
        self.le_teach_button.connect(self.le_teach_button, QtCore.SIGNAL('clicked()'), self.callback_Right)

        return self.le

    def updateRQTValues(self):

        self.le_edit_frame_id.setText(str(self.current_pose.header.frame_id))
        self.le_editx.setText(str( self.current_pose.pose.position.x))
        self.le_edity.setText(str( self.current_pose.pose.position.y))
        self.le_editz.setText(str( self.current_pose.pose.position.z))

        self.le_editori_x.setText(str(self.current_pose.pose.orientation.x))
        self.le_editori_y.setText(str(self.current_pose.pose.orientation.y))
        self.le_editori_z.setText(str(self.current_pose.pose.orientation.z))
        self.le_editori_w.setText(str(self.current_pose.pose.orientation.w))