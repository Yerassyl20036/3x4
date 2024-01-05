import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import cv2
import time
from PIL import Image

def crop_and_save_images(input_folder, output_folder, aspect_ratio=(3, 4), scale_factor=1.5):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(input_folder, filename)
            img = cv2.imread(img_path)

            if img is None:
                print(f"Cannot read image at path: {img_path}")
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            h = gray.shape[0]
            roi_upper_gray = gray[:2 * h // 3, :]

            faces = face_cascade.detectMultiScale(roi_upper_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                max_area = 0
                max_face = None
                for (x, y, w, h) in faces:
                    current_area = w * h
                    if current_area > max_area:
                        max_area = current_area
                        max_face = (x, y, w, h)

                x, y, w, h = max_face

                # Apply scaling factor
                w_scaled = int(w * scale_factor)
                h_scaled = int(h * scale_factor)

                # Centering the scaled face region
                center_x, center_y = x + w // 2, y + h // 2
                img_height, img_width = img.shape[:2]

                # Calculating the new crop size
                new_width = min(w_scaled, img_width)
                new_height = int(new_width * aspect_ratio[1] / aspect_ratio[0])

                # Adjusting crop area to image dimensions
                x1 = max(0, center_x - new_width // 2)
                x2 = min(img_width, center_x + new_width // 2)
                y1 = max(0, center_y - new_height // 2)
                y2 = min(img_height, center_y + new_height // 2)

                cropped_img = img[y1:y2, x1:x2]
                pil_image = Image.fromarray(cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB))

                # Save the cropped image
                output_path = os.path.join(output_folder, filename)
                pil_image.save(output_path)

                print(f"Processed {filename}")
            else:
                print(f"No face detected in {filename}. Skipping...")

# Usage
def start_cropping():
    input_folder = input_path.get()
    output_folder = output_path.get()

    if not input_folder or not output_folder:
        messagebox.showerror("Error", "Please select both input and output folders.")
        return

    # Disable start button and reset progress bar
    start_button.config(state=tk.DISABLED)
    window.update()

    total_files = len([name for name in os.listdir(input_folder) if name.lower().endswith(('.png', '.jpg', '.jpeg'))])

    def thread_target():
        crop_and_save_images(input_folder, output_folder)
        messagebox.showinfo("Complete", "Processing complete.")
        start_button.config(state=tk.NORMAL)

    # Start the cropping in a separate thread to keep the UI responsive
    thread = threading.Thread(target=thread_target)
    thread.start()

# Update progress bar
def update_progress_bar():
    while True:
        try:
            window.update()
            time.sleep(1)
        except:
            break

def select_input_folder():
    path = filedialog.askdirectory()
    input_path.set(path)

def select_output_folder():
    path = filedialog.askdirectory()
    output_path.set(path)

# Setting up the UI
window = tk.Tk()
window.title("Image Cropper")

input_path = tk.StringVar()
output_path = tk.StringVar()

tk.Label(window, text="Input Folder:").grid(row=0, column=0, padx=10, pady=10)
input_entry = tk.Entry(window, textvariable=input_path, width=50).grid(row=0, column=1, padx=10, pady=10)
input_button = tk.Button(window, text="Browse", command=select_input_folder).grid(row=0, column=2, padx=10, pady=10)

tk.Label(window, text="Output Folder:").grid(row=1, column=0, padx=10, pady=10)
output_entry = tk.Entry(window, textvariable=output_path, width=50).grid(row=1, column=1, padx=10, pady=10)
output_button = tk.Button(window, text="Browse", command=select_output_folder).grid(row=1, column=2, padx=10, pady=10)

start_button = tk.Button(window, text="Start", command=start_cropping)
start_button.grid(row=2, column=1, padx=10, pady=10)


window.mainloop()

