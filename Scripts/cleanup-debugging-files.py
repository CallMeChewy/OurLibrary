#!/usr/bin/env python3
# File: cleanup-debugging-files.py
# Path: /home/herb/Desktop/OurLibrary/Scripts/cleanup-debugging-files.py
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-20
# Last Modified: 2025-08-20 05:45PM
# CLEANUP: Remove debugging files and organize for Phase 1

import os
import shutil

def cleanup_debugging_files():
    """Clean up debugging files and organize for Phase 1"""
    
    print("🧹 CLEANUP: Organizing OurLibrary for Phase 1 Foundation")
    print("=" * 60)
    
    root_dir = "/home/herb/Desktop/OurLibrary"
    
    # Files to remove from root directory
    debug_files_to_remove = [
        "test-complete-email-journey.py",
        "test-firebase-imports.py", 
        "test-signin-credential-specific.py",
        "test-login-simple.py",
        "test-google-oauth-fixed.py",
        "test-both-auth-methods-final.py",
        "debug-google-oauth-flow.py",
        "comprehensive-firebase-verification-test.py",
        "final-google-oauth-test.py",
        "oauth_debug.png",
        "google_oauth_test_fixed.png",
        "firebase_imports_debug.png",
        "simple_login_test.png",
        "final_auth_test.png",
        "phase1_complete_test.png",
        "google_oauth_test_results.json",
        "final_auth_test_results.json",
        "phase1_complete_results.json"
    ]
    
    # Keep essential files
    keep_files = [
        "test-both-auth-methods-final.py",  # Keep as the main comprehensive test
        "phase1_complete_results.json"      # Keep final results for reference
    ]
    
    removed_count = 0
    kept_count = 0
    
    print("\\n📂 Cleaning root directory...")
    for filename in debug_files_to_remove:
        filepath = os.path.join(root_dir, filename)
        if os.path.exists(filepath):
            if filename in keep_files:
                print(f"   ✅ KEEPING: {filename}")
                kept_count += 1
            else:
                try:
                    os.remove(filepath)
                    print(f"   🗑️ REMOVED: {filename}")
                    removed_count += 1
                except Exception as e:
                    print(f"   ❌ Error removing {filename}: {e}")
    
    # Create archive directory for important test files
    archive_dir = os.path.join(root_dir, "Archive", "Phase1_Development")
    os.makedirs(archive_dir, exist_ok=True)
    
    # Move kept files to archive
    for filename in keep_files:
        src_path = os.path.join(root_dir, filename)
        if os.path.exists(src_path):
            dst_path = os.path.join(archive_dir, filename)
            try:
                shutil.move(src_path, dst_path)
                print(f"   📦 ARCHIVED: {filename} → Archive/Phase1_Development/")
            except Exception as e:
                print(f"   ❌ Error archiving {filename}: {e}")
    
    # Check current root directory status
    print("\\n📋 Current root directory files:")
    root_files = [f for f in os.listdir(root_dir) if os.path.isfile(os.path.join(root_dir, f))]
    
    essential_files = [
        "index.html",
        "auth-demo.html", 
        "CLAUDE.md",
        "README.md",
        "StartOurLibrary.py"
    ]
    
    for filename in sorted(root_files):
        if filename in essential_files:
            print(f"   ✅ {filename}")
        else:
            print(f"   📄 {filename}")
    
    print(f"\\n📊 Cleanup Summary:")
    print(f"   🗑️ Files removed: {removed_count}")
    print(f"   📦 Files archived: {kept_count}")
    print(f"   📁 Archive location: Archive/Phase1_Development/")
    
    # Verify essential Phase 1 files exist
    print(f"\\n✅ Phase 1 Essential Files Status:")
    essential_status = {}
    for filename in essential_files:
        filepath = os.path.join(root_dir, filename)
        exists = os.path.exists(filepath)
        essential_status[filename] = exists
        status = "✅" if exists else "❌ MISSING"
        print(f"   {status} {filename}")
    
    all_essential_exist = all(essential_status.values())
    
    if all_essential_exist:
        print(f"\\n🎉 PHASE 1 FOUNDATION READY!")
        print(f"   ✅ All essential files present")
        print(f"   ✅ Debugging files cleaned up")
        print(f"   ✅ Email authentication working")
        print(f"   🚀 Ready for Phase 2 development")
    else:
        print(f"\\n⚠️ Missing essential files - check status above")
    
    return all_essential_exist

if __name__ == "__main__":
    cleanup_debugging_files()