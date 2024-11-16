import os

def collect_code(base_dir, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write("Project Directory Structure and Files\n")
        outfile.write("="*50 + "\n\n")
        for root, dirs, files in os.walk(base_dir):
            # Exclude hidden directories and files (like .git, __pycache__, etc.)
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files = [f for f in files if not f.startswith('.') and f != os.path.basename(__file__)]
            # Generate the relative path
            rel_dir = os.path.relpath(root, base_dir)
            if rel_dir == '.':
                rel_dir = ''
            # Write directory name
            outfile.write(f"Directory: {rel_dir}\n")
            outfile.write("-"*50 + "\n")
            for file in files:
                file_path = os.path.join(root, file)
                # Read file content
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                except Exception as e:
                    content = f"Could not read file due to error: {e}"
                # Write file name and content
                outfile.write(f"File: {file}\n")
                outfile.write("-"*20 + "\n")
                outfile.write(content)
                outfile.write("\n" + "-"*20 + "\n\n")
            outfile.write("\n")
        print(f"All code has been collected into '{output_file}'.")

if __name__ == "__main__":
    # Set the base directory as the current directory
    base_directory = os.getcwd()
    # Output file name
    output_filename = "all_code.txt"
    collect_code(base_directory, output_filename)
