# CHDMAN GUI Converter

A lightweight, user-friendly Windows graphical interface for `chdman.exe` designed to seamlessly convert `.cue` disc images to `.chd` compressed archives and extract them back.

---

## Prerequisites

Before running the program, ensure you have the core utility file ready:
1. Obtain **`chdman.exe`** (typically bundled with tools from [MAME](https://www.mamedev.org/)).
2. Place **`chdman.exe`** in the **exact same directory** as the program executable (`chdman_gui.exe`).

---

## Build Tool

This program was developed using [Python](https://www.python.org/).

---

## How to Use

1. Launch **`chdman_gui.exe`**.
2. **Select Working Mode:**
   * **`.cue to .chd (Create CHD)`**: Compresses a standard CUE/BIN disc image into a single CHD file.
   * **`.chd to .cue (Extract CHD)`**: Extracts a CHD file back into a CUE and its corresponding track files.
3. **Choose Processing Option:**
   * **Single File**: Selects one individual file to process.
   * **Batch Directory**: Processes all supported files found within a chosen folder.
4. **Set Paths:**
   * Click **Browse...** next to **Input** to choose your source file or folder.
   * Click **Browse...** next to **Output Dir** to choose where converted files will be saved *(leave blank or it will default to the source directory)*.
5. **Start Conversion:**
   * Click **Start Converting**. The progress bar will track real-time completion status directly from `chdman`.
6. **Post-Conversion:**
   * Click **Open Output Folder** to quickly access your freshly converted files.

---

## License

This project is open-source and licensed under the [MIT License](LICENSE).
