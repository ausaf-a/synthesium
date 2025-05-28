import os
import random
from moviepy.editor import *
from config.settings import settings
from services.caption_service import CaptionService
from typing import List, Dict

class VideoComposer:
    def __init__(self):
        self.fps = settings.VIDEO_FPS
        self.width = settings.VIDEO_WIDTH
        self.height = settings.VIDEO_HEIGHT
        self.enable_movement = settings.ENABLE_CAMERA_MOVEMENT
        self.zoom_intensity = settings.ZOOM_INTENSITY
        self.pan_intensity = settings.PAN_INTENSITY
        self.caption_service = CaptionService()
    
    def apply_camera_movement(self, image_clip: ImageClip, duration: float) -> VideoClip:
        """
        Apply Ken Burns effect (zoom and pan) to an image clip.
        
        Args:
            image_clip: The image clip to apply movement to
            duration: Duration of the clip in seconds
            
        Returns:
            VideoClip with camera movement applied
        """
        if not self.enable_movement:
            return image_clip
        
        # Choose random movement type
        movement_types = ['zoom_in', 'zoom_out', 'pan_left', 'pan_right', 'zoom_in_pan']
        movement = random.choice(movement_types)
        
        # Ensure image is properly sized before applying movement
        base_clip = image_clip.resize(newsize=(self.width, self.height))
        
        # Calculate movement parameters
        zoom_factor = 1 + self.zoom_intensity
        pan_pixels = int(self.width * self.pan_intensity)
        
        def make_frame(t):
            # Normalize time (0 to 1)
            progress = t / duration
            
            if movement == 'zoom_in':
                # Start normal, zoom in over time
                current_zoom = 1 + (zoom_factor - 1) * progress
                return base_clip.resize(current_zoom).get_frame(t)
            
            elif movement == 'zoom_out':
                # Start zoomed in, zoom out over time
                current_zoom = zoom_factor - (zoom_factor - 1) * progress
                return base_clip.resize(current_zoom).get_frame(t)
            
            elif movement == 'pan_left':
                # Pan from right to left
                x_offset = pan_pixels * progress
                # Create larger canvas and crop to simulate panning
                expanded_clip = base_clip.resize((self.width + pan_pixels, self.height))
                return expanded_clip.crop(x1=x_offset, x2=x_offset + self.width).get_frame(t)
            
            elif movement == 'pan_right':
                # Pan from left to right  
                x_offset = pan_pixels * (1 - progress)
                # Create larger canvas and crop to simulate panning
                expanded_clip = base_clip.resize((self.width + pan_pixels, self.height))
                return expanded_clip.crop(x1=x_offset, x2=x_offset + self.width).get_frame(t)
            
            elif movement == 'zoom_in_pan':
                # Zoom in while panning slightly
                current_zoom = 1 + (zoom_factor - 1) * progress
                x_offset = (pan_pixels * 0.3) * progress  # Gentler pan when zooming
                zoomed_clip = base_clip.resize(current_zoom)
                if x_offset > 0:
                    expanded_clip = zoomed_clip.resize((self.width + int(pan_pixels * 0.3), self.height))
                    return expanded_clip.crop(x1=x_offset, x2=x_offset + self.width).get_frame(t)
                else:
                    return zoomed_clip.get_frame(t)
            
            # Fallback: no movement
            return base_clip.get_frame(t)
        
        # Create the animated clip
        animated_clip = VideoClip(make_frame, duration=duration).set_fps(self.fps)
        
        print(f"Applied camera movement: {movement}")
        return animated_clip
    
    def create_caption_clip(self, text: str, duration: float, whisper_timing: Dict = None) -> VideoClip:
        """
        Create a caption clip with single word pop animation using Whisper timing.
        
        Args:
            text: Text to be displayed as captions
            duration: Duration of the caption clip
            whisper_timing: Optional Whisper timing data
            
        Returns:
            VideoClip with animated captions
        """
        if not self.caption_service.enabled:
            return None
        
        # Generate caption data with Whisper timing
        caption_data = self.caption_service.generate_caption_data(text, duration, whisper_timing)
        
        if not caption_data['enabled']:
            return None
        
        word_timings = caption_data['word_timings']
        style = caption_data['style']
        
        # Create individual text clips for each word
        text_clips = []
        
        for word_timing in word_timings:
            word = word_timing['word']
            start_time = word_timing['start_time']
            end_time = word_timing['end_time']
            word_duration = end_time - start_time
            
            if word.strip():  # Skip empty words
                try:
                    # Create text clip for this word
                    text_clip = TextClip(
                        word,
                        fontsize=style['fontsize'],
                        color=style['color'],
                        stroke_color=style['stroke_color'],
                        stroke_width=style['stroke_width'],
                        font=style['font'],
                        method='caption'
                    ).set_position('center').set_start(start_time).set_duration(word_duration)
                    
                    text_clips.append(text_clip)
                    
                except Exception as e:
                    # Fallback to default font if Montserrat fails
                    print(f"Font {style['font']} failed, using fallback: {e}")
                    text_clip = TextClip(
                        word,
                        fontsize=style['fontsize'],
                        color=style['color'],
                        stroke_color=style['stroke_color'],
                        stroke_width=style['stroke_width'],
                        font=self.caption_service.font_fallback,
                        method='caption'
                    ).set_position('center').set_start(start_time).set_duration(word_duration)
                    
                    text_clips.append(text_clip)
        
        if text_clips:
            # Composite all word clips
            caption_clip = CompositeVideoClip(text_clips, size=(self.width, self.height)).set_duration(duration)
            timing_source = "Whisper" if whisper_timing else "fallback"
            print(f"Created caption clip with {len(text_clips)} words using {timing_source} timing")
            return caption_clip
        else:
            return None
    
    def create_scene_clip(self, scene_assets: Dict) -> VideoClip:
        """
        Create a video clip from scene assets (image + audio + captions).
        
        Args:
            scene_assets: Dictionary containing image_path, audio_path, etc.
            
        Returns:
            VideoClip object for the scene
        """
        try:
            # Load audio to determine clip duration
            audio_clip = AudioFileClip(scene_assets['audio_path'])
            duration = audio_clip.duration
            
            # Load image and ensure consistent portrait orientation
            image_clip = ImageClip(scene_assets['image_path']).set_duration(duration)
            
            # Force resize to portrait dimensions (crop if needed to maintain aspect ratio)
            image_clip = image_clip.resize(newsize=(self.width, self.height))
            
            # Apply camera movement (Ken Burns effect)
            if self.enable_movement:
                video_clip = self.apply_camera_movement(image_clip, duration)
            else:
                video_clip = image_clip
            
            # Create captions with Whisper timing if available
            caption_clip = self.create_caption_clip(
                scene_assets['voiceover_text'], 
                duration, 
                scene_assets.get('whisper_timing')
            )
            
            # Combine video, audio, and captions
            if caption_clip:
                # Composite video with captions
                final_clip = CompositeVideoClip([video_clip, caption_clip], size=(self.width, self.height))
                scene_clip = final_clip.set_audio(audio_clip)
                print(f"Created scene clip with captions - Duration: {duration:.2f}s")
            else:
                # Just video and audio
                scene_clip = video_clip.set_audio(audio_clip)
                print(f"Created scene clip without captions - Duration: {duration:.2f}s")
            
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
