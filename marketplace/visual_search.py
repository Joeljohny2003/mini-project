import imagehash
import numpy as np
from PIL import Image
import os

MIN_SCORE = 65


def compute_phash(img, hash_size=16):
    """Compute perceptual hash of a PIL Image (RGB)."""
    return imagehash.phash(img, hash_size=hash_size)


def compute_color_histogram(img):
    """Compute a normalised HSV colour histogram (90-bin) from a PIL Image."""
    hsv = img.convert("HSV").resize((128, 128))
    arr = np.array(hsv)

    h_hist, _ = np.histogram(arr[:, :, 0], bins=30, range=(0, 256), density=True)
    s_hist, _ = np.histogram(arr[:, :, 1], bins=30, range=(0, 256), density=True)
    v_hist, _ = np.histogram(arr[:, :, 2], bins=30, range=(0, 256), density=True)

    hist = np.concatenate([h_hist, s_hist, v_hist])
    norm = np.linalg.norm(hist)
    return hist / norm if norm > 0 else hist


def histogram_similarity(hist_a, hist_b):
    """Cosine similarity between two normalised histograms."""
    dot = np.dot(hist_a, hist_b)
    return float(np.clip(dot, 0.0, 1.0))


def find_similar_products(uploaded_image_file, top_n=8):
    """
    Compare uploaded image against every Product that has an image.
    Returns a list of dicts: {product, hash_score, color_score, score}.
    Only products scoring >= MIN_SCORE are returned.
    """
    from .models import Product

    uploaded_image_file.seek(0)
    uploaded_img = Image.open(uploaded_image_file).convert("RGB")
    uploaded_hash = compute_phash(uploaded_img)
    uploaded_hist = compute_color_histogram(uploaded_img)

    candidates = Product.objects.filter(
        image__isnull=False
    ).exclude(image="")

    results = []
    for product in candidates:
        try:
            img_path = product.image.path
            if not os.path.isfile(img_path):
                continue
            prod_img = Image.open(img_path).convert("RGB")
        except Exception:
            continue

        prod_hash = compute_phash(prod_img)
        hamming = uploaded_hash - prod_hash
        hash_score = 1.0 - (hamming / 256.0)

        prod_hist = compute_color_histogram(prod_img)
        color_score = histogram_similarity(uploaded_hist, prod_hist)

        combined = 0.9 * hash_score + 0.1 * color_score
        score = round(combined * 100, 1)

        if score >= MIN_SCORE:
            results.append({
                "product": product,
                "hash_score": round(hash_score * 100, 1),
                "color_score": round(color_score * 100, 1),
                "score": score,
            })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_n]
