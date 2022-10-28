#!/usr/bin/env python

import roslib
import rospy
import smach
import smach_ros
import time
import random

global battery
battery = 0
# INSTALLATION
#
# - move this file to the 'smach_tutorial/scr' folder and give running permissions to it with
#          $ chmod +x state_machine.py
# - run the 'roscore' and then you can run the state machine with
#          $ rosrun smach_tutorial state_machine.py
# - eventually install the visualiser using
#          $ sudo apt-get install ros-kinetic-smach-viewer
# - run the visualiser with
#          $ rosrun smach_viewer smach_viewer.py

def user_action():
    return random.choice(['received','battery_low', 'charged', 'urgent', 'visited'])

# define state Wait Ontology
class WaitOntology(smach.State):
    def __init__(self):
        # initialisation function, it should not wait
        smach.State.__init__(self,
                             outcomes=['received','battery_low', 'charged', 'urgent', 'visited'],
                             input_keys=['waitOntology_counter_in'], #forse queste vanno cambiate vedi arch scheleton
                             output_keys=['waitOntology_counter_out'])

    def execute(self, userdata):
        # function called when exiting from the node, it can be blacking
        time.sleep(5)

        rospy.loginfo('Executing state WaitOntology (users = %f)'%userdata.waitOntology_counter_in)
        userdata.waitOntology_counter_out = userdata.waitOntology_counter_in + 1
        return user_action()

class Recharging(smach.State):
    def __init__(self):
        # initialisation function, it should not wait
        smach.State.__init__(self,
                             outcomes=['received','battery_low', 'charged', 'urgent', 'visited'],
                             input_keys=['recharging_counter_in'],
                             output_keys=['recharging_counter_out'])

    def execute(self, userdata):
        # function called when exiting from the node, it can be blacking
        battery = 0
        while (battery < 10):
        	time.sleep(1)
        	battery += 1
        	print("Battery at: ", battery*10 , " %", end='\r')

        rospy.loginfo('Executing state RECHARGING (users = %f)'%userdata.recharging_counter_in)
        userdata.recharging_counter_out = userdata.recharging_counter_in + 1
        return 'charged'



# define state Locked
class Corridor(smach.State):
    def __init__(self):
        smach.State.__init__(self,
                             outcomes=['received','battery_low', 'charged', 'urgent', 'visited'],
                             input_keys=['corridor_counter_in'],
                             output_keys=['corridor_counter_out'])
        self.sensor_input = 0
        self.rate = rospy.Rate(200)  # Loop at 200 Hz

    def execute(self, userdata):
        # simulate that we have to get 5 data samples to compute the outcome
        while not rospy.is_shutdown():
            time.sleep(1)
            if self.sensor_input < 5:
                rospy.loginfo('Executing state CORRIDOR (users = %f)'%userdata.corridor_counter_in)
                userdata.corridor_counter_out = userdata.corridor_counter_in + 1
                return user_action()
            self.sensor_input += 1
            self.rate.sleep

class Room(smach.State):
    def __init__(self):
        # initialisation function, it should not wait
        smach.State.__init__(self,
                             outcomes=['received','battery_low', 'charged', 'urgent', 'visited'],
                             input_keys=['room_counter_in'],
                             output_keys=['room_counter_out'])

    def execute(self, userdata):
        # function called when exiting from the node, it can be blacking
        time.sleep(5)

        rospy.loginfo('Executing state ROOM (users = %f)'%userdata.room_counter_in)
        userdata.room_counter_out = userdata.room_counter_in + 1
        return user_action()

def main():
    rospy.init_node('exercise_robot_state_machine')

    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=['container_interface'])
    sm.userdata.sm_counter = 0

    # Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add('WAIT ONTOLOGY', WaitOntology(),
                               transitions={'received':'RECHARGING',
                                            'battery_low':'WAIT ONTOLOGY',
                                            'charged':'WAIT ONTOLOGY',
                                            'urgent':'WAIT ONTOLOGY',
                                            'visited':'WAIT ONTOLOGY'},
                               remapping={'waitOntology_counter_in':'sm_counter',
                                          'waitOntology_counter_out':'sm_counter'})
        smach.StateMachine.add('RECHARGING', Recharging(),
                               transitions={'received':'RECHARGING',
                                            'battery_low':'RECHARGING',
                                            'charged':'CORRIDOR',
                                            'urgent':'RECHARGING',
                                            'visited':'RECHARGING'},
                               remapping={'recharging_counter_in':'sm_counter',
                                          'recharging_counter_out':'sm_counter'})
        smach.StateMachine.add('CORRIDOR', Corridor(),
                               transitions={'received':'CORRIDOR',
                                            'battery_low':'RECHARGING',
                                            'charged':'CORRIDOR',
                                            'urgent':'ROOM',
                                            'visited':'CORRIDOR'},
                               remapping={'corridor_counter_in':'sm_counter',
                                          'corridor_counter_out':'sm_counter'})

        smach.StateMachine.add('ROOM', Room(),
                               transitions={'received':'ROOM',
                                            'battery_low':'RECHARGING',
                                            'charged':'ROOM',
                                            'urgent':'ROOM',
                                            'visited':'CORRIDOR'},
                               remapping={'room_counter_in':'sm_counter',
                                          'room_counter_out':'sm_counter'})


    # Create and start the introspection server for visualization
    sis = smach_ros.IntrospectionServer('server_name', sm, '/SM_ROOT')
    sis.start()

    # Execute the state machine
    outcome = sm.execute()

    # Wait for ctrl-c to stop the application
    rospy.spin()
    sis.stop()


if __name__ == '__main__':
    main()
