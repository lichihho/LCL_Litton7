from PIL import Image
from matplotlib.figure import Figure
from torchvision import transforms
import gradio as gr
import matplotlib.pyplot as plt
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
NAS_DATABASE_ROOT = "/mnt/run_database"


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


def predict(imgfile: str) -> tuple[Figure]:
    with Image.open(imgfile) as img:
        image = img.convert("RGB")
    input_tensor = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(input_tensor)
        probs = F.softmax(logits[:, :7], dim=1).cpu()

    chart = draw_bar(LABELS, probs[0] * 100)

    return chart


def draw_bar(classes: str, probabilities: list[float]):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(classes, probabilities, color="skyblue")

    ax.set_xlabel("Class")
    ax.set_ylabel("Probability (%)")

    for i, prob in enumerate(probabilities):
        ax.text(i, prob + 0.01, f"{prob:.2f}%", ha="center", va="bottom")

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
            '<div class="main-title">Litton7 景觀分類模型</div>'
            '<div class="reference">'
            '<a href="https://www.airitilibrary.com/article/detail/10125434-n202406210003-00003" target="_blank">'
            "何立智、李沁築、邱浩修(2024)。Litton7：Litton視覺景觀分類深度學習模型。戶外遊憩研究，37(2)"
            "</a>"
            "</div>"
        ),
    )
    with gr.Row(equal_height=True):
        with gr.Column():
            image_input = gr.Image(label="上傳影像", type="filepath", height="256px")
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

    gr.HTML(
        '<div class="footer">© 2024 LCL 版權所有<br>開發者：何立智、楊哲睿</div>',
    )

    start.click(
        fn=predict,
        inputs=image_input,
        outputs=bar_chart,
    )

    ex1.select(fn=choose_example, inputs=ex1, outputs=image_input)
    ex2.select(fn=choose_example, inputs=ex2, outputs=image_input)
    ex3.select(fn=choose_example, inputs=ex3, outputs=image_input)

if __name__ == "__main__":
    webapp.launch()
