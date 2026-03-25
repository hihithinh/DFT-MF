import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint, EarlyStopping, CSVLogger, Callback
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from datetime import datetime
import logging
import time
import sys

# Setup logging
log_dir = "training_logs"
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(log_dir, f"training_{timestamp}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

logger.info("="*80)
logger.info("STARTING CNN TRAINING WITH GPU SUPPORT (Generator Mode)")
logger.info("="*80)

# Check GPU
logger.info("\n" + "="*80)
logger.info("GPU CONFIGURATION CHECK")
logger.info("="*80)
logger.info(f"TensorFlow version: {tf.__version__}")
logger.info(f"GPU Available: {tf.config.list_physical_devices('GPU')}")
logger.info(f"Built with CUDA: {tf.test.is_built_with_cuda()}")

gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logger.info(f"Found {len(gpus)} GPU(s)")
        for i, gpu in enumerate(gpus):
            logger.info(f"  GPU {i}: {gpu}")
        logger.info("Testing GPU accessibility...")
        with tf.device('/GPU:0'):
            test_tensor = tf.constant([[1.0, 2.0], [3.0, 4.0]])
            result = tf.matmul(test_tensor, test_tensor)
        logger.info("GPU test successful!")
    except RuntimeError as e:
        logger.error(f"GPU configuration error: {e}")
        gpus = []
else:
    logger.warning("No GPU found! Training will use CPU (very slow)")

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREPARED_DIR = os.path.join(BASE_DIR, "preprocessed_data")
IMG_SIZE = 50
BATCH_SIZE = 32
EPOCHS = 50
MODEL_NAME = f"CNN_CelebDF_{timestamp}"

logger.info("\n" + "="*80)
logger.info("TRAINING CONFIGURATION")
logger.info("="*80)
logger.info(f"Preprocessed data directory: {PREPARED_DIR}")
logger.info(f"Image size: {IMG_SIZE}x{IMG_SIZE}")
logger.info(f"Batch size: {BATCH_SIZE}")
logger.info(f"Epochs: {EPOCHS}")
logger.info(f"Model name: {MODEL_NAME}")

# Custom data generator to load from pickle in batches
import pickle

class PickleDataGenerator(tf.keras.utils.Sequence):
    def __init__(self, X_path, y_path, batch_size, shuffle=True):
        # Load only labels to get size
        with open(y_path, "rb") as f:
            self.y = pickle.load(f)
        self.X_path = X_path
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.indexes = np.arange(len(self.y))
        self.X_cache = None  # Will load X on first access
        if self.shuffle:
            np.random.shuffle(self.indexes)
    
    def __len__(self):
        return int(np.floor(len(self.y) / self.batch_size))
    
    def __getitem__(self, index):
        # Load X data on first access
        if self.X_cache is None:
            logger.info(f"Loading data from {self.X_path}...")
            with open(self.X_path, "rb") as f:
                self.X_cache = pickle.load(f) / 255.0
        
        # Get batch indexes
        batch_indexes = self.indexes[index * self.batch_size:(index + 1) * self.batch_size]
        
        # Get batch data
        X_batch = self.X_cache[batch_indexes]
        y_batch = self.y[batch_indexes]
        
        return X_batch, y_batch
    
    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indexes)

logger.info("\n" + "="*80)
logger.info("SETTING UP DATA GENERATORS")
logger.info("="*80)

X_train_path = os.path.join(PREPARED_DIR, "X_train.pickle")
y_train_path = os.path.join(PREPARED_DIR, "y_train.pickle")
X_test_path = os.path.join(PREPARED_DIR, "X_test.pickle")
y_test_path = os.path.join(PREPARED_DIR, "y_test.pickle")

# Load only labels to calculate class distribution
logger.info("Loading labels for class distribution...")
with open(y_train_path, "rb") as f:
    y_train = pickle.load(f)
with open(y_test_path, "rb") as f:
    y_test = pickle.load(f)

logger.info(f"Train samples: {len(y_train)}")
logger.info(f"Test samples: {len(y_test)}")

# Calculate class distribution
train_real = np.sum(y_train == 0)
train_fake = np.sum(y_train == 1)
test_real = np.sum(y_test == 0)
test_fake = np.sum(y_test == 1)

logger.info("\nClass distribution:")
logger.info(f"  Training - Real: {train_real}, Fake: {train_fake}")
logger.info(f"  Testing  - Real: {test_real}, Fake: {test_fake}")

# Calculate class weights
total_train = len(y_train)
weight_for_0 = (1 / train_real) * (total_train / 2.0)
weight_for_1 = (1 / train_fake) * (total_train / 2.0)
class_weight = {0: weight_for_0, 1: weight_for_1}
logger.info(f"\nClass weights: {class_weight}")

# Create generators
logger.info("\nCreating data generators...")
train_generator = PickleDataGenerator(X_train_path, y_train_path, BATCH_SIZE, shuffle=True)
test_generator = PickleDataGenerator(X_test_path, y_test_path, BATCH_SIZE, shuffle=False)

steps_per_epoch = len(train_generator)
validation_steps = len(test_generator)

logger.info(f"Steps per epoch: {steps_per_epoch}")
logger.info(f"Validation steps: {validation_steps}")

# Build model
logger.info("\n" + "="*80)
logger.info("BUILDING CNN MODEL")
logger.info("="*80)

model = Sequential()
model.add(Conv2D(256, (3, 3), input_shape=(IMG_SIZE, IMG_SIZE, 1)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(128, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.2))
model.add(Flatten())

model.add(Dense(64))
model.add(Activation('relu'))

model.add(Dense(1))
model.add(Activation('sigmoid'))

model.summary(print_fn=lambda x: logger.info(x))

# Compile model
logger.info("\nCompiling model...")
model.compile(
    loss='binary_crossentropy',
    optimizer='adam',
    metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
)

# Custom callback for progress logging
class ProgressLogger(Callback):
    def __init__(self, logger, total_epochs):
        super().__init__()
        self.logger = logger
        self.total_epochs = total_epochs
        self.epoch_start_time = None
        
    def on_epoch_begin(self, epoch, logs=None):
        self.epoch_start_time = time.time()
        self.logger.info(f"\n[Epoch {epoch+1}/{self.total_epochs}] Starting...")
        
    def on_epoch_end(self, epoch, logs=None):
        duration = time.time() - self.epoch_start_time
        msg1 = f"[Epoch {epoch+1}/{self.total_epochs}] Completed in {duration:.1f}s"
        msg2 = f"  Train Loss: {logs.get('loss', 0):.4f} | Train Acc: {logs.get('accuracy', 0):.4f}"
        msg3 = f"  Val Loss:   {logs.get('val_loss', 0):.4f} | Val Acc:   {logs.get('val_accuracy', 0):.4f}"
        
        self.logger.info(msg1)
        self.logger.info(msg2)
        self.logger.info(msg3)
        
        if 'val_accuracy' in logs:
            progress = (epoch + 1) / self.total_epochs * 100
            # Get best val accuracy from history
            val_accs = self.model.history.history.get('val_accuracy', [])
            if val_accs:
                best_val_acc = max(val_accs)
            else:
                best_val_acc = logs.get('val_accuracy', 0)
            msg4 = f"  Progress: {progress:.1f}% | Best Val Acc: {best_val_acc:.4f}"
            self.logger.info(msg4)
        
        sys.stdout.flush()
        sys.stderr.flush()

# Setup callbacks
callbacks_dir = "callbacks"
os.makedirs(callbacks_dir, exist_ok=True)

tensorboard_dir = os.path.join("logs", MODEL_NAME)
os.makedirs(tensorboard_dir, exist_ok=True)

callbacks = [
    ProgressLogger(logger, EPOCHS),
    TensorBoard(log_dir=tensorboard_dir, histogram_freq=1),
    ModelCheckpoint(
        filepath=os.path.join(callbacks_dir, f"{MODEL_NAME}_best.h5"),
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=0
    ),
    EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=0
    ),
    CSVLogger(os.path.join(log_dir, f"training_history_{timestamp}.csv"))
]

logger.info(f"TensorBoard logs: {tensorboard_dir}")
logger.info(f"Model checkpoints: {callbacks_dir}")

# Train model
logger.info("\n" + "="*80)
logger.info("STARTING TRAINING")
logger.info("="*80)

device_name = '/GPU:0' if gpus else '/CPU:0'
logger.info(f"Training on device: {device_name}")

history = model.fit(
    train_generator,
    steps_per_epoch=steps_per_epoch,
    epochs=EPOCHS,
    validation_data=test_generator,
    validation_steps=validation_steps,
    class_weight=class_weight,
    callbacks=callbacks,
    verbose=0
)

# Evaluate on test set
logger.info("\n" + "="*80)
logger.info("FINAL EVALUATION")
logger.info("="*80)

test_results = model.evaluate(test_generator, verbose=0)
logger.info(f"Test Loss: {test_results[0]:.4f}")
logger.info(f"Test Accuracy: {test_results[1]:.4f}")
logger.info(f"Test Precision: {test_results[2]:.4f}")
logger.info(f"Test Recall: {test_results[3]:.4f}")

# Calculate F1 Score
precision = test_results[2]
recall = test_results[3]
f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
logger.info(f"Test F1-Score: {f1_score:.4f}")

# Save final model
models_dir = "trained_models"
os.makedirs(models_dir, exist_ok=True)
final_model_path = os.path.join(models_dir, f"{MODEL_NAME}_final.h5")
model.save(final_model_path)
logger.info(f"\nFinal model saved: {final_model_path}")

logger.info("\n" + "="*80)
logger.info("TRAINING COMPLETED SUCCESSFULLY!")
logger.info("="*80)
logger.info(f"Log file: {log_file}")
logger.info(f"TensorBoard: tensorboard --logdir={tensorboard_dir}")
logger.info("="*80)
