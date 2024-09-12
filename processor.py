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

        # # Convert list of images to a batch of images (assume ResNet expects (N, H, W, 3))
        # batch_images = np.stack(preprocessed_images, axis=0)

        # # Initialize Triton client
        # triton_client = AsyncioModelClient(
        #     self._address, self._model_name, init_timeout_s=5)

        # # Send the batch of images to the Triton server
        # result_dict = await triton_client.infer_sample(batch_images)

        # # Close the client
        # await triton_client.close()

        # # Assuming the model returns a set of embeddings or class predictions
        # # Adjust this based on the model's output format
        # result = result_dict["output"]
        # return result
        return random.random() < 0.5
