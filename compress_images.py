from PIL import Image
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def compress_image(filename, input_folder, output_folder, quality):
    img_path = os.path.join(input_folder, filename)

    original_size = os.path.getsize(img_path)

    img = Image.open(img_path)

    # 如果图像有 alpha 通道，则转换为 RGB
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        img = img.convert('RGB')

    compressed_path = os.path.join(output_folder, filename)

    # 使用指定的质量保存图像
    img.save(compressed_path, format='JPEG', optimize=True, quality=quality)

    compressed_size = os.path.getsize(compressed_path)
    return original_size, compressed_size

def compress_images(input_folder, output_folder, quality=85):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    total_original_size = 0
    total_compressed_size = 0

    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(compress_image, filename, input_folder, output_folder, quality): filename for filename in image_files}

        for future in as_completed(futures):
            original_size, compressed_size = future.result()
            total_original_size += original_size
            total_compressed_size += compressed_size
            filename = futures[future]
            print(f"{filename}: 原始大小: {format_size(original_size)}, 压缩后大小: {format_size(compressed_size)}")

    print("\n总计:")
    print(f"原始总大小: {format_size(total_original_size)}")
    print(f"压缩后总大小: {format_size(total_compressed_size)}")

while True:
    try:
        quality_input = int(input("请输入保存原照片质量的百分制（0-100）："))
        if 0 <= quality_input <= 100:
            break
        else:
            print("请确保输入的质量在0到100之间。")
    except ValueError:
        print("无效输入，请输入一个整数。")

input_folder = 'img'
output_folder = 'compressed'
compress_images(input_folder, output_folder, quality=quality_input)
