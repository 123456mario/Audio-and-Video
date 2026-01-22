from PIL import Image
import sys
from collections import deque

def flood_fill_remove_bg(input_path, output_path, tolerance=30):
    try:
        img = Image.open(input_path).convert("RGBA")
        width, height = img.size
        pixels = img.load()
        
        # Visited mask
        visited = set()
        queue = deque()
        
        # Start from corners
        starts = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]
        
        for start in starts:
            if start not in visited:
                # Check if corner is dark enough to be background
                r, g, b, a = pixels[start]
                if r < tolerance and g < tolerance and b < tolerance:
                    queue.append(start)
                    visited.add(start)
        
        # BFS
        while queue:
            x, y = queue.popleft()
            
            # Set to transparent
            pixels[x, y] = (0, 0, 0, 0)
            
            # Check neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                
                if 0 <= nx < width and 0 <= ny < height:
                    if (nx, ny) not in visited:
                        r, g, b, a = pixels[nx, ny]
                        if r < tolerance and g < tolerance and b < tolerance:
                            visited.add((nx, ny))
                            queue.append((nx, ny))
                            
        img.save(output_path, "PNG")
        print(f"Smart-processed {output_path}")
        
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        flood_fill_remove_bg(sys.argv[1], sys.argv[2])
