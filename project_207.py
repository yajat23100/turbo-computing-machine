import glob
import os
import sys
import random
import time
import numpy as np
import cv2
import mayavi as mlab

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

IM_WIDTH = 640
IM_HEIGHT = 480


def image(image):
    matrix_representational_data = np.array(image.raw_data)
    reshape_of_image = matrix_representational_data.reshape((IM_HEIGHT, IM_WIDTH, 4))
    live_feed_from_camera = reshape_of_image[:, :, :3]
    cv2.imshow("", live_feed_from_camera)
    cv2.waitKey(1)
    return


def camera(get_blueprint_of_world):
    camera_sensor = get_blueprint_of_world.find('sensor.camera.rgb')
    camera_sensor.set_attribute('image_size_x', f'{IM_WIDTH}')
    camera_sensor.set_attribute('image_size_y', f'{IM_HEIGHT}')
    camera_sensor.set_attribute('fov', '70')
    return camera_sensor


def car_control():
    dropped_vehicle.apply_control(carla.VehicleControl(hand_brake=True))
    time.sleep(10)
    location = dropped_vehicle.get_location()

    return location


data = []
actor_list = []
try:
    client = carla.Client('127.0.0.1', 2000)
    client.set_timeout(2.0)
    world = client.get_world()
    get_blueprint_of_world = world.get_blueprint_library()
    car_model = get_blueprint_of_world.filter('model3')[0]
    spawn_point = (world.get_map().get_spawn_points()[1])
    dropped_vehicle = world.spawn_actor(car_model, spawn_point)

    simulator_camera_location_rotation = carla.Transform(spawn_point.location, spawn_point.rotation)
    simulator_camera_location_rotation.location += spawn_point.get_forward_vector() * 30
    simulator_camera_location_rotation.rotation.yaw += 180
    simulator_camera_view = world.get_spectator()
    simulator_camera_view.set_transform(simulator_camera_location_rotation)
    location = dropped_vehicle.get_location()
    print("Car present location:", location)

    camera_sensor = camera(get_blueprint_of_world)
    sensor_camera_spawn_point = carla.Transform(carla.Location(x=2.5, z=0.7))
    sensor = world.spawn_actor(camera_sensor, sensor_camera_spawn_point, attach_to=dropped_vehicle)
    actor_list.append(sensor)
    sensor.listen(lambda camera_data: image(camera_data))

    car_new_location = car_control()
    print("Car new location:", car_new_location)

    actor_list.append(dropped_vehicle)
finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')
