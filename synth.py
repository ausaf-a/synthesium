#!/usr/bin/env python3
"""
Synthesium Video Generator
Main orchestrator for creating narrative-driven videos from scripts.
"""

import os
import sys
import time
import argparse
from datetime import datetime
from config.settings import settings
from services.openai_service import OpenAIService
from video.composer import VideoComposer
from video.utils import ensure_directory, cleanup_directory, validate_script, get_file_size_mb

def create_video(script, output_filename=None, cleanup_temp=True, character_config=None, episode_dir=None):
    """
    Create a video from a script.
    
    Args:
        script: List of scene dictionaries with 'sceneDescription' and 'voiceoverText'
        output_filename: Optional custom filename for output video
        cleanup_temp: Whether to clean up temporary files after completion
        character_config: Optional character configuration for channel-based generation
        episode_dir: Optional episode directory to use instead of temp
        
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
    
    # Use episode directory if provided, otherwise temp
    if episode_dir:
        work_dir = episode_dir
        print(f"📁 Using episode directory: {work_dir}")
    else:
        work_dir = ensure_directory(settings.TEMP_DIR)
        print(f"📁 Using temp directory: {work_dir}")
    
    # Generate output filename if not provided
    if not output_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"synthesium_video_{timestamp}.mp4"
        output_path = os.path.join(output_dir, output_filename)
    else:
        # If episode_dir is provided, save to episode directory
        if episode_dir:
            output_path = os.path.join(episode_dir, output_filename)
        else:
            # If output_filename is provided but no episode_dir, use normal output logic
            if os.path.isabs(output_filename):
                output_path = output_filename
            else:
                output_path = os.path.join(output_dir, output_filename)
    
    try:
        print("🎬 Starting Synthesium Video Generation")
        print(f"📝 Script has {len(script)} scenes")
        print(f"🎯 Output: {output_path}")
        print(f"🔍 Debug - output_path is absolute: {os.path.isabs(output_path)}")
        print(f"🔍 Debug - output_path parent exists: {os.path.exists(os.path.dirname(output_path))}")
        
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(f"🔍 Debug - Created parent directory: {os.path.dirname(output_path)}")
        
        print("-" * 50)
        
        start_time = time.time()
        
        # Initialize services
        openai_service = OpenAIService()
        video_composer = VideoComposer()
        
        # Generate assets for each scene
        scene_assets_list = []
        
        for i, scene in enumerate(script):
            print(f"\n📹 Processing Scene {i+1}/{len(script)}")
            scene_assets = openai_service.generate_scene_assets(scene, i, work_dir, character_config)
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
        # Cleanup temporary files (only if using temp directory)
        if cleanup_temp and not episode_dir:
            print(f"\n🧹 Cleaning up temporary files...")
            cleanup_directory(work_dir)
        elif episode_dir:
            print(f"\n💾 Assets preserved in episode directory: {episode_dir}")

def main():
    """Main function with example script."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate narrative videos with AI')
    parser.add_argument('--regenerate-images', action='store_true', help='Force regenerate all images')
    parser.add_argument('--regenerate-audio', action='store_true', help='Force regenerate all audio')
    parser.add_argument('--regenerate-all', action='store_true', help='Force regenerate everything')
    parser.add_argument('--clear-cache', choices=['images', 'audio', 'whisper', 'all'], help='Clear cache')
    parser.add_argument('--cache-stats', action='store_true', help='Show cache statistics')
    parser.add_argument('--music-info', action='store_true', help='Show background music information')
    parser.add_argument('--channel', type=str, help='Generate video for specific channel')
    parser.add_argument('--list-channels', action='store_true', help='List available channels')
    parser.add_argument('--channel-stats', type=str, help='Show stats for specific channel')
    args = parser.parse_args()
    
    # Handle cache clearing
    if args.clear_cache:
        from services.cache_manager import CacheManager
        cache_manager = CacheManager()
        cache_manager.clear_cache(args.clear_cache)
        return 0
    
    # Handle cache stats
    if args.cache_stats:
        from services.cache_manager import CacheManager
        cache_manager = CacheManager()
        stats = cache_manager.get_cache_stats()
        print("\n📊 Cache Statistics:")
        print(f"Images cached: {stats['images_cached']}")
        print(f"Audio cached: {stats['audio_cached']}")
        print(f"Whisper timings cached: {stats['whisper_cached']}")
        print(f"Cache enabled: {stats['cache_enabled']}")
        return 0
    
    # Handle music info
    if args.music_info:
        from services.audio_manager import AudioManager
        audio_manager = AudioManager()
        info = audio_manager.get_music_info()
        print("\n🎵 Background Music Information:")
        print(f"Music enabled: {info['enabled']}")
        print(f"Tracks available: {info['tracks_available']}")
        print(f"Music volume: {info['music_volume']}")
        print(f"Voiceover volume: {info['voiceover_volume']}")
        print(f"Music directory: {info['music_directory']}")
        if info['track_list']:
            print("Available tracks:")
            for i, track in enumerate(info['track_list'], 1):
                print(f"  {i}. {track}")
        else:
            audio_manager.add_sample_tracks()
        return 0
    
    # Handle channel listing
    if args.list_channels:
        from services.channel_manager import ChannelManager
        channel_manager = ChannelManager()
        channels = channel_manager.get_available_channels()
        print("\n📺 Available Channels:")
        for channel_id, info in channels.items():
            print(f"\n🎬 {info['name']} ({channel_id})")
            print(f"   Description: {info['description']}")
            print(f"   Type: {info['type']}")
            print(f"   Episodes generated: {info['episode_count'] - 1}")
        print("\n💡 Usage: python synth.py --channel <channel_id>")
        return 0
    
    # Handle channel stats
    if args.channel_stats:
        from services.channel_manager import ChannelManager
        channel_manager = ChannelManager()
        stats = channel_manager.get_channel_stats(args.channel_stats)
        if 'error' in stats:
            print(f"❌ {stats['error']}")
        else:
            print(f"\n📊 {stats['name']} Statistics:")
            print(f"Description: {stats['description']}")
            print(f"Type: {stats['type']}")
            print(f"Episodes generated: {stats['episodes_generated']}")
            print(f"Topics used: {stats['topics_used']}/{stats['available_topics']}")
            if stats['recent_topics']:
                print(f"Recent topics: {', '.join(stats['recent_topics'])}")
        return 0
    
    # Override settings based on arguments
    if args.regenerate_images or args.regenerate_all:
        settings.FORCE_REGENERATE_IMAGES = True
        print("🔄 Force regenerating images")
    
    if args.regenerate_audio or args.regenerate_all:
        settings.FORCE_REGENERATE_AUDIO = True
        print("🔄 Force regenerating audio")
    
    # Generate script based on mode (channel vs manual)
    episode_info = None
    character_config = None
    
    if args.channel:
        # Channel-based generation
        from services.channel_manager import ChannelManager
        channel_manager = ChannelManager()
        
        print(f"🎬 Generating episode for channel: {args.channel}")
        episode_data = channel_manager.generate_episode_script(args.channel)
        
        script = episode_data["script"]
        character_config = episode_data["character"]
        episode_info = episode_data
        
        if episode_data.get("is_resume"):
            print(f"🔄 Resuming Episode {episode_data['episode_number']}: {episode_data['topic']}")
        else:
            print(f"🎵 Episode {episode_data['episode_number']}: {episode_data['topic']}")
            
        print(f"📝 Generated {len(script)} scenes")
        
    else:
        # Manual script (original behavior)
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
        if args.channel:
            # For channel-based generation, use episode directory for assets
            episode_dir = episode_info["video_dir"]
            output_filename = f"episode_{episode_info['video_number']}.mp4"
            
            # Pass the episode directory and filename separately
            # Don't construct the full path here - let create_video handle it
            video_path = create_video(script, output_filename=output_filename, cleanup_temp=False, character_config=character_config, episode_dir=episode_dir)
        else:
            video_path = create_video(script, character_config=character_config)
            
        print(f"\n🎉 Success! Your video is ready: {video_path}")
        
    except Exception as e:
        print(f"\n💥 Failed to create video: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
