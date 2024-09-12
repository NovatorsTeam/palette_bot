import os
import numpy as np
from PIL import Image
from pytriton.client import AsyncioModelClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ImageProcessor:
    def __init__(self, model_name: str) -> None:
        """
        Initialize the ImageProcessor with the Triton server address and model name.
        """
        self._address = f"{os.getenv('TRITON_SERVER_ADDRESS')}:{os.getenv('TRITON_SERVER_PORT')}"
        self._model_name = model_name

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Converts the input image into a NumPy array with three channels (RGB) and keeps the original size.
        
        Args:
            image_path (str): The path to the input image.
        
        Returns:
            np.ndarray: The image as a NumPy array with shape (height, width, 3).
        """
        with Image.open(image_path) as img:
            # Convert image to RGB and then to NumPy array
            img_rgb = img.convert("RGB")
            image_array = np.array(img_rgb)
        return image_array

    async def process(self, image_paths: list) -> np.ndarray:
        """
        Sends the preprocessed images to the Triton server for inference.

        Args:
            image_paths (list): A list of paths to the images to be processed.

        Returns:
            np.ndarray: The prediction from the model for each image.
        """
        # Convert images to numpy arrays
        preprocessed_images = [self.preprocess_image(image_path) for image_path in image_paths]

        # Convert list of images to a batch of images for Triton (assume ResNet expects (N, H, W, 3))
        batch_images = np.stack(preprocessed_images, axis=0)

        # Initialize Triton client
        triton_client = AsyncioModelClient(self._address, self._model_name, init_timeout_s=5)

        # Send the batch of images to the Triton server
        result_dict = await triton_client.infer_sample(batch_images)

        # Close the client
        await triton_client.close()

        # Assuming the model returns a set of embeddings or class predictions
        result = result_dict["output"]  # Adjust this based on the model's output format
        return result
