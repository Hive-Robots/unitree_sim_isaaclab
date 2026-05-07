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
- `teleimager` (sub-submodule) — on the `hive/floor-wall` branch off upstream `e3d63a7`. Hive patch:
  - `cam_config_server.yaml` — `head_camera.binocular: true → false` and `image_shape: [480, 1280] → [480, 640]`. Upstream's binocular branch (`image_server.py:1158-1166`) reads the `"left"`/`"right"` shared-memory keys (which the IsaacSim writer fills from the **wrist** cameras), so with `binocular=true` the published `head_camera` feed was actually two wrists concatenated, not the front_camera. Monocular makes it read the `"head"` shm key correctly populated from `front_camera`.

## Wall geometry knobs (in `base_scene_floor_wall.py`)

- `pos=[0.60, 0.0, 1.0]` — wall sits 0.60 m in front of the robot, world origin facing +X. Tuned away from `0.55` after a hand-vs-wall collision during the paint trajectory (2026-05-07).
- `size=(0.05, 8.0, 2.0)` — 5 cm thick, 8 m wide (Y), 2 m tall (Z). The 8 m width gives ~8 step-rights of margin at the Wholebody RL policy's effective ~0.5 m drift per step (commanded at vy=-0.4).

## Pushability

The `hive/floor-wall` branch lives only on the developer machine until pushed to a Hive-controlled fork on GitHub. Until then, the submodule SHA pinned in ki_orchestrator can't be cloned by anyone else — they'd land on upstream `main` and lose all the changes above. Setting up a fork is the natural next step before sharing.
