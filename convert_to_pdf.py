import os
import subprocess
import glob
import shutil

# Configuration
SOURCE_GUIDES_DIR = 'attach'
SOURCE_EXERCISES_DIR = 'attach/exercises'
OUTPUT_DIR = 'attach/course_pdf'

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_md_to_pdf(input_path, final_output_path):
    """Runs npx md-to-pdf to convert input file, then moves it to output path."""
    # md-to-pdf creates output in same dir with .pdf extension
    expected_output = input_path.replace('.md', '.pdf')
    
    cmd = ['npx', '-y', 'md-to-pdf', input_path]
    try:
        print(f"Converting {input_path}...")
        subprocess.run(cmd, check=True)
        
        # Move to final destination
        if os.path.exists(expected_output):
            print(f"Moving {expected_output} -> {final_output_path}")
            shutil.move(expected_output, final_output_path)
        else:
            print(f"Error: Expected output file {expected_output} not found.")
            
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_path}: {e}")

def convert_guides():
    """Converts markdown guides in SOURCE_GUIDES_DIR to PDF."""
    md_files = glob.glob(os.path.join(SOURCE_GUIDES_DIR, '*.md'))
    
    for md_file in md_files:
        filename = os.path.basename(md_file)
        if filename.startswith('temp_') or filename == 'implementation_plan.md':
            continue

        output_filename = filename.replace('.md', '.pdf')
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        run_md_to_pdf(md_file, output_path)

def convert_exercises():
    """Converts Lua exercises to PDF by wrapping them in Markdown."""
    lua_files = glob.glob(os.path.join(SOURCE_EXERCISES_DIR, '*.lua'))
    
    for lua_file in lua_files:
        filename = os.path.basename(lua_file)
        temp_md_content = f"# {filename}\n\n```lua\n"
        
        with open(lua_file, 'r', encoding='utf-8') as f:
            temp_md_content += f.read()
            
        temp_md_content += "\n```\n"
        
        # Save temp md in the SAME directory as source (so md-to-pdf finds it easily)
        temp_md_path = os.path.join(SOURCE_EXERCISES_DIR, f"temp_{filename}.md")
        
        with open(temp_md_path, 'w', encoding='utf-8') as f:
            f.write(temp_md_content)
            
        output_filename = filename.replace('.lua', '.pdf')
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        try:
            run_md_to_pdf(temp_md_path, output_path)
        finally:
            # Clean up temp md file
            if os.path.exists(temp_md_path):
                os.remove(temp_md_path)

if __name__ == "__main__":
    print("Starting PDF conversion task...")
    
    print("\n--- Converting Guides ---")
    convert_guides()
    
    print("\n--- Converting Exercises ---")
    convert_exercises()
    
    print("\nAll tasks completed.")
