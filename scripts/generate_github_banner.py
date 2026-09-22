import os
from PIL import Image, ImageDraw, ImageFont

def generate_banner():
    # Dimensions
    width, height = 1200, 400
    
    # Create image with transparent background
    # We will use white text so it looks amazing on GitHub dark mode.
    # We can also generate a light mode one, but GitHub READMEs let you specify <picture> for light/dark!
    
    # Let's generate a dark-mode banner (white text, transparent bg)
    img_dark = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw_dark = ImageDraw.Draw(img_dark)
    
    # Load fonts
    font_dir = os.path.join("assets", "fonts")
    try:
        title_font = ImageFont.truetype(os.path.join(font_dir, "SpaceGrotesk-Bold.ttf"), 140)
        subtitle_font = ImageFont.truetype(os.path.join(font_dir, "SpaceGrotesk-Regular.ttf"), 36)
        accent_font = ImageFont.truetype(os.path.join(font_dir, "SpaceGrotesk-Bold.ttf"), 24)
    except IOError:
        print("Fonts not found! Please ensure SpaceGrotesk is in assets/fonts/")
        return

    # Draw Title (NEXUS)
    title = "NEXUS"
    title_bbox = draw_dark.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]
    title_x = (width - title_w) // 2
    title_y = (height - title_h) // 2 - 40
    
    # Draw title with a subtle blue drop shadow/glow for a cyber feel
    draw_dark.text((title_x + 4, title_y + 4), title, font=title_font, fill=(37, 99, 235, 100)) # blue shadow
    draw_dark.text((title_x, title_y), title, font=title_font, fill=(255, 255, 255, 255))

    # Draw Subtitle
    subtitle = "ADVANCED AUTONOMOUS CYBER WARFARE"
    sub_bbox = draw_dark.textbbox((0, 0), subtitle, font=subtitle_font)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_x = (width - sub_w) // 2
    sub_y = title_y + 160
    
    draw_dark.text((sub_x, sub_y), subtitle, font=subtitle_font, fill=(148, 163, 184, 255)) # slate-400

    # Draw a colored accent line under the subtitle
    line_y = sub_y + 60
    line_width = 400
    line_start = (width - line_width) // 2
    draw_dark.line([(line_start, line_y), (line_start + line_width, line_y)], fill=(56, 189, 248, 255), width=3)
    
    # Draw small tech tag
    tag = "AI-DRIVEN THREAT SIMULATION"
    tag_bbox = draw_dark.textbbox((0, 0), tag, font=accent_font)
    tag_w = tag_bbox[2] - tag_bbox[0]
    draw_dark.text(((width - tag_w) // 2, line_y + 20), tag, font=accent_font, fill=(56, 189, 248, 255))

    # Save Dark Mode Banner
    os.makedirs("assets/images", exist_ok=True)
    img_dark.save("assets/images/github_banner_dark.png")
    print("Generated github_banner_dark.png")

    # Now let's generate a Light Mode Banner (black text)
    img_light = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw_light = ImageDraw.Draw(img_light)
    
    draw_light.text((title_x + 3, title_y + 3), title, font=title_font, fill=(203, 213, 225, 150)) # light gray shadow
    draw_light.text((title_x, title_y), title, font=title_font, fill=(15, 23, 42, 255)) # slate-900

    draw_light.text((sub_x, sub_y), subtitle, font=subtitle_font, fill=(71, 85, 105, 255)) # slate-600
    draw_light.line([(line_start, line_y), (line_start + line_width, line_y)], fill=(37, 99, 235, 255), width=3)
    draw_light.text(((width - tag_w) // 2, line_y + 20), tag, font=accent_font, fill=(37, 99, 235, 255))

    img_light.save("assets/images/github_banner_light.png")
    print("Generated github_banner_light.png")

if __name__ == "__main__":
    generate_banner()
