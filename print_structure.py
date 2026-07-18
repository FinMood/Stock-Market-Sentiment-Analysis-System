import os

def print_tree(startpath):
    # 設定需要忽略的資料夾（避免輸出虛擬環境等大量無關檔案）
    exclude_dirs = {'.venv', '.git', '__pycache__', '.vscode'}
    
    print("======= 專案目前根目錄與腳本結構 =======")
    for root, dirs, files in os.walk(startpath):
        # 過濾掉不需要顯示的隱藏或虛擬環境資料夾
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # 計算目前目錄的深度
        level = root.replace(startpath, '').count(os.sep)
        indent = '│   ' * (level)
        
        # 印出目前資料夾名稱
        if root == startpath:
            print(f"Stock-Market-Sentiment-Analysis-System/ (根目錄)")
        else:
            print(f"{indent}├── {os.path.basename(root)}/")
            
        # 印出該資料夾底下的檔案
        sub_indent = '│   ' * (level + 1)
        for f in sorted(files):
            # 忽略臨時診斷腳本與系統暫存檔
            if f not in {'check_db.py', '.DS_Store'} and not f.endswith('.pyc'):
                print(f"{sub_indent}├── {f}")

if __name__ == "__main__":
    # 取得目前執行的根目錄路徑
    current_dir = os.getcwd()
    print_tree(current_dir)