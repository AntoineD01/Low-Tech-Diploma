# Script to ensure frontend is built before running the app

import os
import subprocess
import sys

def build_frontend():
    """Build the React frontend if dist/ doesn't exist"""
    
    # Get the root directory (parent of scripts/)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dist_path = os.path.join(root_dir, 'dist')
    
    # Check if dist exists and has files
    if os.path.exists(dist_path) and os.listdir(dist_path):
        print("✅ Frontend already built (dist/ exists)")
        return True
    
    print("🏗️  Building React frontend...")
    
    # Change to root directory
    os.chdir(root_dir)
    
    # Check if node_modules exists
    node_modules_path = os.path.join(root_dir, 'node_modules')
    if not os.path.exists(node_modules_path):
        print("📦 Installing Node.js dependencies...")
        try:
            subprocess.run(['npm', 'install'], check=True, cwd=root_dir)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    # Build the frontend
    try:
        subprocess.run(['npm', 'run', 'build'], check=True, cwd=root_dir)
        print("✅ Frontend built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build frontend: {e}")
        return False
    except FileNotFoundError:
        print("⚠️  npm not found - skipping frontend build")
        print("   The app will run in API-only mode")
        return False

if __name__ == "__main__":
    success = build_frontend()
    sys.exit(0 if success else 1)
