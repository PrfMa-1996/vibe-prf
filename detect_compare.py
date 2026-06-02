import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import cv2
import matplotlib
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from PIL import Image, ImageTk
from ultralytics import YOLO


matplotlib.use("TkAgg")

CUP_CLASS_ID = 41
RUNS = 3

MODELS = [
    ("YOLOv5n", "yolov5nu.pt", "result_yolov5.jpg"),
    ("YOLOv8n", "yolov8n.pt", "result_yolov8.jpg"),
    ("YOLOv10n", "yolov10n.pt", "result_yolov10.jpg"),
]

BG = "#111827"
PANEL_BG = "#1f2937"
TEXT = "#e5e7eb"
MUTED = "#9ca3af"
ACCENT = "#38bdf8"
BAR_COLORS = ["#38bdf8", "#22c55e", "#f59e0b"]


def choose_image(root):
    return filedialog.askopenfilename(
        parent=root,
        title="选择测试图片",
        filetypes=[
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.webp"),
            ("所有文件", "*.*"),
        ],
    )


def read_image(image_path):
    data = np.fromfile(str(image_path), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"无法读取图片: {image_path}")
    return image


def run_inference(model, image):
    start = time.perf_counter()
    result = model.predict(image, classes=[CUP_CLASS_ID], verbose=False)[0]
    elapsed_ms = (time.perf_counter() - start) * 1000
    return result, elapsed_ms


def box_count(result):
    if result.boxes is None:
        return 0
    return len(result.boxes)


def best_detection(result):
    if result.boxes is None or len(result.boxes) == 0:
        return "-", "-"

    confidences = result.boxes.conf.detach().cpu().numpy()
    best_index = int(np.argmax(confidences))
    class_id = int(result.boxes.cls[best_index].item())
    class_name = result.names.get(class_id, str(class_id))
    return class_name, f"{confidences[best_index]:.4f}"


def save_result_image(result, output_name):
    plotted = result.plot()
    output_path = Path(__file__).with_name(output_name)
    cv2.imwrite(str(output_path), plotted)
    return output_path


def print_table(rows):
    headers = ["模型名称", "推理时间(ms)", "检测数量", "最高置信度目标", "置信度"]
    widths = [len(header) for header in headers]

    for row in rows:
        values = [row["name"], f"{row['time_ms']:.2f}", row["count"], row["best_name"], row["confidence"]]
        for i, cell in enumerate(values):
            widths[i] = max(widths[i], len(str(cell)))

    def line(values):
        return " | ".join(str(value).ljust(widths[i]) for i, value in enumerate(values))

    print(line(headers))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(
            line(
                [
                    row["name"],
                    f"{row['time_ms']:.2f}",
                    row["count"],
                    row["best_name"],
                    row["confidence"],
                ]
            )
        )


def load_preview(path, max_size=(360, 260)):
    image = Image.open(path).convert("RGB")
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(image)


def build_chart(parent, rows):
    figure = Figure(figsize=(9.4, 2.8), dpi=100, facecolor=BG)
    axis = figure.add_subplot(111, facecolor=BG)

    names = [row["name"] for row in rows]
    times = [row["time_ms"] for row in rows]
    bars = axis.bar(names, times, color=BAR_COLORS, width=0.55)

    axis.set_title("Inference Time Comparison", color=TEXT, fontsize=13, pad=12)
    axis.set_ylabel("ms", color=MUTED)
    axis.tick_params(axis="x", colors=TEXT)
    axis.tick_params(axis="y", colors=MUTED)
    axis.grid(axis="y", color="#374151", linewidth=0.8, alpha=0.75)
    axis.set_axisbelow(True)
    for spine in axis.spines.values():
        spine.set_color("#374151")

    for bar, value in zip(bars, times):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.1f}",
            ha="center",
            va="bottom",
            color=TEXT,
            fontsize=10,
        )

    figure.tight_layout(pad=1.4)
    canvas = FigureCanvasTkAgg(figure, master=parent)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.configure(bg=BG, highlightthickness=0)
    return widget


def show_report(root, rows, source_image_path):
    root.title("目标检测模型性能对比报告")
    root.configure(bg=BG)
    root.geometry("1240x860")
    root.minsize(1050, 760)
    root.deiconify()

    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)

    title = tk.Label(
        root,
        text="目标检测模型性能对比报告",
        bg=BG,
        fg=TEXT,
        font=("Microsoft YaHei UI", 24, "bold"),
        pady=18,
    )
    title.grid(row=0, column=0, sticky="ew")

    content = tk.Frame(root, bg=BG, padx=22, pady=6)
    content.grid(row=1, column=0, sticky="nsew")
    for index in range(3):
        content.grid_columnconfigure(index, weight=1, uniform="model")

    image_refs = []
    for index, row in enumerate(rows):
        card = tk.Frame(content, bg=PANEL_BG, padx=16, pady=16, highlightthickness=1, highlightbackground="#374151")
        card.grid(row=0, column=index, sticky="nsew", padx=10)
        card.grid_columnconfigure(0, weight=1)

        photo = load_preview(row["image_path"])
        image_refs.append(photo)
        image_label = tk.Label(card, image=photo, bg=PANEL_BG)
        image_label.grid(row=0, column=0, sticky="n", pady=(0, 12))

        name_label = tk.Label(
            card,
            text=row["name"],
            bg=PANEL_BG,
            fg=TEXT,
            font=("Microsoft YaHei UI", 16, "bold"),
        )
        name_label.grid(row=1, column=0, pady=(0, 12))

        metrics = (
            f"推理时间: {row['time_ms']:.2f} ms\n"
            f"检测数量: {row['count']}\n"
            f"最高置信度: {row['confidence']}"
        )
        metric_label = tk.Label(
            card,
            text=metrics,
            bg=PANEL_BG,
            fg=MUTED,
            justify="left",
            font=("Microsoft YaHei UI", 12),
        )
        metric_label.grid(row=2, column=0, sticky="w")

    chart_frame = tk.Frame(root, bg=BG, padx=30, pady=18)
    chart_frame.grid(row=2, column=0, sticky="ew")
    chart_frame.grid_columnconfigure(0, weight=1)

    chart = build_chart(chart_frame, rows)
    chart.grid(row=0, column=0, sticky="ew")

    footer = tk.Label(
        root,
        text=f"测试图片: {source_image_path}",
        bg=BG,
        fg=MUTED,
        font=("Microsoft YaHei UI", 10),
        anchor="w",
        padx=30,
        pady=8,
    )
    footer.grid(row=3, column=0, sticky="ew")

    root.image_refs = image_refs


def run_comparison(image_path):
    image = read_image(image_path)
    rows = []

    for display_name, weights, output_name in MODELS:
        print(f"Loading {display_name}: {weights}")
        model = YOLO(weights)

        timings = []
        last_result = None
        for _ in range(RUNS):
            last_result, elapsed_ms = run_inference(model, image)
            timings.append(elapsed_ms)

        average_ms = sum(timings) / len(timings)
        output_path = save_result_image(last_result, output_name)
        best_name, best_conf = best_detection(last_result)

        rows.append(
            {
                "name": display_name,
                "time_ms": average_ms,
                "count": box_count(last_result),
                "best_name": best_name,
                "confidence": best_conf,
                "image_path": output_path,
            }
        )

    return rows


def main():
    root = tk.Tk()
    root.withdraw()

    image_path = choose_image(root)
    if not image_path:
        root.destroy()
        return

    try:
        rows = run_comparison(Path(image_path))
    except Exception as exc:
        messagebox.showerror("检测失败", str(exc), parent=root)
        root.destroy()
        raise

    print()
    print_table(rows)
    show_report(root, rows, image_path)
    root.mainloop()


if __name__ == "__main__":
    main()
