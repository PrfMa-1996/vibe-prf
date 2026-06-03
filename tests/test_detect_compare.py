from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import detect_compare


class FakeTensor:
    def __init__(self, values):
        self.values = np.array(values)

    def detach(self):
        return self

    def cpu(self):
        return self

    def numpy(self):
        return self.values


class FakeScalar:
    def __init__(self, value):
        self.value = value

    def item(self):
        return self.value


class FakeClassIds:
    def __init__(self, values):
        self.values = values

    def __getitem__(self, index):
        return FakeScalar(self.values[index])


class FakeBoxes:
    def __init__(self, confidences, class_ids):
        self.conf = FakeTensor(confidences)
        self.cls = FakeClassIds(class_ids)

    def __len__(self):
        return len(self.conf.values)


def make_result(confidences=None, class_ids=None, names=None):
    boxes = None
    if confidences is not None:
        boxes = FakeBoxes(confidences, class_ids)
    return SimpleNamespace(boxes=boxes, names=names or {})


def test_read_image_decodes_file_bytes(monkeypatch, tmp_path):
    image_path = tmp_path / "cup.jpg"
    image_path.write_bytes(b"fake image bytes")
    decoded = np.zeros((2, 3, 3), dtype=np.uint8)

    monkeypatch.setattr(detect_compare.cv2, "imdecode", lambda data, flag: decoded)

    image = detect_compare.read_image(image_path)

    assert image is decoded


def test_read_image_raises_when_decode_fails(monkeypatch, tmp_path):
    image_path = tmp_path / "broken.jpg"
    image_path.write_bytes(b"not an image")
    monkeypatch.setattr(detect_compare.cv2, "imdecode", lambda data, flag: None)

    with pytest.raises(ValueError) as exc_info:
        detect_compare.read_image(image_path)

    assert str(image_path) in str(exc_info.value)


def test_run_inference_filters_to_cup_class_and_returns_elapsed_ms(monkeypatch):
    image = np.zeros((1, 1, 3), dtype=np.uint8)
    expected_result = object()
    model = SimpleNamespace()
    calls = []

    def fake_predict(received_image, classes, verbose):
        calls.append((received_image, classes, verbose))
        return [expected_result]

    model.predict = fake_predict
    ticks = iter([10.0, 10.125])
    monkeypatch.setattr(detect_compare.time, "perf_counter", lambda: next(ticks))

    result, elapsed_ms = detect_compare.run_inference(model, image)

    assert result is expected_result
    assert elapsed_ms == pytest.approx(125.0)
    assert calls == [(image, [detect_compare.CUP_CLASS_ID], False)]


def test_box_count_handles_missing_and_present_boxes():
    assert detect_compare.box_count(SimpleNamespace(boxes=None)) == 0
    assert detect_compare.box_count(make_result([0.1, 0.2], [41, 41])) == 2


def test_best_detection_returns_placeholder_without_boxes():
    assert detect_compare.best_detection(SimpleNamespace(boxes=None)) == ("-", "-")
    assert detect_compare.best_detection(make_result([], [], {})) == ("-", "-")


def test_best_detection_returns_highest_confidence_class_name():
    result = make_result(
        confidences=[0.35, 0.91, 0.72],
        class_ids=[1, 41, 99],
        names={41: "cup"},
    )

    assert detect_compare.best_detection(result) == ("cup", "0.9100")


def test_best_detection_falls_back_to_class_id_when_name_missing():
    result = make_result(confidences=[0.8], class_ids=[123], names={})

    assert detect_compare.best_detection(result) == ("123", "0.8000")


def test_save_result_image_writes_plotted_image(monkeypatch):
    plotted = np.zeros((2, 2, 3), dtype=np.uint8)
    result = SimpleNamespace(plot=lambda: plotted)
    writes = []

    monkeypatch.setattr(
        detect_compare.cv2,
        "imwrite",
        lambda output_path, image: writes.append((Path(output_path), image)) or True,
    )

    output_path = detect_compare.save_result_image(result, "unit_result.jpg")

    assert output_path == Path(detect_compare.__file__).with_name("unit_result.jpg")
    assert writes == [(output_path, plotted)]


def test_print_table_outputs_rows(capsys):
    rows = [
        {
            "name": "YOLOv8n",
            "time_ms": 12.345,
            "count": 2,
            "best_name": "cup",
            "confidence": "0.8765",
        }
    ]

    detect_compare.print_table(rows)

    output = capsys.readouterr().out
    assert "YOLOv8n" in output
    assert "12.35" in output
    assert "cup" in output
    assert "0.8765" in output


def test_run_comparison_builds_summary_rows(monkeypatch, tmp_path):
    image = np.zeros((2, 2, 3), dtype=np.uint8)
    result_one = make_result([0.5], [41], {41: "cup"})
    result_two = make_result([0.7, 0.6], [41, 41], {41: "cup"})
    inference_results = iter(
        [
            (result_one, 10.0),
            (result_two, 20.0),
            (result_two, 40.0),
            (result_one, 60.0),
        ]
    )
    loaded_weights = []

    class FakeYolo:
        def __init__(self, weights):
            loaded_weights.append(weights)

    monkeypatch.setattr(detect_compare, "MODELS", [("ModelA", "a.pt", "a.jpg"), ("ModelB", "b.pt", "b.jpg")])
    monkeypatch.setattr(detect_compare, "RUNS", 2)
    monkeypatch.setattr(detect_compare, "read_image", lambda path: image)
    monkeypatch.setattr(detect_compare, "YOLO", FakeYolo)
    monkeypatch.setattr(detect_compare, "run_inference", lambda model, received_image: next(inference_results))
    monkeypatch.setattr(
        detect_compare,
        "save_result_image",
        lambda result, output_name: tmp_path / output_name,
    )

    rows = detect_compare.run_comparison(tmp_path / "source.jpg")

    assert loaded_weights == ["a.pt", "b.pt"]
    assert rows == [
        {
            "name": "ModelA",
            "time_ms": 15.0,
            "count": 2,
            "best_name": "cup",
            "confidence": "0.7000",
            "image_path": tmp_path / "a.jpg",
        },
        {
            "name": "ModelB",
            "time_ms": 50.0,
            "count": 1,
            "best_name": "cup",
            "confidence": "0.5000",
            "image_path": tmp_path / "b.jpg",
        },
    ]
