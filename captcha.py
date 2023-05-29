import os
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


def generate_arrays(df, resize=True, img_height=50, img_width=200):
    """Generates image array and labels array from a dataframe.

    Args:
        df: dataframe from which we want to read the data
        resize (bool)    : whether to resize images or not
        img_weidth (int): width of the resized images
        img_height (int): height of the resized images

    Returns:
        images (ndarray): grayscale images
        labels (ndarray): corresponding encoded labels
    """

    num_items = len(df)
    images = np.zeros((num_items, img_height, img_width), dtype=np.float32)
    labels = [0] * num_items

    for i in range(num_items):
        img = cv2.imread(df["img_path"][i])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if resize:
            img = cv2.resize(img, (img_width, img_height))

        img = (img / 255.).astype(np.float32)
        label = df["label"][i]

        # Add only if it is a valid captcha
        #if is_valid_captcha(label):
        images[i, :, :] = img
        labels[i] = label

    return images, np.array(labels)


class DataGenerator(keras.utils.Sequence):
    """Generates batches from a given dataset.

    Args:
        data: training or validation data
        labels: corresponding labels
        char_map: dictionary mapping char to labels
        batch_size: size of a single batch
        img_width: width of the resized
        img_height: height of the resized
        downsample_factor: by what factor did the CNN downsample the images
        max_length: maximum length of any captcha
        shuffle: whether to shuffle data or not after each epoch
    Returns:
        batch_inputs: a dictionary containing batch inputs
        batch_labels: a batch of corresponding labels
    """

    def __init__(self,
                 data,
                 labels,
                 char_map,
                 batch_size=16,
                 img_width=200,
                 img_height=50,
                 downsample_factor=4,
                 max_length=5,  # 글자 개수에 맞춰서 4개 or 5개
                 shuffle=True
                 ):
        self.data = data
        self.labels = labels
        self.char_map = char_map
        self.batch_size = batch_size
        self.img_width = img_width
        self.img_height = img_height
        self.downsample_factor = downsample_factor
        self.max_length = max_length
        self.shuffle = shuffle
        self.indices = np.arange(len(data))
        self.on_epoch_end()

    def __len__(self):
        return int(np.ceil(len(self.data) / self.batch_size))

    def __getitem__(self, idx):
        # 1. Get the next batch indices
        curr_batch_idx = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]

        # 2. This isn't necessary but it can help us save some memory
        # as not all batches the last batch may not have elements
        # equal to the batch_size
        batch_len = len(curr_batch_idx)

        # 3. Instantiate batch arrays
        batch_images = np.ones((batch_len, self.img_width, self.img_height, 1),
                               dtype=np.float32)
        batch_labels = np.ones((batch_len, self.max_length), dtype=np.float32)
        input_length = np.ones((batch_len, 1), dtype=np.int64) * \
                       (self.img_width // self.downsample_factor - 2)
        label_length = np.zeros((batch_len, 1), dtype=np.int64)

        for j, idx in enumerate(curr_batch_idx):
            # 1. Get the image and transpose it
            img = self.data[idx].T
            # 2. Add extra dimenison
            img = np.expand_dims(img, axis=-1)
            # 3. Get the correpsonding label
            text = self.labels[idx]
            # 4. Include the pair only if the captcha is valid
            #if is_valid_captcha(text):
            label = [self.char_map[ch] for ch in text]
            batch_images[j] = img
            batch_labels[j] = label
            label_length[j] = len(text)

        batch_inputs = {
            'input_data': batch_images,
            'input_label': batch_labels,
            'input_length': input_length,
            'label_length': label_length,
        }
        return batch_inputs, np.zeros(batch_len).astype(np.float32)

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indices)


class CTCLayer(layers.Layer):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.loss_fn = keras.backend.ctc_batch_cost

    def call(self, y_true, y_pred, input_length, label_length):
        # Compute the training-time loss value and add it
        # to the layer using `self.add_loss()`.
        loss = self.loss_fn(y_true, y_pred, input_length, label_length)
        self.add_loss(loss)

        # On test time, just return the computed loss
        return loss

'''
def build_model(opt, lr=0.001):
    # Inputs to the model
    input_img = layers.Input(shape=(img_width, img_height, 1),
                            name='input_data',
                            dtype='float32')
    labels = layers.Input(name='input_label', shape=[max_length], dtype='float32')
    input_length = layers.Input(name='input_length', shape=[1], dtype='int64')
    label_length = layers.Input(name='label_length', shape=[1], dtype='int64')
    
    # First conv block
    x = layers.Conv2D(32,
               (3,3),
               activation='relu',
               kernel_initializer='he_normal',
               padding='same',
               name='Conv1')(input_img)
    x = layers.MaxPooling2D((2,2), name='pool1')(x)
    
    # Second conv block
    x = layers.Conv2D(64,
               (3,3),
               activation='relu',
               kernel_initializer='he_normal',
               padding='same',
               name='Conv2')(x)
    x = layers.MaxPooling2D((2,2), name='pool2')(x)
    
    # We have used two max pool with pool size and strides of 2.
    # Hence, downsampled feature maps are 4x smaller. The number of
    # filters in the last layer is 64. Reshape accordingly before
    # passing it to RNNs
    new_shape = ((img_width // 4), (img_height // 4)*64)
    x = layers.Reshape(target_shape=new_shape, name='reshape')(x)
    x = layers.Dense(64, activation='relu', name='dense1')(x)
    x = layers.Dropout(0.2)(x)
    
    # RNNs
    x = layers.Bidirectional(layers.LSTM(128,
                                         return_sequences=True,
                                         dropout=0.2))(x)
    x = layers.Bidirectional(layers.LSTM(64,
                                         return_sequences=True,
                                         dropout=0.25))(x)
    
    # Predictions
    x = layers.Dense(len(characters)+1,
              activation='softmax', 
              name='dense2',
              kernel_initializer='he_normal')(x)
    
    # Calculate CTC
    output = CTCLayer(name='ctc_loss')(labels, x, input_length, label_length)
    
    # Define the model
    model = keras.models.Model(inputs=[input_img,
                                       labels,
                                       input_length,
                                       label_length],
                                outputs=output,
                                name='ocr_model_v1')
    
    # Optimizer
    sgd = keras.optimizers.legacy.SGD(learning_rate=lr,
                               decay=1e-6,
                               momentum=0.9,
                               nesterov=True,
                               clipnorm=5)
    
    Adam = tf.keras.optimizers.Adam(
        learning_rate=lr,
        beta_1=0.9,
        beta_2=0.999,
        epsilon=1e-07,
        amsgrad=False,
        weight_decay=None,
        clipnorm=None,
        clipvalue=None,
        global_clipnorm=None,
        use_ema=False,
        ema_momentum=0.99,
        ema_overwrite_frequency=None,
        jit_compile=True)

    if opt=='SGD':
      opt=sgd

    if opt=='Adam':
      opt=Adam  
      
    # Compile the model and return
    model.compile(optimizer=opt, metrics=['accuracy'])
    return model
'''

# test 이미지가 저장된 디렉토리 주소 입력
test_data_dir = Path("C:\\Users\\choo0\\Downloads\\")
images = list(test_data_dir.glob("*.png"))
images += list(test_data_dir.glob("*.jpg"))
print("Number of images found: ", len(images))

  # Store all the characters in a set
characters = set()

  # A list to store the length of each captcha
captcha_length = []

  # Store image-label info
dataset = []

  # Iterate over the dataset and store the
  # information needed
for img_path in images:
  # 1. Get the label associated with each image
  if str(img_path)[-3:] == 'png':
    label = img_path.name.split(".png")[0]
  else:
    label = img_path.name.split(".jpg")[0]
  # 2. Store the length of this cpatcha
  captcha_length.append(len(label))
  # 3. Store the image-label pair info
  dataset.append((str(img_path), label))
  # 4. Store the characters present
  for ch in label:
    characters.add(ch)

  # Sort the characters
characters = sorted(characters)

  # Convert the dataset info into a dataframe
dataset = pd.DataFrame(dataset, columns=["img_path", "label"], index=None)

  # Shuffle the dataset
dataset = dataset.sample(frac=1.).reset_index(drop=True)

  # Build test data
test_data, test_labels = generate_arrays(df=dataset)
print("Number of test images: ", test_data.shape)
print("Number of test labels: ", test_labels.shape)

  # Map text to numeric labels
char_to_labels = {char:idx for idx, char in enumerate(characters)}

  # Map numeric labels to text
labels_to_char = {val:key for key, val in char_to_labels.items()}

  # Batch size for training and validation
batch_size = 32

  # Desired image dimensions
img_width=200
img_height=50

  # Factor  by which the image is going to be downsampled
  # by the convolutional blocks
downsample_factor=4

  # Maximum length of any captcha in the data
  # 글자 개수에 맞춰서 4개 or 5개
max_length=5

  # Get a generator object for the validation data
test_data_generator = DataGenerator(data=test_data,
                                      labels=test_labels,
                                      char_map=char_to_labels,
                                      batch_size=batch_size,
                                      img_width=img_width,
                                      img_height=img_height,
                                      downsample_factor=downsample_factor,
                                      max_length=max_length,
                                      shuffle=False
                                      )

# 모델 로드
model_addr = '"C:\\Users\\choo0\\Documents\\Repository\\Captcha-Recognition-Chrome-Extension\\Chrome-Extension\\captcha_recognition_32000_model.h5"' # 모델 주소 입력
test_model = tf.keras.models.load_model(model_addr, custom_objects={"CTCLayer": CTCLayer})

prediction_model = keras.models.Model(test_model.get_layer(name='input_data').input,
                                      test_model.get_layer(name='dense2').output)


# A utility to decode the output of the network
def decode_batch_predictions(pred):
    pred = pred[:, :-2]
    input_len = np.ones(pred.shape[0]) * pred.shape[1]

    # Use greedy search. For complex tasks, you can use beam search
    results = keras.backend.ctc_decode(pred,
                                       input_length=input_len,
                                       greedy=True)[0][0]

    # Iterate over the results and get back the text
    output_text = []
    for res in results.numpy():
        outstr = ''
        for c in res:
            if c < len(characters) and c >= 0:
                outstr += labels_to_char[c]
        output_text.append(outstr)

    # return final text results
    return output_text


p_texts = []
o_texts = []

print('*'*20,'이미지에 대한 예측 결과 확인','*'*20)

#  Let's check results on some validation samples
for p, (inp_value, _) in enumerate(test_data_generator):
    bs = inp_value['input_data'].shape[0]
    X_data = inp_value['input_data']
    labels = inp_value['input_label']

    preds = prediction_model.predict(X_data)
    pred_texts = decode_batch_predictions(preds)

    orig_texts = []
    for label in labels:
        text = ''.join([labels_to_char[int(x)] for x in label])
        orig_texts.append(text)

    p_texts.append(pred_texts)
    o_texts.append(orig_texts)

    for i in range(bs):
        print(
            f'Ground truth: {orig_texts[i]} \t Predicted: {pred_texts[i]} \t Correct: {orig_texts[i] == pred_texts[i]}')
    break

