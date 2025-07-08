import os
from PIL import Image
from PIL.ExifTags import TAGS
import tkinter as tk
from tkinter import filedialog, messagebox
import logging

# ログ設定
logging.basicConfig(filename="photo_sorting.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def browse_input_folder():
    """
    入力フォルダを選択するためのダイアログを表示し、選択されたフォルダパスを変数に設定します。
    """
    folder = filedialog.askdirectory()
    if folder:
        input_folder_var.set(folder)

def browse_output_folder():
    """
    出力フォルダを選択するためのダイアログを表示し、選択されたフォルダパスを変数に設定します。
    """
    folder = filedialog.askdirectory()
    if folder:
        output_folder_var.set(folder)

def get_image_taken_date(image_path):
    """
    画像ファイルのEXIFデータから撮影日を取得します。

    Args:
        image_path (str): 画像ファイルのパス

    Returns:
        str: 撮影日（YYYY-MM-DD形式）またはNone
    """
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "DateTimeOriginal":
                        return value.split(" ")[0].replace(":", "-")  # 日付部分のみ取得
            return None
    except Exception:
        return None

def sort_images_by_date(input_folder, output_folder, date_format):
    """
    指定された入力フォルダ内の画像を撮影日ごとに出力フォルダに振り分けます。

    Args:
        input_folder (str): 入力フォルダのパス
        output_folder (str): 出力フォルダのパス
        date_format (str): 日付フォーマット

    Raises:
        ValueError: 入力フォルダが存在しない場合
    """
    if not os.path.exists(input_folder):
        raise ValueError("入力フォルダが存在しません。")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, _, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.join(root, file)
            taken_date = get_image_taken_date(file_path)
            try:
                if taken_date:
                    # 撮影日フォルダを作成
                    date_folder = os.path.join(output_folder, taken_date)
                    if not os.path.exists(date_folder):
                        os.makedirs(date_folder)
                    destination = os.path.join(date_folder, file)
                    if os.path.exists(destination):
                        base, ext = os.path.splitext(file)
                        counter = 1
                        while os.path.exists(destination):
                            destination = os.path.join(date_folder, f"{base}_{counter}{ext}")
                            counter += 1
                    os.rename(file_path, destination)
                    logging.info(f"Moved {file} to {date_folder}")
                else:
                    # 撮影日がない場合のフォルダ
                    no_date_folder = os.path.join(output_folder, "NoDate")
                    if not os.path.exists(no_date_folder):
                        os.makedirs(no_date_folder)
                    destination = os.path.join(no_date_folder, file)
                    if os.path.exists(destination):
                        base, ext = os.path.splitext(file)
                        counter = 1
                        while os.path.exists(destination):
                            destination = os.path.join(no_date_folder, f"{base}_{counter}{ext}")
                            counter += 1
                    os.rename(file_path, destination)
                    logging.info(f"Moved {file} to {no_date_folder}")
            except Exception as e:
                logging.error(f"Error moving file {file_path}: {e}")

def execute_sorting():
    """
    GUIで指定された入力フォルダ、出力フォルダ、日付フォーマットを使用して画像の振り分けを実行します。
    """
    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()
    date_format = date_format_var.get()

    if not input_folder or not output_folder:
        messagebox.showerror("エラー", "入力フォルダと出力フォルダを指定してください。")
        return

    try:
        sort_images_by_date(input_folder, output_folder, date_format)
        messagebox.showinfo("成功", "振り分け処理が完了しました。")
    except Exception as e:
        messagebox.showerror("エラー", f"振り分け処理中にエラーが発生しました: {e}")

# メインウィンドウの作成
root = tk.Tk()
root.title("写真振り分けツール")

# 入力フォルダ
tk.Label(root, text="入力フォルダ:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
input_folder_var = tk.StringVar()
tk.Entry(root, textvariable=input_folder_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="参照", command=browse_input_folder).grid(row=0, column=2, padx=5, pady=5)

# 出力フォルダ
tk.Label(root, text="出力フォルダ:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
output_folder_var = tk.StringVar()
tk.Entry(root, textvariable=output_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="参照", command=browse_output_folder).grid(row=1, column=2, padx=5, pady=5)

# 日付フォーマット
tk.Label(root, text="日付フォーマット:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
date_format_var = tk.StringVar(value="%Y-%m-%d")
date_format_dropdown = tk.OptionMenu(root, date_format_var, "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y")
date_format_dropdown.grid(row=2, column=1, padx=5, pady=5)

# 実行ボタン
tk.Button(root, text="実行", command=execute_sorting).grid(row=3, column=0, columnspan=3, pady=10)

# メインループの開始
root.mainloop()