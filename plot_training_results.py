import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10

# Read data
uadfv_data = pd.read_csv('training_logs/training_history_20260328_130711.csv')
celebdf_data = pd.read_csv('training_logs/training_history_20260328_131026.csv')

# Create figure with subplots
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('So sánh kết quả huấn luyện: UADFV vs CelebDF', fontsize=16, fontweight='bold')

# 1. Training Accuracy
axes[0, 0].plot(uadfv_data['epoch'] + 1, uadfv_data['accuracy'], 'o-', label='UADFV', linewidth=2, markersize=6)
axes[0, 0].plot(celebdf_data['epoch'] + 1, celebdf_data['accuracy'], 's-', label='CelebDF', linewidth=2, markersize=6)
axes[0, 0].set_xlabel('Epoch')
axes[0, 0].set_ylabel('Accuracy')
axes[0, 0].set_title('Training Accuracy')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# 2. Validation Accuracy
axes[0, 1].plot(uadfv_data['epoch'] + 1, uadfv_data['val_accuracy'], 'o-', label='UADFV', linewidth=2, markersize=6)
axes[0, 1].plot(celebdf_data['epoch'] + 1, celebdf_data['val_accuracy'], 's-', label='CelebDF', linewidth=2, markersize=6)
axes[0, 1].set_xlabel('Epoch')
axes[0, 1].set_ylabel('Validation Accuracy')
axes[0, 1].set_title('Validation Accuracy')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# 3. Training Loss
axes[0, 2].plot(uadfv_data['epoch'] + 1, uadfv_data['loss'], 'o-', label='UADFV', linewidth=2, markersize=6)
axes[0, 2].plot(celebdf_data['epoch'] + 1, celebdf_data['loss'], 's-', label='CelebDF', linewidth=2, markersize=6)
axes[0, 2].set_xlabel('Epoch')
axes[0, 2].set_ylabel('Loss')
axes[0, 2].set_title('Training Loss')
axes[0, 2].legend()
axes[0, 2].grid(True, alpha=0.3)

# 4. Validation Loss
axes[1, 0].plot(uadfv_data['epoch'] + 1, uadfv_data['val_loss'], 'o-', label='UADFV', linewidth=2, markersize=6)
axes[1, 0].plot(celebdf_data['epoch'] + 1, celebdf_data['val_loss'], 's-', label='CelebDF', linewidth=2, markersize=6)
axes[1, 0].set_xlabel('Epoch')
axes[1, 0].set_ylabel('Validation Loss')
axes[1, 0].set_title('Validation Loss')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# 5. Precision
axes[1, 1].plot(uadfv_data['epoch'] + 1, uadfv_data['precision'], 'o-', label='UADFV (Train)', linewidth=2, markersize=6)
axes[1, 1].plot(celebdf_data['epoch'] + 1, celebdf_data['precision'], 's-', label='CelebDF (Train)', linewidth=2, markersize=6)
axes[1, 1].plot(uadfv_data['epoch'] + 1, uadfv_data['val_precision'], 'o--', label='UADFV (Val)', linewidth=2, markersize=6, alpha=0.7)
axes[1, 1].plot(celebdf_data['epoch'] + 1, celebdf_data['val_precision'], 's--', label='CelebDF (Val)', linewidth=2, markersize=6, alpha=0.7)
axes[1, 1].set_xlabel('Epoch')
axes[1, 1].set_ylabel('Precision')
axes[1, 1].set_title('Precision (Train & Validation)')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

# 6. Recall
axes[1, 2].plot(uadfv_data['epoch'] + 1, uadfv_data['recall'], 'o-', label='UADFV (Train)', linewidth=2, markersize=6)
axes[1, 2].plot(celebdf_data['epoch'] + 1, celebdf_data['recall'], 's-', label='CelebDF (Train)', linewidth=2, markersize=6)
axes[1, 2].plot(uadfv_data['epoch'] + 1, uadfv_data['val_recall'], 'o--', label='UADFV (Val)', linewidth=2, markersize=6, alpha=0.7)
axes[1, 2].plot(celebdf_data['epoch'] + 1, celebdf_data['val_recall'], 's--', label='CelebDF (Val)', linewidth=2, markersize=6, alpha=0.7)
axes[1, 2].set_xlabel('Epoch')
axes[1, 2].set_ylabel('Recall')
axes[1, 2].set_title('Recall (Train & Validation)')
axes[1, 2].legend()
axes[1, 2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('materials/training_comparison.png', dpi=300, bbox_inches='tight')
print("Đã lưu biểu đồ vào: materials/training_comparison.png")

# Create comparison bar chart for final test results
fig2, ax = plt.subplots(figsize=(10, 6))

metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
uadfv_scores = [0.8026, 0.7816, 0.8525, 0.8155]
celebdf_scores = [0.8197, 0.8380, 0.8979, 0.8669]

x = np.arange(len(metrics))
width = 0.35

bars1 = ax.bar(x - width/2, uadfv_scores, width, label='UADFV', alpha=0.8)
bars2 = ax.bar(x + width/2, celebdf_scores, width, label='CelebDF', alpha=0.8)

ax.set_xlabel('Metrics')
ax.set_ylabel('Score')
ax.set_title('So sánh kết quả Test cuối cùng: UADFV vs CelebDF')
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}',
                ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('materials/test_results_comparison.png', dpi=300, bbox_inches='tight')
print("Đã lưu biểu đồ vào: materials/test_results_comparison.png")

print("\nĐã tạo xong 2 biểu đồ!")
