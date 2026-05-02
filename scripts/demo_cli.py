import argparse
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from stitcher.pipeline.stitching_pipeline import StitchingPipeline
from stitcher.io.image_io import cv_imwrite
from stitcher.common.logger import setup_logger


def main():
    parser = argparse.ArgumentParser(
        description='多图顺序拼接命令行工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python demo_cli.py image1.png image2.png image3.png -o result.png
  python demo_cli.py img1.jpg img2.jpg img3.jpg --seam-band 15 --feather-radius 20
  python demo_cli.py img1.jpg img2.jpg --show-seam -o result.png

说明: 按输入顺序依次拼接多张图像。后一张作为基础图不动，当前拼接结果作为待变换图继续参与下一轮拼接。
        """
    )

    parser.add_argument(
        'images',
        nargs='+',
        help='要拼接的图像文件路径（至少两张）'
    )

    parser.add_argument(
        '-o', '--output',
        default='./outputs/result.png',
        help='输出文件路径（默认：./outputs/result.png）'
    )

    parser.add_argument(
        '--seam-band',
        type=int,
        default=9,
        help='融合带宽（默认：9）'
    )

    parser.add_argument(
        '--feather-radius',
        type=int,
        default=11,
        help='羽化半径（默认：11）'
    )

    parser.add_argument(
        '--show-seam',
        action='store_true',
        help='额外输出一张缝合线标注图（红色标记）'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细输出'
    )

    args = parser.parse_args()

    if len(args.images) < 2:
        parser.error('至少需要两张图像进行拼接')

    for img_path in args.images:
        if not os.path.exists(img_path):
            parser.error(f'图像文件不存在: {img_path}')

    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    setup_logger('stitcher', 'DEBUG' if args.verbose else 'INFO')

    print(f"开始按顺序拼接 {len(args.images)} 张图像...")

    pipeline = StitchingPipeline()
    pipeline.update_config({
        'SEAM_BAND': args.seam_band,
        'FEATHER_RADIUS': args.feather_radius
    })
    pipeline.load_images(args.images)

    result = pipeline.run(output_path=args.output)

    if result is not False:
        print(f"拼接完成！结果已保存至: {args.output}")

        if args.show_seam and pipeline.seam_mask is not None:
            output_path = Path(args.output)
            seam_path = str(output_path.with_stem(output_path.stem + "_seam"))
            seam_overlay = StitchingPipeline.overlay_seam(
                pipeline.result_image, pipeline.seam_mask,
                color=(0, 0, 255), dilate_radius=2
            )
            cv_imwrite(seam_path, seam_overlay)
            print(f"缝合线标注已保存至: {seam_path}")

        return 0
    else:
        print("拼接失败！")
        return 1


if __name__ == '__main__':
    sys.exit(main())
