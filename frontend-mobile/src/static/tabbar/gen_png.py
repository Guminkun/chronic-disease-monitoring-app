"""
Generate tabbar PNG icons from SVG path data.
Pure Python, no third-party dependencies.
"""
import struct, zlib, math, os

SIZE = 81  # output PNG size

def write_png(path, pixels):
    """pixels: list of SIZE rows, each row is list of (r,g,b,a) tuples"""
    def chunk(tag, data):
        c = tag + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', SIZE, SIZE, 8, 6, 0, 0, 0))  # RGBA
    raw = b''
    for row in pixels:
        raw += b'\x00'
        for r, g, b, a in row:
            raw += bytes([r, g, b, a])
    idat = chunk(b'IDAT', zlib.compress(raw, 9))
    iend = chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(sig + ihdr + idat + iend)

def empty_pixels():
    return [[(0, 0, 0, 0)] * SIZE for _ in range(SIZE)]

def fill_pixel(pixels, x, y, color):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        pixels[y][x] = color

def draw_circle_filled(pixels, cx, cy, r, color):
    for y in range(int(cy - r) - 1, int(cy + r) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            if dist <= r:
                fill_pixel(pixels, x, y, color)
            elif dist <= r + 1:
                alpha = int((r + 1 - dist) * color[3])
                fill_pixel(pixels, x, y, (color[0], color[1], color[2], alpha))

def draw_rect(pixels, x1, y1, x2, y2, color):
    for y in range(int(y1), int(y2) + 1):
        for x in range(int(x1), int(x2) + 1):
            fill_pixel(pixels, x, y, color)

def draw_polygon(pixels, points, color):
    """Fill a polygon using scanline algorithm"""
    if not points:
        return
    min_y = int(min(p[1] for p in points))
    max_y = int(max(p[1] for p in points))
    for y in range(min_y, max_y + 1):
        intersections = []
        n = len(points)
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            if y1 == y2:
                continue
            if min(y1, y2) <= y <= max(y1, y2):
                x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                intersections.append(x)
        intersections.sort()
        for i in range(0, len(intersections) - 1, 2):
            for x in range(int(intersections[i]), int(intersections[i+1]) + 1):
                fill_pixel(pixels, x, y, color)

# Scale factor: SVG viewBox is 0-24, output is SIZE px
S = SIZE / 24.0

def sc(v):
    """scale coordinate"""
    return v * S

def make_home(color):
    """Home icon path"""
    px = empty_pixels()
    c = color
    # Outer house shape: M12 3L2 12H5V20H11V14H13V20H19V12H22L12 3Z
    house = [
        (sc(12), sc(3)),
        (sc(2),  sc(12)),
        (sc(5),  sc(12)),
        (sc(5),  sc(20)),
        (sc(11), sc(20)),
        (sc(11), sc(14)),
        (sc(13), sc(14)),
        (sc(13), sc(20)),
        (sc(19), sc(20)),
        (sc(19), sc(12)),
        (sc(22), sc(12)),
    ]
    draw_polygon(px, house, c)
    return px

def make_home_outline(color):
    """Home outline icon"""
    px = empty_pixels()
    c = color
    # Outer: M12 3L2 12H5V20H11V14H13V20H19V12H22L12 3Z
    outer = [
        (sc(12), sc(3)),
        (sc(2),  sc(12)),
        (sc(5),  sc(12)),
        (sc(5),  sc(20)),
        (sc(11), sc(20)),
        (sc(11), sc(14)),
        (sc(13), sc(14)),
        (sc(13), sc(20)),
        (sc(19), sc(20)),
        (sc(19), sc(12)),
        (sc(22), sc(12)),
    ]
    draw_polygon(px, outer, c)
    # Inner cutout (roof triangle area) - draw inner walls lighter
    # Inner path: M12 5.69L17 10.19V18H15V12H9V18H7V10.19L12 5.69Z
    inner = [
        (sc(12), sc(5.69)),
        (sc(17), sc(10.19)),
        (sc(17), sc(18)),
        (sc(15), sc(18)),
        (sc(15), sc(12)),
        (sc(9),  sc(12)),
        (sc(9),  sc(18)),
        (sc(7),  sc(18)),
        (sc(7),  sc(10.19)),
    ]
    draw_polygon(px, inner, c)
    return px

def make_todo(color):
    """Calendar/todo icon - filled"""
    px = empty_pixels()
    c = color
    # Calendar body: M19 3H18V1H16V3H8V1H6V3H5C3.89 3 3 3.9 3 5V19C3 20.1 3.89 21 5 21H19C20.11 21 21 20.1 21 19V5C21 3.9 20.11 3 19 3Z
    # Simplified as rectangle with rounded feel
    draw_rect(px, sc(3), sc(3), sc(21), sc(21), c)
    # White header area
    white = (255, 255, 255, 255)
    draw_rect(px, sc(3), sc(3), sc(21), sc(7), white)
    # Plus sign: M14 14V17H10V14H7V12H10V9H13V12H17V14H14Z
    plus = [
        (sc(14), sc(14)),
        (sc(14), sc(17)),
        (sc(10), sc(17)),
        (sc(10), sc(14)),
        (sc(7),  sc(14)),
        (sc(7),  sc(12)),
        (sc(10), sc(12)),
        (sc(10), sc(9)),
        (sc(13), sc(9)),
        (sc(13), sc(12)),
        (sc(17), sc(12)),
        (sc(17), sc(14)),
    ]
    draw_polygon(px, plus, white)
    # Ring handles
    draw_rect(px, sc(7.5), sc(1), sc(8.5), sc(4), c)
    draw_rect(px, sc(15.5), sc(1), sc(16.5), sc(4), c)
    return px

def make_profile(color):
    """Profile/person icon"""
    px = empty_pixels()
    c = color
    # Head circle: center (12,8), r=3
    draw_circle_filled(px, sc(12), sc(8), sc(3), c)
    # Body: lower half circle approximation
    body = []
    cx, cy, r = sc(12), sc(15.98), sc(6)
    for angle in range(0, 181):
        rad = math.radians(angle)
        x = cx + r * math.cos(math.radians(180 - angle))
        y = cy - r * math.sin(rad)
        body.append((x, y))
    body.append((sc(18), sc(15.98)))
    body.append((sc(6), sc(15.98)))
    draw_polygon(px, body, c)
    # Outer circle border
    for angle in range(0, 360):
        rad = math.radians(angle)
        for dr in [sc(10) - 1, sc(10)]:
            x = int(sc(12) + dr * math.cos(rad))
            y = int(sc(12) + dr * math.sin(rad))
            fill_pixel(px, x, y, c)
    # Fill outer circle
    draw_circle_filled(px, sc(12), sc(12), sc(10), c)
    # Punch out inner (white)
    white = (255, 255, 255, 255)
    draw_circle_filled(px, sc(12), sc(8), sc(3), c)
    # Redo body on top of circle
    body2 = [
        (sc(6),  sc(19.2)),
        (sc(6),  sc(15.98)),
        (sc(18), sc(15.98)),
        (sc(18), sc(19.2)),
    ]
    # Use the actual SVG shape
    return px

def make_profile_v2(color):
    """Profile icon - circle with person silhouette"""
    px = empty_pixels()
    c = color
    # Full circle background
    draw_circle_filled(px, sc(12), sc(12), sc(10), c)
    # Punch out with white for person shape
    white = (255, 255, 255, 255)
    # Head
    draw_circle_filled(px, sc(12), sc(8), sc(3), white)
    # Body lower area
    body = []
    for angle in range(0, 181):
        rad = math.radians(angle)
        x = sc(12) + sc(6) * math.cos(math.radians(180 - angle))
        y = sc(15.98) - sc(6) * math.sin(rad)
        body.append((x, y))
    body.append((sc(18), sc(15.98)))
    body.append((sc(6),  sc(15.98)))
    draw_polygon(px, body, white)
    return px

def make_profile_solid(color):
    """Profile icon matching SVG exactly"""
    px = empty_pixels()
    c = color
    # Outer circle
    draw_circle_filled(px, sc(12), sc(12), sc(10), c)
    # Head circle (same color - it's a solid icon)
    # Body shape
    # The SVG is a single path that draws the whole silhouette
    # Approximate: circle + head bump + body
    return px

def make_medication(color):
    """Pill / capsule icon"""
    px = empty_pixels()
    c = color
    cx, cy = int(sc(12)), int(sc(12))
    # Left circle (top-left of pill)
    draw_circle_filled(px, cx - int(sc(4)), cy - int(sc(2)), int(sc(4)), c)
    # Right circle (bottom-right of pill)
    draw_circle_filled(px, cx + int(sc(4)), cy + int(sc(2)), int(sc(4)), c)
    # Connecting body
    for dx in range(-int(sc(7)), int(sc(7))+1):
        for dy in range(-int(sc(3)), int(sc(3))+1):
            rx = dx * 0.87 - dy * 0.5
            ry = dx * 0.5  + dy * 0.87
            if abs(rx) <= sc(5.5) and abs(ry) <= sc(3):
                fill_pixel(px, cx + dx, cy + dy, c)
    # Draw a white dividing line across pill center
    white = (255, 255, 255, 255)
    for t in range(-int(sc(5)), int(sc(5))+1):
        lx = cx + int(t * 0.5)
        ly = cy - int(t * 0.87)
        fill_pixel(px, lx, ly, white)
        fill_pixel(px, lx+1, ly, white)
    return px

def make_monitor_icon(color):
    """Heart with ECG waveform icon"""
    px = empty_pixels()
    c = color
    cx, cy = int(sc(12)), int(sc(11))
    def draw_heart(px, cx, cy, size, col):
        for angle in range(0, 360):
            t = math.radians(angle)
            hx = 16 * (math.sin(t) ** 3)
            hy = -(13*math.cos(t) - 5*math.cos(2*t) - 2*math.cos(3*t) - math.cos(4*t))
            px_x = int(cx + hx * size / 16)
            px_y = int(cy + hy * size / 16)
            fill_pixel(px, px_x, px_y, col)
    draw_heart(px, cx, cy, int(sc(8)), c)
    for y in range(SIZE):
        start_x = -1
        last_x = -1
        for x in range(SIZE):
            if px[y][x][3] > 0:
                if start_x < 0:
                    start_x = x
                last_x = x
        if start_x >= 0:
            for x in range(start_x, last_x+1):
                fill_pixel(px, x, y, c)
    wh = (255, 255, 255, 200)
    pts = [
        (int(sc(5)), int(sc(11))), (int(sc(7)), int(sc(11))),
        (int(sc(8)), int(sc(8))),  (int(sc(9)), int(sc(14))),
        (int(sc(10.5)), int(sc(7))), (int(sc(12)), int(sc(15))),
        (int(sc(13.5)), int(sc(11))), (int(sc(19)), int(sc(11)))
    ]
    for i in range(len(pts)-1):
        x0,y0 = pts[i]; x1,y1 = pts[i+1]
        steps = max(abs(x1-x0), abs(y1-y0), 1)
        for s in range(steps+1):
            ix = int(x0 + (x1-x0)*s/steps)
            iy = int(y0 + (y1-y0)*s/steps)
            for th in [-1,0,1]:
                fill_pixel(px, ix, iy+th, wh)
    return px

# Generate all icons
base = os.path.dirname(os.path.abspath(__file__))

GRAY   = (148, 163, 184, 255)   # #94a3b8
BLUE   = (59,  130, 246, 255)   # #3b82f6
INDIGO = (99,  102, 241, 255)   # #6366f1

icons = [
    ("home.png",              make_home_outline(GRAY)),
    ("home-active.png",       make_home(INDIGO)),
    ("todo.png",              make_todo(GRAY)),
    ("todo-active.png",       make_todo(INDIGO)),
    ("profile.png",           make_profile_v2(GRAY)),
    ("profile-active.png",    make_profile_v2(INDIGO)),
    ("medication.png",        make_medication(GRAY)),
    ("medication-active.png", make_medication(INDIGO)),
    ("monitor.png",           make_monitor_icon(GRAY)),
    ("monitor-active.png",    make_monitor_icon(INDIGO)),
]

for name, pixels in icons:
    path = os.path.join(base, name)
    write_png(path, pixels)
    print(f"Generated: {name}")

print("Done!")
