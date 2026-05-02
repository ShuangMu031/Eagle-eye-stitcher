import time
import traceback
from pathlib import Path

from stitcher.common.image_utils import ensure_directory
from stitcher.common.logger import get_logger
from stitcher.io.image_io import cv_imwrite
from stitcher.pipeline.stitching_pipeline import StitchingPipeline

logger = get_logger(__name__)


def run_stitching_worker(image_paths, config, progress_queue, result_queue, output_path):
    try:
        output_path = str(output_path)
        ensure_directory(str(Path(output_path).parent))

        pipeline = StitchingPipeline()
        pipeline.update_config(config or {})
        pipeline.load_images(list(image_paths))

        def progress_callback(step, total, message):
            try:
                total = max(int(total), 1)
                step = max(0, min(int(step), total))
                progress = int((step / total) * 100)
                progress_queue.put(("progress", progress, message))
            except Exception as callback_error:
                logger.warning(f"发送进度消息失败: {callback_error}")

        pipeline.set_progress_callback(progress_callback)

        t0 = time.time()
        result = pipeline.run(output_path=output_path)
        elapsed = time.time() - t0

        if result is False:
            result_queue.put(("error", "图像拼接失败，请检查输入图像、图像顺序或日志。"))
            return

        seam_path = None
        if pipeline.seam_mask is not None and pipeline.result_image is not None:
            seam_path = str(Path(output_path).with_stem(Path(output_path).stem + "_seam"))
            seam_overlay = StitchingPipeline.overlay_seam(
                pipeline.result_image, pipeline.seam_mask,
                color=(0, 0, 255), dilate_radius=2
            )
            cv_imwrite(seam_path, seam_overlay)

        result_queue.put(("done", output_path, elapsed, seam_path))

    except Exception as exc:
        logger.exception("子进程执行拼接失败")
        result_queue.put(("error", f"{exc}\n\n{traceback.format_exc()}"))
