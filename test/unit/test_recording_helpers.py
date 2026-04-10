from __future__ import annotations


def test_recorder_can_manage_recording_points(nrv_module) -> None:
    recorder = nrv_module.recorder("endoneurium_ranck")
    recorder.set_recording_point(100, 10, 0)
    recorder.set_recording_point(200, -10, 5)

    assert recorder.is_empty() is False
    assert len(recorder.recording_points) == 2
    assert recorder.recording_points[0].get_ID() == 0
    assert recorder.recording_points[1].get_ID() == 1


def test_recorder_group_transform_updates_points(nrv_module) -> None:
    recorder = nrv_module.recorder("endoneurium_ranck")
    recorder.set_recording_point(100, 10, 0)

    recorder.translate(y=5, z=-2)
    recorder.rotate(angle=90, degree=True)

    point = recorder.recording_points[0]

    assert point.x == 100
    assert point.y != 10
    assert point.z != 0
