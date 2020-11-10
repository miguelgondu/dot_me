import click
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree

def get_background(img):
    """
    Returns a white background
    """
    background = (255 * np.ones(img.shape)).astype(int)

    return background

def compute_random_dots(img, random_dots):
    h, w, _ = img.shape
    i_s = np.random.randint(0, h, size=random_dots)
    j_s = np.random.randint(0, w, size=random_dots)
    dots = list(zip(i_s, j_s))
    
    return dots

def plot_dot(img, dot, radius, color):
    lower_i = max(0, dot[0] - radius)
    upper_i = min(img.shape[0], dot[0] + radius)
    lower_j = max(0, dot[1] - radius)
    upper_j = min(img.shape[1], dot[1] + radius)
    for i in range(lower_i, upper_i):
        for j in range(lower_j, upper_j):
            if np.sqrt((i - dot[0]) ** 2 + (j - dot[1]) ** 2) < radius:
                img[i, j, :] = color

def compute_radius(dots):
    tree = cKDTree(dots)
    radius_d = {
        d: max(tree.query(d, k=2)[0][1], 3) for d in dots
    }

    return radius_d

def compute_circle(img, dot, radius):
    """
    Computes the indices to be painted and
    the mean color of them.
    """
    lower_i = int(max(0, dot[0] - radius))
    upper_i = int(min(img.shape[0], dot[0] + radius))
    lower_j = int(max(0, dot[1] - radius))
    upper_j = int(min(img.shape[1], dot[1] + radius))
    colors = []
    circle = []
    for i in range(lower_i, upper_i):
        for j in range(lower_j, upper_j):
            if np.sqrt((i - dot[0]) ** 2 + (j - dot[1]) ** 2) < radius:
                circle.append([i, j])
                colors.append([
                    img[i, j, 0],
                    img[i, j, 1],
                    img[i, j, 2]
                ])
    
    colors = np.array(colors)
    if len(colors) > 1:
        mean_color = np.array([
            np.mean(colors[:, 0]),
            np.mean(colors[:, 1]),
            np.mean(colors[:, 2]),
        ]).astype(int)
    else:
        mean_color = colors[0].astype(int)

    return circle, mean_color

@click.command()
@click.argument("path", type=str)
@click.option("--n-dots", type=int, default=1500)
@click.option("--out", type=str, default="./out.jpg")
def dot_me(path, n_dots, out):
    img = Image.open(path)
    img = np.asarray(img).copy()
    dots = compute_random_dots(img, n_dots)
    canvas = get_background(img)

    radius_d = compute_radius(dots)
    for dot, r in radius_d.items():
        try:
            circle, color = compute_circle(img, dot, r)
            for point in circle:
                i, j = point
                canvas[i, j, :] = color
        except IndexError:
            pass
    
    im = Image.fromarray(np.uint8(canvas))
    im.save(out, quality=100, subsampling=0)

if __name__ == "__main__":
    dot_me()
