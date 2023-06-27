#!/usr/bin/env python3

import rospy
from std_msgs.msg import Bool

if __name__ =="__main__":
    rospy.init_node("fake node")
    pub = rospy.Publisher('arm_settled', Bool, queue_size=10)
    rate = rospy.Rate(1)

    while not rospy.is_shutdown():
        rospy.loginfo("settled")
        my_bool_value = False
        pub.publish(my_bool_value)
        rate.sleep()
        #false at patient, true at object.