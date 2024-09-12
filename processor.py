import numpy as np
from PIL import Image
from pytriton.client import AsyncioModelClient
from io import BytesIO
from dotenv import load_dotenv
import os
import random

# Load environment variables
load_dotenv()


class ImageProcessor:
    def __init__(self, model_name: str) -> None:
        """
        Initialize the ImageProcessor with the Triton server address and model name.
        """
        self._address = os.getenv(
            'TRITON_SERVER_ADDRESS') + ':' + os.getenv('TRITON_SERVER_PORT')
        self._model_name = model_name

    def preprocess_image(self, image: bytes) -> np.ndarray:
        """
        Converts a Telegram image byte array into a NumPy array with three channels (RGB) and keeps the original size.

        Args:
            image (bytes): Byte data of the image.

        Returns:
            np.ndarray: The image as a NumPy array with shape (height, width, 3).
        """
        img = Image.open(BytesIO(image)).convert("RGB")

        # Convert the PIL image to a NumPy array with shape (height, width, channels)
        img_array = np.array(img)

        print(img_array.shape)

        # Transpose the array to get (channels, height, width)
        img_array = img_array.transpose(2, 0, 1)

        return img_array

    def create_image_dict(self, processed_images):
        image_names = ['bottom_image', *
                       [f"side_{i}_image" for i in range(1, 5)]]
        return {name: image for image, name in zip(processed_images, image_names)}

    async def process(self, images: list) -> np.ndarray:
        """
        Sends the preprocessed images to the Triton server for inference.

        Args:
            images (list): A list of byte arrays representing the images to be processed.

        Returns:
            np.ndarray: The prediction from the model for each image.
        """
        # Preprocess each image
        preprocessed_images = [self.preprocess_image(img) for img in images]
        print(len(preprocessed_images), [
              image.shape for image in preprocessed_images])

        image_dict = self.create_image_dict(preprocessed_images)

        # Initialize Triton client
        triton_client = AsyncioModelClient(
            self._address, self._model_name, init_timeout_s=15)

        # Send the batch of images to the Triton server
        result_dict = await triton_client.infer_sample(**image_dict)

        # Close the client
        await triton_client.close()

        # return result
        return (bool(result_dict['boolean_output']), float(result_dict['probability_output']))
