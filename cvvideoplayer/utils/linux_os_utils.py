from .video_player_utils import CURRENT_OS, SupportedOS

if CURRENT_OS == SupportedOS.LINUX:
    from PIL import Image
    import Xlib.display


def rgba_to_uint32(r, g, b, a):
    """Convert RGBA values to 32-bit unsigned integer in BGRA format"""
    return (a << 24) | (r << 16) | (g << 8) | b


def set_icon_linux(window_id, display, icon_path):
    try:
        # Get the window handle using Xlib
        # Load and prepare the icon
        icon = Image.open(icon_path)
        icon = icon.convert("RGBA")
        icon = icon.resize((32, 32))
        width, height = icon.size

        # Convert icon to X format
        icon_data = []
        icon_data.extend([width, height])

        for y in range(height):
            for x in range(width):
                r, g, b, a = icon.getpixel((x, y))
                icon_data.append(rgba_to_uint32(r, g, b, a))

        # Get the _NET_WM_ICON atom
        _NET_WM_ICON = display.intern_atom('_NET_WM_ICON')

        # Convert the list to a format Xlib can handle
        data = (height * width + 2) * [0]
        for i in range(len(icon_data)):
            data[i] = icon_data[i]

        # Set the property
        window = display.create_resource_object('window', window_id)
        window.change_property(_NET_WM_ICON, Xlib.Xatom.CARDINAL, 32, data)

        # Flush the changes
        display.flush()
        display.sync()
    except Exception:
        return
