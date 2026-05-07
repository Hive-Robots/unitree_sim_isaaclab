# Copyright (c) 2025, Unitree Robotics Co., Ltd. All Rights Reserved.
# License: Apache License, Version 2.0
"""Minimal scene: ground plane, dome light, and a single wall."""
import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim.spawners.from_files.from_files_cfg import GroundPlaneCfg
from isaaclab.utils import configclass

from tasks.common_config import CameraBaseCfg  # isort: skip


@configclass
class FloorWallSceneCfg(InteractiveSceneCfg):
    """Empty scene with a ground plane and a single wall in front of the robot."""

    ground = AssetBaseCfg(
        prim_path="/World/GroundPlane",
        spawn=GroundPlaneCfg(),
    )

    # Wall ~0.60 m in front of a robot placed at the world origin facing +X.
    # 8 m wide (Y) gives ample room for the robot to step right repeatedly
    # along the wall — at vy=-0.4 in Isaac the effective drift per step is
    # ~0.5 m, so 8 m supports ~8 strips with comfortable margin.
    wall = AssetBaseCfg(
        prim_path="/World/envs/env_.*/Wall",
        init_state=AssetBaseCfg.InitialStateCfg(
            pos=[0.60, 0.0, 1.0],
            rot=[1.0, 0.0, 0.0, 0.0],
        ),
        spawn=sim_utils.CuboidCfg(
            size=(0.05, 8.0, 2.0),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.7, 0.7, 0.7)),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(kinematic_enabled=True),
        ),
    )

    light = AssetBaseCfg(
        prim_path="/World/light",
        spawn=sim_utils.DomeLightCfg(color=(0.75, 0.75, 0.75), intensity=3000.0),
    )

    world_camera = CameraBaseCfg.get_camera_config(
        prim_path="/World/PerspectiveCamera",
        pos_offset=(-1.5, -1.5, 1.5),
        rot_offset=(-0.27984, 0.67558, 0.6429, -0.26627),
    )
