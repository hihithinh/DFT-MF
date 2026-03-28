from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
import sys
import os
import glob
import openpyxl
from timeit import default_timer as timer
import time
# import face_recognition  # Commented out - crashes with dlib CUDA build
import cv2
from datetime import datetime
import math
from multiprocessing import Pool, cpu_count
from functools import partial

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
predictor_path = os.path.join(BASE_DIR, "shape_predictor_68_face_landmarks.dat")

def get_lip_height(lip):
    """Calculate average height of lip"""
    sum=0
    for i in [2,3,4]:
        distance = math.sqrt( (lip[i][0] - lip[12-i][0])**2 +
                              (lip[i][1] - lip[12-i][1])**2   )
        sum += distance
    return sum / 3

def get_mouth_height(top_lip, bottom_lip):
    sum=0
    for i in [8,9,10]:
        distance = math.sqrt( (top_lip[i][0] - bottom_lip[18-i][0])**2 + 
                              (top_lip[i][1] - bottom_lip[18-i][1])**2   )
        sum += distance
    return sum / 3

def is_mouth_open(face_landmarks):
    top_lip = face_landmarks['top_lip']
    bottom_lip = face_landmarks['bottom_lip']

    top_lip_height = get_lip_height(top_lip)
    bottom_lip_height = get_lip_height(bottom_lip)
    mouth_height = get_mouth_height(top_lip, bottom_lip)
    
    ratio = 0.4
    if mouth_height > min(top_lip_height, bottom_lip_height) * ratio:
        return True
    else:
        return False

def Crooped_mouth(frame, detector, predictor):
    """Crop mouth from frame using dlib"""
    dets = detector(frame, 1)
    for k, d in enumerate(dets):
        shape = predictor(frame, d)     
        xmouthpoints = [shape.part(x).x for x in range(48,67)]
        ymouthpoints = [shape.part(x).y for x in range(48,67)]
        maxx = max(xmouthpoints)
        minx = min(xmouthpoints)
        maxy = max(ymouthpoints)
        miny = min(ymouthpoints) 
        pad = 10
        mouth = frame[miny-pad:maxy+pad,minx-pad:maxx+pad]
        crop_image = frame[miny-pad:maxy+pad,minx-pad:maxx+pad]
        Final_image = cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY)
        return Final_image
    return None

def process_single_video(args_tuple):
    """Process a single video - will be called in parallel"""
    video_name, dataset_folder = args_tuple
    import logging
    import sys
    
    # Use print for child process output (logging doesn't work with Pool)
    from datetime import datetime
    
    def log_msg(msg):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {msg}", flush=True)
    
    try:
        log_msg(f">> Starting {video_name}...")
        model_start = timer()
        
        # Each process loads its own models
        # Use HOG detector (fast and stable)
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(predictor_path)
        
        model_time = timer() - model_start
        start = timer()
        
        faces_folder_path = os.path.join(BASE_DIR, dataset_folder, "ExtractFrams", video_name)
        
        # Different folder structure for different datasets
        mouth_dir = os.path.join(BASE_DIR, dataset_folder, "CroppedMouth", video_name)
        
        os.makedirs(mouth_dir, exist_ok=True)
        imagesFolder = mouth_dir

        # Get all frames
        frame_files = sorted(glob.glob(os.path.join(faces_folder_path, "*.jpg")))
        total_frames = len(frame_files)
        
        M = 0
        processed_frames = 0
        no_face_count = 0
        open_mouth_count = 0
        
        # Progress logging every 1/4 of video
        log_interval = max(1, total_frames // 4)
        
        for i, f in enumerate(frame_files):
            processed_frames += 1
            
            # Progress log every 1/4
            if processed_frames % log_interval == 0:
                progress = (processed_frames / total_frames) * 100
                fps = processed_frames / (timer() - start) if (timer() - start) > 0 else 0
                log_msg(f"  {video_name}: {processed_frames}/{total_frames} ({progress:.0f}%) - {fps:.1f} fps - Open: {M}")
            
            # Load image with error handling
            try:
                frame = cv2.imread(f)
                if frame is None or frame.size == 0:
                    continue
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            except Exception:
                continue  # Skip corrupt frames
            
            # Find faces using HOG detector (already loaded outside loop)
            faces = detector(frame_rgb, 1)
            
            # Convert to face_recognition format for compatibility
            face_locations = [(face.top(), face.right(), face.bottom(), face.left()) for face in faces]
            
            # Get face landmarks using dlib
            face_landmarks_list = []
            for face in faces:
                shape = predictor(frame_rgb, face)
                landmarks = face_utils.shape_to_np(shape)
                
                # Convert to face_recognition format
                # dlib 68-point landmarks for mouth:
                # Outer lip: 48-59 (12 points clockwise from left corner)
                # Inner lip: 60-67 (8 points)
                # 
                # face_recognition format:
                # top_lip: upper contour (outer top + inner top reversed)
                # bottom_lip: lower contour (outer bottom + inner bottom reversed)
                
                # Top lip: outer points 48-54 (left to right) + inner points 64-60 (right to left)
                top_lip_outer = landmarks[48:55].tolist()  # 48-54 (7 points)
                top_lip_inner = landmarks[60:65].tolist()[::-1]  # 64-60 reversed (5 points)
                
                # Bottom lip: outer points 54-59+48 (right to left) + inner points 60-64 (left to right)
                bottom_lip_outer = (landmarks[54:60].tolist() + [landmarks[48].tolist()])  # 54-59+48 (7 points)
                bottom_lip_inner = landmarks[64:68].tolist() + [landmarks[60].tolist()]  # 64-67+60 (5 points)
                
                face_landmarks_dict = {
                    'top_lip': top_lip_outer + top_lip_inner,  # 12 points total
                    'bottom_lip': bottom_lip_outer + bottom_lip_inner  # 12 points total
                }
                face_landmarks_list.append(face_landmarks_dict)
            
            if len(face_locations) == 0:
                no_face_count += 1
                continue
                
            # Process each face
            for face_landmarks in face_landmarks_list:
                ret_mouth_open = is_mouth_open(face_landmarks)
                if ret_mouth_open is True:
                    open_mouth_count += 1
                    cropped = Crooped_mouth(frame, detector, predictor)
                    if cropped is not None:
                        filename = os.path.splitext(imagesFolder+"/Real")[0]
                        cv2.imwrite(filename+str(int(M))+'.jpg', cropped)
                        M += 1
        
        end = timer()
        elapsed = timer() - start
        fps = processed_frames / elapsed if elapsed > 0 else 0
        
        log_msg(f"[OK] {video_name} DONE: {M}/{processed_frames} open mouths ({elapsed:.1f}s, {fps:.1f} fps)")
        
        return {
            'video_name': video_name,
            'open_mouth_frames': M,
            'total_frames': processed_frames,
            'time_seconds': elapsed,
            'fps': fps,
            'no_face_frames': no_face_count,
            'detected_open_mouths': open_mouth_count,
            'success': True
        }
    except Exception as e:
        elapsed = timer() - start if 'start' in locals() else 0
        # Log error for debugging
        import traceback
        error_msg = f"{str(e)[:200]}"  # Truncate long errors
        log_msg(f"[FAIL] {video_name}: {error_msg}")
        return {
            'success': False,
            'video_name': video_name,
            'error': error_msg,
            'time_seconds': elapsed
        }

def get_processed_videos(dataset_folder):
    """Get list of already processed videos from Excel"""
    try:
        result_file = os.path.join(BASE_DIR, dataset_folder, 'Result.xlsx')
        book = openpyxl.load_workbook(result_file)
        sheet = book.active
        processed = []
        for row in sheet.iter_rows():
            if row[2].value and 'Open mouth frames' in str(row[2].value):
                video_name = str(row[2].value).replace('Open mouth frames ', '')
                processed.append(video_name)
        return processed
    except:
        return []

if __name__ == '__main__':
    import logging
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='Crop open mouth frames from videos')
    parser.add_argument('dataset', nargs='?', default='CelebDF', choices=['UADFV', 'CelebDF'],
                        help='Dataset name: UADFV or CelebDF (default: CelebDF)')
    args = parser.parse_args()
    
    dataset_folder = args.dataset
    
    # Setup main process logging
    logging.basicConfig(
        level=logging.INFO,
        format='[MAIN] %(asctime)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    log = logging.getLogger(__name__)
    
    log.info(f"Dataset: {dataset_folder}")
    log.info(f"Working directory: {os.path.join(BASE_DIR, dataset_folder)}")
    
    os.makedirs(os.path.join(BASE_DIR, dataset_folder, "ExtractFrams"), exist_ok=True)
    
    # Create CroppedMouth directory based on dataset
    if dataset_folder == "UADFV":
        os.makedirs(os.path.join(BASE_DIR, dataset_folder, "CroppedMouth"), exist_ok=True)
    else:
        os.makedirs(os.path.join(BASE_DIR, "CroppedMouth", dataset_folder), exist_ok=True)
    
    # Get all video folders
    extract_frams_dir = os.path.join(BASE_DIR, dataset_folder, "ExtractFrams")
    all_video_folders = sorted([d for d in os.listdir(extract_frams_dir) 
                           if os.path.isdir(os.path.join(extract_frams_dir, d))])

    # Get already processed videos
    processed_videos = get_processed_videos(dataset_folder)
    log.info(f"Found {len(processed_videos)} already processed videos")
    
    # Skip already processed videos (except last 9 which might be incomplete)
    if len(processed_videos) > 9:
        skip_videos = set(processed_videos[:-9])
        log.info(f"Skipping {len(skip_videos)} completed videos (keeping last 9 for reprocessing)")
    else:
        skip_videos = set()
        log.info(f"Reprocessing all {len(processed_videos)} videos (less than 9)")
    
    video_folders = [v for v in all_video_folders if v not in skip_videos]
    
    # Use 4 workers for optimal GPU/CPU balance with CNN detector
    num_workers = 4
    
    log.info(f"Starting GPU-accelerated parallel processing")
    log.info(f"Total videos: {len(all_video_folders)}")
    log.info(f"Already processed: {len(processed_videos)}")
    log.info(f"To process: {len(video_folders)}")
    log.info(f"Using {num_workers} parallel workers")
    log.info(f"GPU acceleration: ENABLED (CUDA)")
    result_file = os.path.join(BASE_DIR, dataset_folder, 'Result.xlsx')
    log.info(f"Results will be saved to: {result_file}")
    log.info("=" * 60)
    
    # Load Excel workbook
    if not os.path.exists(result_file):
        book = openpyxl.Workbook()
        sheet = book.active
        book.save(result_file)
    else:
        book = openpyxl.load_workbook(result_file)
        sheet = book.active
    
    # Find next empty row
    sheetCount = 1
    for row in sheet.iter_rows():
        if row[2].value and 'Open mouth frames' in str(row[2].value):
            sheetCount += 1
    
    overall_start = timer()
    
    # Process videos in parallel with real-time results
    log.info("Starting parallel processing...")
    
    completed_count = 0
    failed_count = 0
    total_open_mouth = 0
    total_frames = 0
    total_videos = len(video_folders)
    
    with Pool(processes=num_workers) as pool:
        # Use imap_unordered to get results as they complete
        video_args = [(v, dataset_folder) for v in video_folders]
        for i, result in enumerate(pool.imap_unordered(process_single_video, video_args), 1):
            if result['success']:
                completed_count += 1
                video_name = result['video_name']
                M = result['open_mouth_frames']
                processed = result['total_frames']
                elapsed = result['time_seconds']
                fps = result.get('fps', 0)
                
                # Save to Excel
                sheet['C'+str(sheetCount)] = f"Open mouth frames {video_name}"
                sheet['D'+str(sheetCount)] = str(M)
                sheet['L'+str(sheetCount)] = elapsed
                sheetCount += 1
                
                total_open_mouth += M
                total_frames += processed
                
                # Log successful video
                log.info(f"[{i}/{total_videos}] OK: {video_name} - {M}/{processed} open mouths ({elapsed:.1f}s, {fps:.1f} fps)")
            else:
                failed_count += 1
                video_name = result['video_name']
                error = result.get('error', 'Unknown error')
                
                # Log failed video
                log.info(f"[{i}/{total_videos}] FAIL: {video_name} - {error[:80]}")
            
            # Save Excel and show progress every 3 videos (regardless of success/failure)
            if i % 4 == 0:
                book.save(result_file)
                elapsed_total = timer() - overall_start
                videos_per_hour = (i / elapsed_total) * 3600 if elapsed_total > 0 else 0
                remaining = total_videos - i
                eta_hours = (remaining / videos_per_hour) if videos_per_hour > 0 else 0
                log.info(f">> Progress: {i}/{total_videos} ({i/total_videos*100:.1f}%) | {videos_per_hour:.1f} videos/hr | ETA: {eta_hours:.1f}h | Success: {completed_count} | Failed: {failed_count}")
    
    overall_end = timer()
    
    # Final save
    book.save(result_file)
    
    total_time = int(overall_end - overall_start)
    
    log.info("=" * 60)
    log.info("ALL VIDEOS PROCESSED!")
    log.info(f"Successful: {completed_count}/{total_videos}")
    log.info(f"Failed: {failed_count}/{total_videos}")
    log.info(f"Total open mouth frames: {total_open_mouth}")
    log.info(f"Total frames processed: {total_frames}")
    log.info(f"Total time: {total_time}s ({total_time/60:.1f} minutes)")
    if total_time > 0:
        log.info(f"Average speed: {total_videos/total_time*60:.1f} videos/hour")
    log.info(f"Results saved to: {result_file}")
    # Show correct output path based on dataset
    if dataset_folder == "UADFV":
        output_path = os.path.join(BASE_DIR, dataset_folder, "CroppedMouth")
    else:
        output_path = os.path.join(BASE_DIR, "CroppedMouth", dataset_folder)
    log.info(f"Cropped images saved to: {output_path}")
    log.info("=" * 60)
    
    # Performance summary
    if total_time > 0:
        log.info("Final performance summary:")
        log.info(f"   Processing rate: {total_videos/total_time*60:.1f} videos/hour")
        log.info(f"   Time per video: {total_time/total_videos:.1f} seconds")
        log.info(f"   Workers: {num_workers}")
        log.info(f"   GPU acceleration: ENABLED")
        
        if total_frames > 0:
            log.info(f"   Overall FPS: {total_frames/total_time:.1f} frames/second")
            log.info(f"   Open mouth rate: {(total_open_mouth/total_frames)*100:.1f}%")
