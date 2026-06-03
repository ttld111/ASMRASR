import os
import glob
import sys
from pathlib import Path
import torch

# =====================================================================
# 终极修复：强制重写 weights_only 参数，彻底粉碎 PyTorch 2.6 的拦截
# =====================================================================
_original_load = torch.load
def _patched_load(*args, **kwargs):
    # 强制将 weights_only 设为 False，不管上游库（如 Lightning）传的是什么
    kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)
torch.load = _patched_load
# =====================================================================

import pysrt

# =====================================================================
# 临时修复：NumPy 2.0 移除 np.NaN 导致 pyannote 崩溃的问题
# =====================================================================
import numpy as np
if not hasattr(np, "NaN"):
    np.NaN = np.nan  # 给 numpy 动态补上 NaN 属性，防止旧版 pyannote 报错

# =====================================================================
# 核心修复：跳过 ffmpeg_downloader 自动下载，直接关联同目录下的 ffmpeg
# =====================================================================
current_dir = Path(__file__).resolve().parent
local_ffmpeg_bin = current_dir / "ffmpeg" / "bin"

if local_ffmpeg_bin.exists():
    ffmpeg_path_str = str(local_ffmpeg_bin)
    if ffmpeg_path_str not in os.environ["PATH"]:
        os.environ["PATH"] = ffmpeg_path_str + os.path.pathsep + os.environ["PATH"]
    print(f"成功加载本地 FFmpeg 路径: {ffmpeg_path_str}")
else:
    print(f"⚠️ 警告: 未在 {local_ffmpeg_bin} 找到 ffmpeg/bin，请检查文件夹摆放位置！")

# =====================================================================
# 正常加载后续依赖
# =====================================================================
from pyannote.audio import Model
from pyannote.audio.pipelines import VoiceActivityDetection
from settings import config

extensions = ("wav", "mp3", "flac")
pattern = os.path.join(config["path"]["audio"], "*.*")
audio_files = [
    f for f in glob.glob(pattern)
    if f.lower().endswith(extensions)
]

if not audio_files:
    print(f"在 {config['path']['audio']} 中没有找到可处理的音频文件")
    exit(0)

print('设备:', config["device"])

# 2. 初始化 VAD 模型
vad = Model.from_pretrained(
    checkpoint=config["model"]["vad"],
    cache_dir=config["path"]["model"]
)
vad.to(torch.device(config["device"]))

vad_pipeline = VoiceActivityDetection(segmentation=vad)
vad_pipeline.instantiate({
    "min_duration_on": config["vad"]["min_duration_on"],
    "min_duration_off": config["vad"]["min_duration_off"],
})

# 3. 开始循环处理
for audio_path in audio_files:
    print(f"\n处理音频: {audio_path}")

    file_obj = Path(audio_path)
    basename = file_obj.stem
    vad_log_path = os.path.join(config["path"]["vad"], f"{basename}.srt")

    # 4. 执行 VAD 识别
    vad_result = vad_pipeline(audio_path)

    # 5. 生成 SRT
    srt = pysrt.SubRipFile()
    for idx, (segment, _, _) in enumerate(vad_result.itertracks(yield_label=True), start=1):
        sub_item = pysrt.SubRipItem(
            index=idx,
            start=pysrt.SubRipTime.from_ordinal(int(segment.start * 1000)),
            end=pysrt.SubRipTime.from_ordinal(int(segment.end * 1000)),
            text=f"Speech_{idx}"
        )
        srt.append(sub_item)

    srt.save(vad_log_path, encoding='utf-8')
    print(f"VAD记录写入完成: {vad_log_path}")

print("\n所有音频 VAD 处理完毕！")