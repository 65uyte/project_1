from text_editor.ui.editor_window import EditorWindow
import tkinter as tk

def main():
    root = tk.Tk()
    app = EditorWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main() 