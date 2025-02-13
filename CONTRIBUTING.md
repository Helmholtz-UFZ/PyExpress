# Contributing to PyExpress

Thank you for your interest in contributing to **PyExpress**!
We welcome contributions from the community. Whether it's fixing bugs, 
adding new features, or improving documentation, your help is always appreciated.

To ensure a smooth collaboration, please read and follow these guidelines.

# Code Conventions

To maintain readability and consistency in the codebase, we follow the following conventions:

## 1. Class Names
- Use **CamelCase** for class names.
  - Example: `MyClass`, `DataProcessor`, `ImageAnalyzer`
 
## 2. Function and Method Names
- Use **snake_case** for class names.
  - Example: process_image(), load_data(), calculate_metrics()

## 3. Variable and Argument Names
- Use snake_case for variable and argument names.
  - Example: input_file, image_path, data_frame

## 4. Clarity and Precision
- Always choose clear, precise, and concise names.
  - Prefer descriptive names over generic ones. For example:
    - Good: source_path (clear indication of the role of the variable)
    - Bad: _path_tp_your_directory (too vague, not immediately clear)

## 5. Avoid Abbreviations
- Avoid abbreviations unless they are well known and widely used in the context of the project.
  - Good: file_path, image_data
  - Bad: fp, img_data (too ambiguous)

## 6. Docstrings
- Use docstrings to describe the purpose of functions, classes, and methods.
- Keep docstrings concise, but ensure they explain the key purpose and parameters.

## 7. Consistency
- Be consistent in applying naming conventions and formatting rules throughout the codebase.

## Issues
If you encounter any problems or have ideas for improvements, feel free to open an issue in the repository. 
We appreciate your contributions to making PyExpress better!

# How to Contribute

## Repository Structure

- `master` - branch:
  + Stable and usually protected
  + Regular merges from `develop`
- `develop` - branch:
  + The main development branch, no hard stability requirements/guarantees
  + Merges into `develop` should follow the following workflow

## 1. Reporting Issues
If you encounter a bug or have a suggestion for improvement, 
please open an issue in the GitHub repository. Make sure to provide:
- A clear description of the issue or feature request.
- Steps to reproduce (for bugs).
- Any relevant screenshots or logs.

## 2. Submitting Code
To contribute code, please follow these steps:

### 2.1. **Fork the repository**:
- Click the "Fork" button in the top-right corner of the GitHub repository to create your own copy of the project.

### 2.2. **Clone your fork**:
- open a console / bash
- git clone https://github.com/your-username/PyExpress.git
- cd PyExpress

### 2.3. **Create a new feature branch**:
- git checkout -b feature-branch-name

### 2.4. **Make your changes and commit**:
- git add .
- git commit -m "Brief description of changes"

### 2.5. **Push your branch to your fork**:
- git push origin feature-branch-name

### 2.6. **Create a Pull Request**:
- Go to your fork on GitHub and click "Compare & Pull Request".
- Provide a description of the changes and submit the PR.

### 2.7. **Code review**:
- A core developer will review your PR. If any changes are required, update your branch and push them.

### 2.8. **Merge procedure**:
- Once approved, your PR will be merged into the main branch.