import os
import cv2
import numpy as np
import pickle
import argparse
from sklearn.model_selection import train_test_split
from tqdm import tqdm

def prepare_dataset(dataset_name, img_size=50):
    """
    Prepare dataset from CroppedMouth folders
    Split by VIDEO to avoid data leakage
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Determine CroppedMouth directory based on dataset
    cropped_mouth_dir = os.path.join(BASE_DIR, dataset_name, "CelebDF/CroppedMouth")
    
    # Create dataset-specific preprocessed data directory
    output_dir = os.path.join(BASE_DIR, dataset_name, "preprocessed_data")
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading images from: {cropped_mouth_dir}")
    print(f"Image size: {img_size}x{img_size}")
    
    # Step 1: Build video label mapping for CelebDF
    video_label_map = {}
    if dataset_name == "CelebDF":
        dataset_dir = os.path.join(BASE_DIR, "dataset", "Celeb-DF")
        
        # Scan Celeb-real and YouTube-real for real videos
        for real_folder in ["Celeb-real", "YouTube-real"]:
            real_path = os.path.join(dataset_dir, real_folder)
            if os.path.exists(real_path):
                for video_file in os.listdir(real_path):
                    if video_file.endswith('.mp4'):
                        video_name = os.path.splitext(video_file)[0]
                        video_label_map[video_name] = 0  # Real
        
        # Scan Celeb-synthesis for fake videos
        fake_path = os.path.join(dataset_dir, "Celeb-synthesis")
        if os.path.exists(fake_path):
            for video_file in os.listdir(fake_path):
                if video_file.endswith('.mp4'):
                    video_name = os.path.splitext(video_file)[0]
                    video_label_map[video_name] = 1  # Fake
        
        print(f"CelebDF label mapping: {len(video_label_map)} videos")
        print(f"  Real: {sum(1 for v in video_label_map.values() if v == 0)}")
        print(f"  Fake: {sum(1 for v in video_label_map.values() if v == 1)}")
    
    # Step 2: Group frames by video
    video_data = {}  # {video_id: {'frames': [...], 'label': 0/1}}
    
    # Get all video folders
    video_folders = [f for f in os.listdir(cropped_mouth_dir) 
                    if os.path.isdir(os.path.join(cropped_mouth_dir, f))]
    
    print(f"\nFound {len(video_folders)} video folders")
    
    for video_folder in tqdm(video_folders, desc="Loading videos"):
        video_path = os.path.join(cropped_mouth_dir, video_folder)
        
        # Determine label based on dataset
        # Label 0 = Real, Label 1 = Fake
        if dataset_name == "UADFV":
            label = 1 if video_folder.startswith("fake") else 0
        elif dataset_name == "CelebDF":
            # Use mapping from original dataset
            label = video_label_map.get(video_folder, None)
            if label is None:
                print(f"Warning: Unknown video {video_folder}, skipping...")
                continue
        else:
            label = 1 if "fake" in video_folder.lower() else 0
        
        # Load all images from this video folder
        image_files = [f for f in os.listdir(video_path) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        frames = []
        for img_file in image_files:
            img_path = os.path.join(video_path, img_file)
            try:
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    img = cv2.resize(img, (img_size, img_size))
                    frames.append(img)
            except Exception as e:
                print(f"Error loading {img_path}: {e}")
                continue
        
        if frames:
            video_data[video_folder] = {'frames': frames, 'label': label}
    
    # Step 2: Split videos into train/val/test (70/15/15)
    video_ids = list(video_data.keys())
    video_labels = [video_data[vid]['label'] for vid in video_ids]
    
    print(f"\nTotal videos: {len(video_ids)}")
    print(f"Fake videos: {sum(video_labels)}")
    print(f"Real videos: {len(video_labels) - sum(video_labels)}")
    
    # First split: 70% train, 30% temp (by VIDEO)
    train_videos, temp_videos = train_test_split(
        video_ids, test_size=0.3, random_state=42, stratify=video_labels
    )
    
    # Second split: split temp into 50% val, 50% test (by VIDEO)
    temp_labels = [video_data[vid]['label'] for vid in temp_videos]
    val_videos, test_videos = train_test_split(
        temp_videos, test_size=0.5, random_state=42, stratify=temp_labels
    )
    
    print(f"\nVideo split:")
    print(f"  Train videos: {len(train_videos)}")
    print(f"  Val videos: {len(val_videos)}")
    print(f"  Test videos: {len(test_videos)}")
    
    # Step 3: Collect frames from each video split
    def collect_frames(video_list):
        X, y = [], []
        for video_id in video_list:
            frames = video_data[video_id]['frames']
            label = video_data[video_id]['label']
            X.extend(frames)
            y.extend([label] * len(frames))
        return np.array(X, dtype="float32"), np.array(y)
    
    print("\nCollecting frames from videos...")
    X_train, y_train = collect_frames(train_videos)
    X_val, y_val = collect_frames(val_videos)
    X_test, y_test = collect_frames(test_videos)
    
    # Reshape and normalize
    X_train = X_train.reshape(-1, img_size, img_size, 1) / 255.0
    X_val = X_val.reshape(-1, img_size, img_size, 1) / 255.0
    X_test = X_test.reshape(-1, img_size, img_size, 1) / 255.0
    
    total_frames = len(X_train) + len(X_val) + len(X_test)
    print(f"\nTotal frames: {total_frames}")
    print(f"Fake frames: {np.sum(y_train == 1) + np.sum(y_val == 1) + np.sum(y_test == 1)}")
    print(f"Real frames: {np.sum(y_train == 0) + np.sum(y_val == 0) + np.sum(y_test == 0)}")
    
    print(f"\nTrain set: {len(X_train)} images ({len(X_train)/total_frames*100:.1f}%)")
    print(f"Validation set: {len(X_val)} images ({len(X_val)/total_frames*100:.1f}%)")
    print(f"Test set: {len(X_test)} images ({len(X_test)/total_frames*100:.1f}%)")
    
    # Save preprocessed data
    print("\nSaving preprocessed data...")
    
    with open(os.path.join(output_dir, "X_train.pickle"), "wb") as f:
        pickle.dump(X_train, f)
    
    with open(os.path.join(output_dir, "X_val.pickle"), "wb") as f:
        pickle.dump(X_val, f)
    
    with open(os.path.join(output_dir, "X_test.pickle"), "wb") as f:
        pickle.dump(X_test, f)
    
    with open(os.path.join(output_dir, "y_train.pickle"), "wb") as f:
        pickle.dump(y_train, f)
    
    with open(os.path.join(output_dir, "y_val.pickle"), "wb") as f:
        pickle.dump(y_val, f)
    
    with open(os.path.join(output_dir, "y_test.pickle"), "wb") as f:
        pickle.dump(y_test, f)
    
    print(f"Data saved to: {output_dir}")
    print("\nPreprocessing complete!")
    
    return X_train, X_val, X_test, y_train, y_val, y_test

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prepare dataset for training')
    parser.add_argument('dataset', nargs='?', default='CelebDF', 
                       choices=['UADFV', 'CelebDF'],
                       help='Dataset name: UADFV or CelebDF (default: CelebDF)')
    parser.add_argument('--img-size', type=int, default=50,
                       help='Image size (default: 50)')
    
    args = parser.parse_args()
    
    prepare_dataset(args.dataset, args.img_size)
