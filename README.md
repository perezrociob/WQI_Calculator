# 💧 WQI Calculator (Water Quality Index)

![Development Status](https://img.shields.io/badge/Status-Work_in_Progress-yellow)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![GUI](https://img.shields.io/badge/Interface-PyQt5-green)

[![DOI](https://zenodo.org/badge/1154548825.svg)](https://doi.org/10.5281/zenodo.18598741)

A desktop application designed to automate the calculation, analysis, and visualization of Water Quality Indices based on physicochemical parameters. 

**⚠️ Note: This project is currently under active development. Features and code structure are subject to change.**

## 📋 Overview

This tool allows researchers and students to process laboratory water sample data efficiently. It calculates specific indices to determine water suitability for different uses  and provides immediate visual feedback.

### Key Features

* **Data Import:** Support for `.csv` and `.xlsx` files containing water sample data.
* **Automatic Index Calculation:**
    * **IWQI (Irrigation Water Quality Index):** Evaluates water suitability for agricultural use based on parameters like EC, SAR, Na+, Cl-, and HCO3-.
    * **DWQI (Drinking Water Quality Index):** Evaluates water suitability for human consumption based on WHO standards (WIP).
    * **LWQI
* **Dynamic Visualization:**
    * Time-series/Sample plots using **Matplotlib**.
    * Color-coded background zones representing quality categories (e.g., Excellent, Good, Poor).
    * Secondary axis support for comparing individual parameters against the index.
    * Percentage distribution bar charts for quick statistical summary.
* **User-Friendly Interface:** Clean GUI built with **PyQt5** featuring interactive tables and easy configuration.

## 🛠️ Tech Stack

* **Language:** Python 3
* **GUI Framework:** PyQt5 (Qt Designer)
* **Data Analysis:** Pandas, NumPy
* **Plotting:** Matplotlib

## 🚀 Installation & Usage

### Prerequisites
Ensure you have Python 3.8+ installed.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/REPO_NAME.git](https://github.com/YOUR_USERNAME/REPO_NAME.git)
    cd REPO_NAME
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python main.py
    ```

## 📂 Project Structure

* `main.py`: Entry point of the application and main logic.
* `uiWQI.py`: GUI definition (generated from Qt Designer).
* `index_calc.py`: Mathematical logic and algorithms for IWQI and DWQI calculations.
* `plotmodules.py`: Custom Matplotlib canvas classes for plotting and interaction.
* `config.py`: Configuration file for parameters, weights, and standard limits.

## 🤝 Contributing

Contributions are welcome! Since this is a work in progress, please open an issue first to discuss what you would like to change.

## ✒️ Author

* **Ing. Rocío Belén Pérez** - *Initial Work & Development*

---
