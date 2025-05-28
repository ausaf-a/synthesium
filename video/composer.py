import os
from moviepy.editor import *
from config.settings import settings
from typing import List, Dict

class VideoComposer:
    def __init__(self):
        self.fps = settings.VIDEO_FPS
        self.width = settings.VIDEO_WIDTH
        self.height = settings.VIDEO_HEIGHT
    
    def create_scene_clip(self, scene_assets: Dict) -> VideoClip:
        """
        Create a video clip from scene assets (image + audio).
        
        Args:
            scene_assets: Dictionary containing image_path, audio_path, etc.
            
        Returns:
            VideoClip object for the scene
        """
        try:
            # Load audio to determine clip duration
            audio_clip = AudioFileClip(scene_assets['audio_path'])
            duration = audio_clip.duration
            
            # Load and resize image
            image_clip = (ImageClip(scene_assets['image_path'])
                         .set_duration(duration)
                         .resize((self.width, self.height)))
            
            # Combine image and audio
            scene_clip = image_clip.set_audio(audio_clip)
            
            print(f"Created scene clip - Duration: {duration:.2f}s")
            return scene_clip
            
        except Exception as e:
            print(f"Error creating scene clip: {e}")
            raise
    
    def create_video(self, scene_assets_list: List[Dict], output_path: str) -> str:
        """
        Create final video by combining all scene clips.
        
        Args:
            scene_assets_list: List of scene asset dictionaries
            output_path: Path where the final video will be saved
            
        Returns:
            Path to the saved video file
        """
        try:
            print(f"Creating video with {len(scene_assets_list)} scenes...")
            
            # Create clips for each scene
            clips = []
            for i, scene_assets in enumerate(scene_assets_list):
                print(f"Processing scene {i+1}/{len(scene_assets_list)}")
                clip = self.create_scene_clip(scene_assets)
                clips.append(clip)
            
            # Concatenate all clips
            if len(clips) == 1:
                final_video = clips[0]
            else:
                final_video = concatenate_videoclips(clips, method="compose")
            
            # Write the final video
            print(f"Rendering final video to: {output_path}")
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Clean up clips
            for clip in clips:
                clip.close()
            final_video.close()
            
            print(f"Video saved successfully: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error creating video: {e}")
            raise
    
    def get_video_info(self, video_path: str) -> Dict:
        """
        Get information about the generated video.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary with video information
        """
        try:
            clip = VideoFileClip(video_path)
            info = {
                'duration': clip.duration,
                'fps': clip.fps,
                'size': clip.size,
                'format': 'mp4'
            }
            clip.close()
            return info
        except Exception as e:
            print(f"Error getting video info: {e}")
            return {}
