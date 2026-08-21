import os
from typing import Dict, Any
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for headless file generation
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set up Korean font for Windows matplotlib
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def visualize_color_palette(color_palette_data: Dict[str, Any], output_path: str) -> str:
    """
    Renders a visual color palette swatch graphic using matplotlib and saves it as a PNG file.
    """
    main_color = color_palette_data.get("main", {"hex": "#2E7D32", "name": "Main Color", "description": ""})
    sub_colors = color_palette_data.get("sub", [])

    all_colors = [
        {
            "role": "MAIN COLOR",
            "hex": main_color.get("hex", "#2E7D32"),
            "name": main_color.get("name", "Main Color"),
            "desc": main_color.get("description", "")
        }
    ]

    for idx, sub in enumerate(sub_colors, 1):
        all_colors.append({
            "role": f"SUB COLOR {idx}",
            "hex": sub.get("hex", "#81C784"),
            "name": sub.get("name", f"Sub Color {idx}"),
            "desc": sub.get("description", "")
        })

    num_colors = len(all_colors)

    # Figure dimensions
    fig, ax = plt.subplots(figsize=(10, 2.5 + num_colors * 1.2), dpi=150)
    fig.patch.set_facecolor('#FAFAFA')
    ax.set_facecolor('#FAFAFA')
    ax.axis('off')

    # Title header
    ax.text(0.5, 0.95, "BRAND COLOR PALETTE", fontsize=18, fontweight='bold',
            ha='center', va='top', transform=ax.transAxes, color='#1A1A1A')

    # Draw swatches
    box_height = 0.75 / num_colors
    start_y = 0.85

    for idx, color_info in enumerate(all_colors):
        y_pos = start_y - (idx * (box_height + 0.04))
        hex_code = color_info["hex"]

        # Color Box Swatch
        rect = patches.FancyBboxPatch(
            (0.08, y_pos - box_height + 0.02), 0.25, box_height - 0.02,
            boxstyle="round,pad=0.01,rounding_size=0.02",
            linewidth=1, edgecolor="#E0E0E0", facecolor=hex_code,
            transform=ax.transAxes
        )
        ax.add_patch(rect)

        # Role & Name
        ax.text(0.36, y_pos - 0.02, f"[{color_info['role']}] {color_info['name']}",
                fontsize=13, fontweight='bold', ha='left', va='top',
                transform=ax.transAxes, color='#222222')

        # HEX Code
        ax.text(0.36, y_pos - 0.07, f"HEX: {hex_code}",
                fontsize=11, fontweight='bold', ha='left', va='top',
                transform=ax.transAxes, color='#555555')

        # Description
        desc_text = color_info['desc']
        if len(desc_text) > 45:
            desc_text = desc_text[:45] + "..."
        ax.text(0.36, y_pos - 0.11, desc_text,
                fontsize=9.5, ha='left', va='top',
                transform=ax.transAxes, color='#777777')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight', facecolor=fig.get_facecolor(), pad_inches=0.4)
    plt.close(fig)

    return output_path
