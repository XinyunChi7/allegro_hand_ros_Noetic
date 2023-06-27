#!/usr/bin/env python3

import sys
import argparse
import numpy as np
import rospy
from liballegro import AllegroClient
from std_msgs.msg import String
from std_msgs.msg import Float32
from std_msgs.msg import Bool
#from ur10e main import specific object value

""" position[[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]]=0.5
This file contains several examples of the AllegroClient python library that
allows you to interact with the Allegro hand directly using python.

Set the allegro hand topic directly using:
   --hand_prefix=allegroHand_0
(or some other topic name.)

"""

def hard_grasp(allegro_client,
               finger_indices=None
               ):
    if not finger_indices:
        finger_indices = [0, 1, 2, 3]

    position = np.ones(16)
    allegro_client.command_joint_position(position)



def finger_rel(allegro_client, finger_indices=None):
    
    val = 1.0
    rate = rospy.Rate(4)
    # if not finger_indices:
    #     finger_indices = [0, 1, 2, 3]

    # if position == np.ones(16) *0.5: return


    # position = np.ones(16) *0.6
    # allegro_client.command_joint_position(position)

    while val > 0.5:
        position = np.ones(16) *val
        allegro_client.command_joint_position(position)
        val -= 0.1
        rate.sleep()
    
    allegro_client.is_released = True





    # Additional code to run after loop exits, if needed





# def finger_rel(allegro_client,
#                finger_indices=None,
#                ):
#     if not finger_indices:
#         finger_indices = [0, 1, 2, 3]

#     position = np.ones(16)
#     rate = rospy.Rate(4)
#     val = 0.9
#     reached_half = False
#     done = False

#     while not done:
#         rate.sleep()

#         if not reached_half:

#             for finger_idx in finger_indices:
#                     inds = range(4*finger_idx + 1, 4*finger_idx + 4)
#                     position[inds] = val
#              # Command the joint position.
#             allegro_client.command_joint_position(position)
#             val = val-0.1

#             if val == 0.5:
#                 reached_half = True
        
#         else:

#             val = 0.5    
#             for finger_idx in finger_indices:
#                 inds = range(4*finger_idx + 1, 4*finger_idx + 4)
#                 position[inds] = val
#             # Command the joint position.
#             allegro_client.command_joint_position(position)



def fingers_motion(allegro_client,
                 finger_indices=None,
                 ):
    """
    Wave one or more fingers in a sinusoidal pattern.
    :param allegro_client: The client.
    :param finger_indices: List of finger indices (between 0 and 3)
    :param num_seconds: Total time to spend doing this.
    """
    hz = 4
    r = rospy.Rate(hz)

    # Choose which fingers to wave, by default do all of them.
    if not finger_indices:
        finger_indices = [0, 1, 2, 3]

    # Later we will only change the desired position for the 'active' fingers,
    # so this sets the default pose for *all* fingers. This is set to the value
    # 1.0, except for the first joint of each finger (the finger rotation along
    # its pointing axis) which is 0.0.
    position = np.ones(16)
    position[[0, 4, 8, 12]] = 0.0

    while not rospy.is_shutdown():
        # Generate a sinusoidal signal between 0 and 1.5
        val = (np.sin(0.2 * rospy.Time.now().to_sec()) + 1) * 0.75

        # Set all joints for the fingers we are controlling.
        for finger_idx in finger_indices:
            inds = range(4*finger_idx + 1, 4*finger_idx + 4)
            position[inds] = val
        # Command the joint position.
        allegro_client.command_joint_position(position)

        r.sleep()
    return

class AmigiRuner(object):
    def __init__(self, args) -> None:
        (parsed_args, other_args) = parser.parse_known_args(args)
        self.client = AllegroClient(hand_topic_prefix=parsed_args.hand_prefix)
        self.pub = rospy.Publisher('received_topic', Bool, queue_size=10)
        self.sub = rospy.Subscriber('arm_settled', Bool, self.callback)    
        #listen to the arm, initially arm_settled is set to false, when the arm
        #arrived at the object, arm settled=true
        #and keep sending true until arrived at the patient.
        self.parsed_args = parsed_args
        self.other_args = other_args
        self.client.is_released = False

    def run(self):
        rospy.init_node('example_allegro_lib', self.other_args)
        rospy.sleep(0.5)  # Wait for connections.
        rospy.spin()

    def callback(self, msg):
        # import pdb
        # pdb.set_trace()
        if msg.data:
            hard_grasp(self.client, finger_indices=[0, 1, 2, 3])
            rospy.loginfo("Arm has arrived the object position. Now grasping...")
            self.client.is_released = False
            is_released = False


            #fingers_motion(self.client, finger_indices=[0, 1, 2, 3])
            #self.client.command_hand_configuration('three finger grasp')
            self.get_publish(True)
        else:
            if not self.client.is_released:
                finger_rel(self.client, finger_indices=[0, 1, 2, 3])
                rospy.loginfo("Arm has arrived the patient position. Now releasing...")
            #self.client.command_hand_configuration('home')
            self.get_publish(False)
            
    def get_publish(self, bool_msg):
        
        #rospy.init_node('received_publisher')
        rate = rospy.Rate(1)
        if bool_msg:
            self.pub.publish(True)
            rospy.loginfo("obtained")
            # while not rospy.is_shutdown():
            #     my_bool_value = True
            #     self.pub.publish(my_bool_value)
            #     rate.sleep()
        else:
            self.pub.publish(False)
            rospy.loginfo("Not obtained")
            # while not rospy.is_shutdown():
            #     my_bool_value = False
            #     self.pub.publish(my_bool_value)
            #     rate.sleep()


if __name__ == '__main__':
    args = sys.argv[1:]
    parser = argparse.ArgumentParser(description='Allegro python library')
    parser.add_argument('--hand_prefix', type=str,
                        help='ROS topic prefix for the hand.',
                        default='allegroHand_0')

    runner = AmigiRuner(args)
    runner.run()