import cv2
import numpy as np
import os
import random
from PIL import Image

class DataAugmentor:
    def __init__(self, output_dir="uploads/augmented"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def rotate_image(self, image, angle_range=(-5, 5)):
        angle = random.uniform(*angle_range)
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    def add_noise(self, image):
        # Gaussian Noise
        row, col, ch = image.shape
        mean = 0
        var = 10
        sigma = var**0.5
        gauss = np.random.normal(mean, sigma, (row, col, ch))
        gauss = gauss.reshape(row, col, ch)
        noisy = image + gauss
        return np.clip(noisy, 0, 255).astype(np.uint8)

    def adjust_contrast_brightness(self, image, alpha=1.2, beta=10):
        # alpha: contrast control (1.0-3.0), beta: brightness control (0-100)
        adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        return adjusted

    def augment_file(self, file_path, num_variants=5):
        image = cv2.imread(file_path)
        if image is None:
            print(f"Error: Could not read image {file_path}")
            return

        base_name = os.path.basename(file_path).split('.')[0]
        
        for i in range(num_variants):
            aug_img = image.copy()
            
            # Randomly apply transformations
            if random.random() > 0.5:
                aug_img = self.rotate_image(aug_img)
            
            if random.random() > 0.5:
                aug_img = self.add_noise(aug_img)
                
            if random.random() > 0.5:
                alpha = random.uniform(0.8, 1.3)
                beta = random.randint(-20, 20)
                aug_img = self.adjust_contrast_brightness(aug_img, alpha, beta)

            output_path = os.path.join(self.output_dir, f"{base_name}_aug_{i}.jpg")
            cv2.imwrite(output_path, aug_img)
            print(f"Saved: {output_path}")

if __name__ == "__main__":
    augmentor = DataAugmentor()
    # Example usage:
    # augmentor.augment_file("images/sample_invoice.jpg")
    print("Data Augmentor initialized. Use augment_file(path) to generate variants.")
