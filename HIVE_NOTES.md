# Hive-specific changes on the `hive/floor-wall` branch

This file tracks every diff we carry vs. upstream `unitreerobotics/unitree_sim_isaaclab`. Keep it current when you patch the submodule. Anything not listed here should match upstream.

The submodule is vendored under `ki_orchestrator/third_party/unitree_sim_isaaclab/`. Edits ride on the `hive/floor-wall` branch; the parent ki_orchestrator pins to a specific SHA on that branch.

## New files

- `tasks/common_scene/base_scene_floor_wall.py` — minimal scene (ground + dome light + a single wall) for the painting orchestrator's ROI / coverage / step loop.
- `tasks/g1_tasks/floor_wall_g1_29dof_dex1_wholebody/` — task package that registers `Isaac-FloorWall-G129-Dex1-Wholebody` against the floor_wall scene with the Wholebody RL policy.
- `HIVE_NOTES.md` — this file.

## Modified files

- `tasks/g1_tasks/__init__.py` — imports the new `floor_wall_g1_29dof_dex1_wholebody` package so the auto-walker triggers `gym.register` for it on `import tasks`.
- `tasks/common_config/camera_configs.py` — `g1_front_camera()` now models a **Luxonis OAK-1 Lite** mounted on top of the head (`focal_length=14.56`, `pos_offset=(0,0,0.10)`, HFOV ≈ 69°), replacing the upstream wide-angle d435 defaults. This is the camera the orchestrator's `--isaac-camera head` (default) consumes.
- `tools/episode_writer.py`, `tools/rerun_visualizer.py` — `logging_mp.get_logger` → `logging_mp.getLogger` to align with the bumped teleimager submodule's logging API.
- `sim_main.py` — two robustness fixes (2026-05-08):
  - **SIGINT/SIGTERM unlinks `/dev/shm/psm_*` and `/dev/shm/isaac_*_image_shm`.** Python's `resource_tracker` only *warns* about leaked POSIX shared-memory segments at shutdown; it doesn't unlink them. Stale segments persist across runs and poison DDS discovery for the next sim launch (the new participant attaches to the old shm, sees inconsistent state, and the new `rt/lowstate` publisher becomes silently invisible to subscribers — observed end-to-end on 2026-05-08). The new `_cleanup_shm()` helper unlinks segments owned by the current uid; called from `signal_handler` after the existing controller/dds/image-server stops.
  - **`--robot_type` argparse `choices=("g129", "h1_2", "g129dof")`.** Argparse rejects unknowns at parse time, exiting with code 2 + clean stderr *before* any DDS / image-server / Isaac-Sim init. Closes a silent half-failure mode where a typo (e.g. `--robot_type g12` observed on 2026-05-08) crashed action-provider creation while the image server still came up — making the sim look healthy but with no robot DDS publisher, so subscribers hung forever waiting for `rt/lowstate`. Choices set is the union of literals the codebase already compares against in `dds/dds_create.py` and `tasks/common_config/robot_configs.py`; extend the tuple when a new robot type is added.
- `teleimager` (sub-submodule) — on the `hive/floor-wall` branch off upstream `e3d63a7`. Hive patch:
  - `cam_config_server.yaml` — `head_camera.binocular: true → false` and `image_shape: [480, 1280] → [480, 640]`. Upstream's binocular branch (`image_server.py:1158-1166`) reads the `"left"`/`"right"` shared-memory keys (which the IsaacSim writer fills from the **wrist** cameras), so with `binocular=true` the published `head_camera` feed was actually two wrists concatenated, not the front_camera. Monocular makes it read the `"head"` shm key correctly populated from `front_camera`.

## Wall geometry knobs (in `base_scene_floor_wall.py`)

- `pos=[0.60, 0.0, 1.0]` — wall sits 0.60 m in front of the robot, world origin facing +X. Tuned away from `0.55` after a hand-vs-wall collision during the paint trajectory (2026-05-07).
- `size=(0.05, 8.0, 2.0)` — 5 cm thick, 8 m wide (Y), 2 m tall (Z). The 8 m width gives ~8 step-rights of margin at the Wholebody RL policy's effective ~0.5 m drift per step (commanded at vy=-0.4).
