from PIL import Image
from datetime import datetime
from itertools import islice, batched
from matplotlib.figure import Figure
from torchvision import transforms
from typing import Iterator
import csv
import gradio as gr
import matplotlib.pyplot as plt
import os
import pandas as pd
import tempfile
import torch
import torch.nn.functional as F


LABELS = [
    "Panoramic",
    "Feature",
    "Detail",
    "Enclosed",
    "Focal",
    "Ephemeral",
    "Canopied",
]
NAS_DATABASE_ROOT = "/mnt/ai_data/"
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", 128))

if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    torch.device("cpu")
model = torch.load(
    "/app/Litton-7type-visual-landscape-model.pth",
    map_location=device,
    weights_only=False,
).module
model.eval()
preprocess = transforms.Compose(
    [
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


def predict(imgfile: str) -> tuple[Figure, gr.DownloadButton]:
    with Image.open(imgfile) as img:
        image = img.convert("RGB")
    input_tensor = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(input_tensor)
        probs = F.softmax(logits[:, :7], dim=1).cpu()

    chart = draw_bar(LABELS, probs[0] * 100)

    timestamp = datetime.now().strftime("%Y%b%d-%H%M%S")
    fname = os.path.split(imgfile)[-1]
    fstem = os.path.splitext(fname)[0]
    (_, tmpfname) = tempfile.mkstemp(
        prefix=f"Litton7-{fstem}-{timestamp}", suffix=".csv"
    )
    with open(tmpfname, "w", newline="") as fcsv:
        writer = csv.writer(fcsv)
        writer.writerow(["fid"] + [label.lower() for label in LABELS])
        writer.writerow([fname] + [round(float(prob), 4) for prob in probs[0]])

    btn = gr.DownloadButton("下載結果", value=tmpfname, visible=True)

    return chart, btn


def batch_predict(
    dataset: str, progress=gr.Progress()
) -> tuple[Figure, pd.DataFrame, gr.DownloadButton]:
    "predict the whole database"
    progress(0, desc="⌛ 載入影像列表...")

    imgpaths = list(iter_image(dataset))

    if len(imgpaths) == 0:
        raise gr.Error("此資料集不含任何影像", duration=10)

    top1_counts: list[int] = [0] * len(LABELS)
    results = {}
    cursor = 0
    for paths in batched(imgpaths, BATCH_SIZE):
        images = []
        for path in paths:
            with Image.open(path) as img:
                images.append(img.convert("RGB"))

        if len(images) == 0:
            break

        tensors = torch.stack([preprocess(img) for img in images]).to(device)
        with torch.no_grad():
            logits = model(tensors)
            probs = F.softmax(logits[:, :7], dim=1).cpu()

        fname = [path.replace(f"{NAS_DATABASE_ROOT}/", "") for path in paths]
        results.setdefault("fid", []).extend(fname)
        for i, label in enumerate(LABELS):
            results.setdefault(label.lower(), []).extend(
                [round(prob, 4) for prob in probs[:, i].tolist()]
            )

        for i in range(probs.shape[0]):
            top1_counts[torch.argmax(probs[i])] += 1

        cursor += len(paths)
        progress(cursor / len(imgpaths), desc=f"🔎 {os.path.split(dataset)[-1]}")

    # top1_ratio = [top1_sum[label] / len(imgpaths) for label in LABELS]

    chart = draw_pie(LABELS, top1_counts)

    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%b%d-%H%M%S")
    dataset_name = os.path.split(dataset)[-1]
    (_, tmpfname) = tempfile.mkstemp(
        prefix=f"Litton7-{dataset_name}-{timestamp}", suffix=".csv"
    )
    df.fid = df.fid.str.replace(f"{NAS_DATABASE_ROOT}/", "")
    df.to_csv(tmpfname, index=False)

    btn = gr.DownloadButton("下載結果", value=tmpfname, visible=True)

    return chart, df, btn


def list_dataset() -> gr.Dropdown:
    dirs = [
        name
        for name in os.listdir(NAS_DATABASE_ROOT)
        if os.path.isdir(os.path.join(NAS_DATABASE_ROOT, name))
    ]
    datasets = [(dirname, os.path.join(NAS_DATABASE_ROOT, dirname)) for dirname in dirs]
    return gr.Dropdown(choices=datasets)


def get_previews(dataset: str) -> list[tuple[str, str]]:
    images = islice(iter_image(dataset), 10)
    return [(path, os.path.split(path)[-1]) for path in images]


def iter_image(root: str) -> Iterator[str]:
    accepted_exts = (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp")
    files = (
        os.path.join(dirpath, filename)
        for dirpath, _, filenames in os.walk(root)
        for filename in filenames
        if filename.lower().endswith(accepted_exts)
    )
    for file in files:
        try:
            with Image.open(file) as img:
                img.verify()
        except Exception:
            continue

        yield file


def draw_bar(classes: str, probabilities: list[float]):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(classes, probabilities, color="skyblue")

    ax.set_xlabel("Class")
    ax.set_ylabel("Probability (%)")

    for i, prob in enumerate(probabilities):
        ax.text(i, prob + 0.01, f"{prob:.2f}%", ha="center", va="bottom")

    fig.tight_layout()

    return fig


def draw_pie(classes: str, class_counts: list[int]):
    fig, ax = plt.subplots(figsize=(8, 6))

    def genpct(pct, data):
        absolute = int(round(pct / 100.0 * sum(data)))

        return f"{pct:.1f}%\n({absolute:d})"

    wedges, texts, autotexts = ax.pie(
        class_counts, autopct=lambda pct: genpct(pct, class_counts)
    )
    ax.legend(wedges, classes, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    fig.tight_layout()

    return fig


def choose_example(imgpath: str) -> gr.Image:
    img = Image.open(imgpath)
    width, height = img.size
    ratio = 512 / max(width, height)
    img = img.resize((int(width * ratio), int(height * ratio)))
    return gr.Image(value=img, label="輸入影像（不支援 SVG 格式）", type="filepath")


css = """
.main-title {
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
}
.reference {
    text-align: center;
    font-size: 1.2em;
    color: #d1d5db;
    margin-bottom: 20px;
}
.reference a {
    color: #FB923C;
    text-decoration: none;
}
.reference a:hover {
    text-decoration: underline;
    color: #FB923C;
}
.title {
    border-bottom: 1px solid;
}
.footer {
    text-align: center;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #ddd;
    color: #d1d5db;
    font-size: 14px;
}
"""
theme = gr.themes.Base(
    primary_hue="orange",
    secondary_hue="cyan",
    neutral_hue="gray",
    font=gr.themes.GoogleFont("Source Sans Pro"),
).set(
    body_text_color="*neutral_100",
    body_text_color_subdued="*neutral_600",
    background_fill_primary="*neutral_950",
    background_fill_secondary="*neutral_600",
    border_color_accent="*secondary_800",
    color_accent="*primary_50",
    color_accent_soft="*secondary_800",
    code_background_fill="*neutral_700",
    block_background_fill_dark="*body_background_fill",
    block_info_text_color="#6b7280",
    block_label_text_color="*neutral_300",
    block_label_text_weight="700",
    block_title_text_color="*block_label_text_color",
    block_title_text_weight="300",
    panel_background_fill="*neutral_800",
    table_text_color_dark="*secondary_800",
    checkbox_background_color_selected="*primary_500",
    checkbox_label_background_fill="*neutral_500",
    checkbox_label_background_fill_hover="*neutral_700",
    checkbox_label_text_color="*neutral_200",
    input_background_fill="*neutral_700",
    input_background_fill_focus="*neutral_600",
    slider_color="*primary_500",
    table_even_background_fill="*neutral_700",
    table_odd_background_fill="*neutral_600",
    table_row_focus="*neutral_800",
)
with gr.Blocks(css=css, theme=theme) as webapp:
    gr.HTML(
        value=(
            '<div class="main-title">litton7景觀分類模型</div>'
            '<div class="reference">'
            '<a href="https://www.airitilibrary.com/article/detail/10125434-n202406210003-00003" target="_blank">'
            "何立智、李沁築、邱浩修(2024)。Litton7：Litton視覺景觀分類深度學習模型。戶外遊憩研究，37(2)"
            "</a>"
            "</div>"
        ),
    )
    with gr.Tab("上傳單張影像"):
        with gr.Row(equal_height=True):
            with gr.Column():
                image_input = gr.Image(
                    label="上傳影像", type="filepath", height="256px"
                )
                with gr.Group():
                    gr.Label("範例影像", show_label=False)
                    with gr.Row():
                        ex1 = gr.Image(
                            value="examples/creek_4507_00004840.jpg",
                            show_label=False,
                            type="filepath",
                            elem_classes="example-image",
                            interactive=False,
                            show_download_button=False,
                            show_fullscreen_button=False,
                            show_share_button=False,
                        )
                        ex2 = gr.Image(
                            value="examples/blue-and-white-can-on-brown-wooden-table-mMNKYx0QOoU.jpg",
                            show_label=False,
                            type="filepath",
                            elem_classes="example-image",
                            interactive=False,
                            show_download_button=False,
                            show_fullscreen_button=False,
                            show_share_button=False,
                        )
                        ex3 = gr.Image(
                            value="examples/corn_field_3921_00002540.jpg",
                            show_label=False,
                            type="filepath",
                            elem_classes="example-image",
                            interactive=False,
                            show_download_button=False,
                            show_fullscreen_button=False,
                            show_share_button=False,
                        )
            bar_chart = gr.Plot(label="分類結果")
        with gr.Row():
            start = gr.Button("開始分類", variant="primary")
            download = gr.DownloadButton(visible=False)
    with gr.Tab("從 NAS 上選擇資料集") as database_tab:
        with gr.Row(equal_height=True):
            with gr.Column():
                dataset = gr.Dropdown(label="選擇一個資料集")
                preview = gr.Gallery(label="資料集預覽")
            pie_chart = gr.Plot(label="Top 1 類別分佈")
        with gr.Row():
            start_database = gr.Button("開始分類", variant="primary")
            download_database = gr.DownloadButton(visible=False)
        result = gr.DataFrame()

    gr.HTML(
        '<div class="footer">© 2024 LCL 版權所有<br>開發者：何立智、楊哲睿</div>',
    )

    database_tab.select(fn=list_dataset, outputs=dataset)
    dataset.change(fn=get_previews, inputs=dataset, outputs=preview)

    start.click(
        fn=predict,
        inputs=image_input,
        outputs=[bar_chart, download],
    )
    start_database.click(
        fn=batch_predict,
        inputs=dataset,
        outputs=[pie_chart, result, download_database],
    )

    ex1.select(fn=choose_example, inputs=ex1, outputs=image_input)
    ex2.select(fn=choose_example, inputs=ex2, outputs=image_input)
    ex3.select(fn=choose_example, inputs=ex3, outputs=image_input)

if __name__ == "__main__":
    webapp.launch()
