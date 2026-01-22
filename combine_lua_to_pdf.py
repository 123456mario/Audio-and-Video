import os
import glob
import subprocess
import shutil

# Configuration
TARGET_DIR = "/Users/gimdongseong/Desktop/제어/시리카 test"
TEMP_MD_FILE = "temp_combined_scripts.md"
OUTPUT_PDF_FILE = "all_lua_scripts.pdf"

def combine_and_convert():
    # 1. Gather all Lua files
    lua_pattern = os.path.join(TARGET_DIR, "*.lua")
    lua_files = sorted(glob.glob(lua_pattern))
    
    if not lua_files:
        print(f"No .lua files found in {TARGET_DIR}")
        return

    print(f"Found {len(lua_files)} Lua files. Combining...")

    # 2. specific path for temp md file (in the target dir to avoid path issues)
    temp_md_path = os.path.join(TARGET_DIR, TEMP_MD_FILE)
    
    # 3. Generate Markdown content
    with open(temp_md_path, 'w', encoding='utf-8') as outfile:
        outfile.write("# Combined Xilica Lua Scripts\n\n")
        outfile.write(f"**Source Directory**: `{TARGET_DIR}`\n\n")
        outfile.write("---\n\n")
        
        # Table of Contents
        outfile.write("## Table of Contents\n\n")
        for fpath in lua_files:
            fname = os.path.basename(fpath)
            link_name = fname.replace('.', '').replace(' ', '-').lower() 
            # Simple list is safer than trying to guess MD anchor links which vary by parser
            outfile.write(f"- {fname}\n")
        
        outfile.write("\n---\n\n")

        # Content
        for fpath in lua_files:
            fname = os.path.basename(fpath)
            outfile.write(f"## {fname}\n\n")
            outfile.write("```lua\n")
            
            try:
                with open(fpath, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)
            except Exception as e:
                outfile.write(f"-- Error reading file: {e}")
                
            outfile.write("\n```\n\n")
            outfile.write("---\n\n")

    # 4. Convert to PDF using md-to-pdf
    print(f"Created Markdown at {temp_md_path}. Converting to PDF...")
    
    cmd = ['npx', '-y', 'md-to-pdf', temp_md_path]
    
    try:
        subprocess.run(cmd, check=True)
        print("Conversion successful.")
        
        # md-to-pdf outputs to the same filename but with .pdf extension
        generated_pdf = temp_md_path.replace('.md', '.pdf')
        final_pdf_path = os.path.join(TARGET_DIR, OUTPUT_PDF_FILE)
        
        if os.path.exists(generated_pdf):
            # Rename/Move to final desired name
            if os.path.exists(final_pdf_path):
                os.remove(final_pdf_path)
            os.rename(generated_pdf, final_pdf_path)
            print(f"PDF saved to: {final_pdf_path}")
        else:
            print(f"Error: Expected PDF {generated_pdf} was not created.")

    except subprocess.CalledProcessError as e:
        print(f"Error during PDF conversion: {e}")
    finally:
        # 5. Cleanup temp markdown
        if os.path.exists(temp_md_path):
            os.remove(temp_md_path)
            print("Cleaned up temporary markdown file.")

if __name__ == "__main__":
    combine_and_convert()
