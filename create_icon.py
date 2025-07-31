from PIL import Image, ImageDraw

# 创建32x32的图标
img = Image.new('RGB', (32, 32), color=(73, 109, 137))
d = ImageDraw.Draw(img)

# 绘制一个简单的OCR图标
# 背景
d.rectangle([0, 0, 32, 32], fill=(73, 109, 137))

# 文档形状
d.rectangle([6, 4, 26, 28], fill=(255, 255, 255), outline=(0, 0, 0), width=1)
d.line([6, 8, 26, 8], fill=(0, 0, 0), width=1)

# 文字"O"
d.ellipse([10, 12, 22, 24], fill=(200, 50, 50), outline=(0, 0, 0), width=1)

# 保存为ICO文件
img.save('app_icon.ico', format='ICO')
print("已创建图标文件 app_icon.ico")