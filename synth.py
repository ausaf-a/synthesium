#!/usr/bin/env python3
"""
Synthesium Video Generator
Main orchestrator for creating narrative-driven videos from scripts.
"""

import os
import time
from datetime import datetime
from config.settings import settings
from services.openai_service import OpenAIService
from video.composer import VideoComposer
from video.utils import ensure_directory, cleanup_directory, validate_script, get_file_size_mb

def create_video(script, output_filename=None, cleanup_temp=True):
    """
    Create a video from a script.
    
    Args:
        script: List of scene dictionaries with 'sceneDescription' and 'voiceoverText'
        output_filename: Optional custom filename for output video
        cleanup_temp: Whether to clean up temporary files after completion
    
    Returns:
        Path to the generated video file
    """
    
    # Validate configuration
    settings.validate()
    
    # Validate script
    if not validate_script(script):
        raise ValueError("Invalid script format")
    
    # Setup directories
    output_dir = ensure_directory(settings.OUTPUT_DIR)
    temp_dir = ensure_directory(settings.TEMP_DIR)
    
    # Generate output filename if not provided
    if not output_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"synthesium_video_{timestamp}.mp4"
    
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        print("🎬 Starting Synthesium Video Generation")
        print(f"📝 Script has {len(script)} scenes")
        print(f"🎯 Output: {output_path}")
        print("-" * 50)
        
        start_time = time.time()
        
        # Initialize services
        openai_service = OpenAIService()
        video_composer = VideoComposer()
        
        # Generate assets for each scene
        scene_assets_list = []
        for i, scene in enumerate(script):
            print(f"\n📹 Processing Scene {i+1}/{len(script)}")
            scene_assets = openai_service.generate_scene_assets(scene, i, temp_dir)
            scene_assets_list.append(scene_assets)
        
        # Create the final video
        print(f"\n🎞️ Assembling final video...")
        final_video_path = video_composer.create_video(scene_assets_list, output_path)
        
        # Get video info
        video_info = video_composer.get_video_info(final_video_path)
        file_size = get_file_size_mb(final_video_path)
        
        # Calculate generation time
        total_time = time.time() - start_time
        
        # Print summary
        print("\n" + "="*50)
        print("✅ VIDEO GENERATION COMPLETE!")
        print("="*50)
        print(f"📁 Output File: {final_video_path}")
        print(f"⏱️  Duration: {video_info.get('duration', 0):.1f} seconds")
        print(f"📏 Resolution: {video_info.get('size', 'Unknown')}")
        print(f"💾 File Size: {file_size:.1f} MB")
        print(f"🕐 Generation Time: {total_time:.1f} seconds")
        print(f"⚡ Speed: {video_info.get('duration', 0)/total_time:.2f}x realtime" if total_time > 0 else "")
        
        return final_video_path
        
    except Exception as e:
        print(f"\n❌ Error during video generation: {e}")
        raise
    
    finally:
        # Cleanup temporary files
        if cleanup_temp:
            print(f"\n🧹 Cleaning up temporary files...")
            cleanup_directory(temp_dir)

def main():
    """Main function with example script."""
    
    # Example script from PRD
    script = [
        {
            "sceneDescription": "A lonely robot sits on a rooftop watching the city lights.",
            "voiceoverText": "He was built to serve, but all he wanted was to feel."
        },
        {
            "sceneDescription": "Raindrops fall on his metal shell as neon signs flicker below.",
            "voiceoverText": "The city pulsed with life—something he could never truly grasp."
        },
        {
            "sceneDescription": "He watches a couple sharing an umbrella across the street.",
            "voiceoverText": "Love, warmth, connection—it all seemed so distant."
        },
        {
            "sceneDescription": "A small cat curls up beside him, purring softly.",
            "voiceoverText": "And yet, in that moment, something stirred within him."
        },
        {
            "sceneDescription": "The robot gently pets the cat as the rain continues to fall.",
            "voiceoverText": "Maybe feeling wasn't programmed—but maybe it didn't need to be."
        }
    ]
    
    try:
        video_path = create_video(script)
        print(f"\n🎉 Success! Your video is ready: {video_path}")
        
    except Exception as e:
        print(f"\n💥 Failed to create video: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
