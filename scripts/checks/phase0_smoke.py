"""Phase 0 compatibility diagnostic; no dataset, downloads or trained weights."""

import json
import multiprocessing as mp
import os
import sys


def cpu_probe(connection):
    import torch
    import torchvision
    from torchvision.models import efficientnet_b0, resnet50

    torch.set_num_threads(2)
    torch.manual_seed(0)
    result = {"pid": os.getpid(), "device": "cpu", "finite": True,
              "torch": torch.__version__, "torchvision": torchvision.__version__}
    with torch.inference_mode():
        for name, factory in [("efficientnet_b0", efficientnet_b0), ("resnet50", resnet50)]:
            model = factory(weights=None, num_classes=10).eval()
            output = model(torch.zeros(1, 3, 224, 224))
            assert list(output.shape) == [1, 10], name
            assert bool(torch.isfinite(output).all()), name
            result[name] = list(output.shape)
            del model
    connection.send(result)
    connection.close()


def main():
    import platform
    from importlib.metadata import version
    from PySide6.QtCore import QTimer
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QWidget

    context = mp.get_context("spawn")
    parent, child = context.Pipe(duplex=False)
    worker = context.Process(target=cpu_probe, args=(child,))
    worker.start()
    child.close()
    try:
        if not parent.poll(90):
            raise TimeoutError("CPU/spawn diagnostic exceeded 90 seconds")
        probe = parent.recv()
        worker.join(5)
        if worker.exitcode != 0:
            raise RuntimeError(f"Worker exit code: {worker.exitcode}")
    finally:
        parent.close()
        if worker.is_alive():
            worker.terminate()
            worker.join(5)

    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("Phase 0 compatibility diagnostic")
    window.resize(320, 100)
    window.show()
    qt = {"platform": app.platformName(), "window_exposed":
          QTest.qWaitForWindowExposed(window, 5000), "timer_fired": False}

    def finish():
        qt["timer_fired"] = True
        window.close()
        app.quit()

    QTimer.singleShot(100, finish)
    exitcode = app.exec()
    assert exitcode == 0 and qt["window_exposed"] and qt["timer_fired"]
    assert qt["platform"] == "windows", "Native Windows Qt plugin required"
    print(json.dumps({
        "python": platform.python_version(), "platform": platform.platform(),
        "parent_pid": os.getpid(), "worker_exitcode": worker.exitcode,
        "worker": probe, "qt": qt, "frozen": bool(getattr(sys, "frozen", False)),
        "packages": {name: version(name) for name in ["torch", "torchvision",
                     "PySide6-Essentials", "shiboken6", "Pillow", "PyInstaller", "numpy"]},
        "pretrained_weights_loaded": False, "training_performed": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    mp.freeze_support()
    main()
