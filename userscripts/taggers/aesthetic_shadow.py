# This code is using the image classification "aesthetic-shadow-v2" by shadowlilac (https://huggingface.co/shadowlilac/aesthetic-shadow-v2)
# and "aesthetic-shadow-v2" is licensed under CC-BY-NC 4.0 (https://spdx.org/licenses/CC-BY-NC-4.0)

import math

from PIL import Image
from transformers import pipeline
import torch

from modules import devices, shared
from scripts.tagger import Tagger

# brought and modified from https://huggingface.co/spaces/cafeai/cafe_aesthetic_demo/blob/main/app.py

# I'm not sure if this is really working
BATCH_SIZE = 3

class AestheticShadowV2(Tagger):
    def load(self):
        if devices.device.index is None:
            dev = torch.device(devices.device.type, 0)
        else:
            dev = devices.device
        self.pipe_aesthetic = pipeline("image-classification", "shadowlilac/aesthetic-shadow-v2", device=dev, batch_size=BATCH_SIZE)
    
    def unload(self):
        if not shared.opts.interrogate_keep_models_in_memory:
            self.pipe_aesthetic = None
            devices.torch_gc()

    def start(self):
        self.load()
        return self

    def stop(self):
        self.unload()

    def _get_score(self, data):
        final = {}
        for d in data:
            final[d["label"]] = d["score"]
        hq = final['hq']
        lq = final['lq']
        return [f"score_{math.floor((hq + (1 - lq))/2 * 10)}"]

    def predict(self, image: Image.Image, threshold=None):
        data = self.pipe_aesthetic(image)
        return self._get_score(data)
    
    def predict_pipe(self, data: list[Image.Image], threshold=None):
        if data is None:
            return
        for out in self.pipe_aesthetic(data, batch_size=BATCH_SIZE):
            yield self._get_score(out)

    def name(self):
        return "aesthetic shadow"