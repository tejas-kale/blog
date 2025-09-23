---
title: "Logistic Regression with MLX"
date: "2025-09-23"
draft: false
---
The M1 MacBook Air, though not powerful, contains 8 CPU cores and 7-8 GPU cores. These processing units share a unified memory. In order to use the GPUs for training machine learning and deep learning models, one needs to use the [MLX](https://opensource.apple.com/projects/mlx/) framework. As quoted on the website:

> MLX is an array framework designed for efficient and flexible machine learning research on Apple silicon.

In this post, we will build a logistic regression model as a neural network using MLX. It will be trained on a [retinopathy](https://www.kaggle.com/datasets/mohamedabdalkader/retinal-disease-detection/data) dataset available on Kaggle. The code in this notebook is inspired from [lecture 8](https://www.youtube.com/watch?v=DzE0eSdy5Hk) of Jeremy Howard's course, Introduction to Machine Learning for Coders. 

The notebook that forms the basis of this post can be found [here](https://github.com/tejas-kale/blog/blob/main/notebooks/mlx_logistic_regression.ipynb). Since the MLX interface is similar to NumPy, its [quick start guide](https://ml-explore.github.io/mlx/build/html/usage/quick_start.html) is an excellent resource to get an introduction to the framework.

## Data
We’ll use the diabetic retinopathy training annotations (`annotations.csv`) and images under `data/diabetic_retinopathy/train/images/`.

```python
from pathlib import Path

import matplotlib.pyplot as plt
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
import pandas as pd
from PIL import Image

DATA_DIR = Path("data/diabetic_retinopathy")
df_annotations = pd.read_csv(DATA_DIR / "train" / "annotations.csv")
df_annotations.shape, df_annotations.head()
```

Using `matplotlib`, the images can be visualised although it is difficult for a non-expert to understand why an image is given a certain grade.


```python
image_idx = 0
image_name = df_annotations.iloc[image_idx]["Image name"]
image_grade = df_annotations.iloc[image_idx]["Retinopathy grade"]
image_path = DATA_DIR / "train" / "images" / image_name

# Load and display the image
img = Image.open(image_path)
plt.figure(figsize=(8, 6))
plt.imshow(img)
plt.title(f"Sample Image: {image_name}, Shape: {img.size}, Grade: {image_grade}")
plt.axis('off')
plt.show()
```
    
![Sample Image](../../mlx_logistic_regression_17_0.png)
    

## Data Preparation
To simplify, we frame the classification problem as Grade 0 vs. all other grades. Data preprocessing includes balancing the classes, stratifying the split, resizing images, flattening to vectors, and standardising using training statistics only.

Another normalisation approach is to scale pixel values by dividing by 255. However, when images are predominantly dark (as with the retinopathy set), most pixels end up very close to 0. With such tiny inputs, the linear scores z = X @ W + b are small and the gradients computed by SGD shrink accordingly leading to a slowdown in learning. A better default is to standardise using the training mean and standard deviation (optionally per channel), or rescale to [-1, 1], both of which keep features away from zero and yield healthier gradient magnitudes. See this [Claude conversation](https://gist.github.com/tejas-kale/175e2542b82ef6e7ac158d2bd983e227) for more context.

To speed up execution, we only pick 100 images from each binary class to train on.

```python
def load_and_preprocess_image(image_path, target_size=(96, 96)):
    """Load and resize image to target size."""
    img = Image.open(image_path)
    img = img.resize(target_size)
    return np.array(img, dtype=np.float32)


def sample_balanced_binary_data(df_annotations, samples_per_class=20, random_state=42):
    """Sample equal numbers for binary classification: grade 0 vs. all other grades."""
    # Create binary labels: 0 for grade 0, 1 for all other grades
    df_binary = df_annotations.copy()
    df_binary["Binary grade"] = (df_binary["Retinopathy grade"] > 0).astype(int)
    
    # Sample equal numbers from each binary class
    return df_binary.groupby("Binary grade", group_keys=False)[
        ["Image name", "Retinopathy grade", "Binary grade"]
    ].apply(
        lambda x: x.sample(n=min(samples_per_class, len(x)), random_state=random_state)
    ).reset_index(drop=True)


def stratified_train_val_split_binary(df_sampled, val_ratio=0.2):
    """Perform stratified train-validation split by binary grade."""
    train_data_list = []
    val_data_list = []
    
    for binary_grade in df_sampled["Binary grade"].unique():
        grade_data = df_sampled[df_sampled["Binary grade"] == binary_grade]
        val_size = max(1, int(len(grade_data) * val_ratio))
        train_size = len(grade_data) - val_size
        train_data_list.append(grade_data.iloc[:train_size])
        val_data_list.append(grade_data.iloc[train_size:])
    
    return pd.concat(train_data_list, ignore_index=True), pd.concat(val_data_list, ignore_index=True)


def load_images_from_dataframe_binary(df, data_dir, target_size=(96, 96)):
    """Load and preprocess images from dataframe for binary classification."""
    images = []
    labels = []
    
    for _, row in df.iterrows():
        image_path = data_dir / "train" / "images" / row["Image name"]
        if image_path.exists():
            img_array = load_and_preprocess_image(image_path, target_size)
            images.append(img_array.reshape(-1))
            labels.append(row["Binary grade"])  # Use binary grade instead of original grade
    
    return np.stack(images), np.array(labels)


def standardize_data(X_train, X_val):
    """Standardize data to mean=0, std=1 using training stats."""
    train_mean = np.mean(X_train)
    train_std = np.std(X_train)
    return (X_train - train_mean) / train_std, (X_val - train_mean) / train_std


def create_binary_dataset(df_annotations, data_dir, target_size=(96, 96), samples_per_class=20, val_ratio=0.2):
    """Create MLX arrays for binary classification with balanced sampling, split, and standardization."""
    df_sampled = sample_balanced_binary_data(df_annotations, samples_per_class)
    train_df, val_df = stratified_train_val_split_binary(df_sampled, val_ratio)
    X_train_raw, y_train = load_images_from_dataframe_binary(train_df, data_dir, target_size)
    X_val_raw, y_val = load_images_from_dataframe_binary(val_df, data_dir, target_size)
    X_train_std, X_val_std = standardize_data(X_train_raw, X_val_raw)
    
    return mx.array(X_train_std), mx.array(y_train), mx.array(X_val_std), mx.array(y_val)
```


```python
X_train, y_train, X_val, y_val = create_binary_dataset(
    df_annotations, DATA_DIR, target_size=(224, 224), samples_per_class=100
)
```

To reduce correlation between updates, we shuffle the dataset at every epoch and then build mini-batches. The function below, based on the [MLX MLP example](https://ml-explore.github.io/mlx/build/html/examples/mlp.html), automates this.
w.

```python
def batch_iterate(batch_size, X, y):
    perm = mx.array(np.random.permutation(y.size))
    for s in range(0, y.size, batch_size):
        ids = perm[s : s + batch_size]
        yield X[ids], y[ids]
```

## Build Model
Logistic regression takes a feature vector (`X`) and computes a linear score, then squashes it into a probability. In other words, the model forms a score `z = X @ W + b` (where `W` is called the weights matrix and `b` is the bias vector) and passes it through a non-linearity. 

For binary tasks it uses a sigmoid, which returns a value between 0 and 1. For multi-class tasks (such as retinopathy grades), it computes one score per class and applies softmax, which produces a probability for each class and ensures they sum to 1. It’s best viewed as a one-layer neural network: inputs → linear combination → non-linear activation. 

We follow this setup and train with cross-entropy on integer labels. 

```python
class MyLogisticRegression(nn.Module):
    def __init__(self, input_size: int, num_classes: int):
        super().__init__()
        # MLX automatically treats arrays assigned to instance variables as parameters
        self.weights = mx.random.normal((input_size, num_classes)) * 0.01
        self.bias = mx.zeros(num_classes)

    def __call__(self, x):
        linear_output = x @ self.weights + self.bias
        return mx.softmax(linear_output, axis=-1)
```

Next, we define a loss function to optimise the network parameters and an evaluation function to compute model accuracy on the validation set.

```python
def loss_fn(model, X, y):
    return mx.mean(nn.losses.cross_entropy(model(X), y))
```


```python
def eval_fn(model, X, y):
    return mx.mean(mx.argmax(model(X), axis=1) == y)
```

## Fit Model
In order to fit the model, the required steps are:
* Initialise the model and its parameters
* Associate the loss function with the model
* Define the optimiser to use
* Train the model for `n` epochs

```python
model = MyLogisticRegression(input_size=X_train.shape[1], num_classes=2)
mx.eval(model.parameters())  # Forces initialisation of weights and bias
model.parameters()
```

`nn.value_and_grad()` wraps the `loss_fn` so the returned callable computes both the loss and its gradients with respect to the model’s trainable parameters in one go.

The wrapped function:
* runs a forward pass with the current weights and biases to get predictions
* computes the loss against the targets
* backpropagates to obtain gradients w.r.t. the model’s parameters
* returns (loss, grads), where grads mirrors the model’s parameter structure.

```python
loss_and_grad_fn = nn.value_and_grad(model, loss_fn)
optimiser = optim.SGD(learning_rate=1e-5)
```

```python
for e in range(100):
    epoch_losses = []
    for X, y in batch_iterate(8, X_train, y_train):
        loss, grads = loss_and_grad_fn(model, X, y)
        epoch_losses.append(loss.item())
        # Updates model parameters using SGD
        optimiser.update(model, grads)
        mx.eval(model.parameters(), optimiser.state)  # Forces evaluation

    accuracy = eval_fn(model, X_val, y_val)
    avg_loss = sum(epoch_losses) / len(epoch_losses)
    print(f"Epoch {e}: Avg Loss {avg_loss:.6f}, Validation accuracy {accuracy.item():.3f}")
```

## Notes and Lessons
To conclude, here are my learnings from the exercise:
* Best validation accuracy was ~75% after ~100 epochs on my machine.
* Larger input images often helped; start small for speed, then scale up.
* If training collapses to predicting a single class, just rerun (initialisation + shuffling matter here).
* Keep the pipeline reproducible: balance classes, stratify, and standardise with training stats.