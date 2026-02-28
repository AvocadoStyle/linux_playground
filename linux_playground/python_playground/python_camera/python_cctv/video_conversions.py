# video_converter.py
from pathlib import Path
from typing import Optional
import av
from av import VideoFrame


class VideoConverter:
    """
    A class for handling video processing tasks, including:
    - Extracting frames at specific intervals
    - Converting videos to WhatsApp-compatible MP4 (H.264 + yuv420p)
    
    Attributes:
        input_path (Path): Path to the source video.
        output_path (Path): Path where the converted video will be saved.
        frame_output_dir (Optional[Path]): Directory to save extracted frames as PNGs.
    """

    def __init__(
        self,
        input_path: str,
        output_path: str,
        frame_output_dir: Optional[str] = None,
    ) -> None:
        """
        Initialize VideoConverter with paths.
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.frame_output_dir: Optional[Path] = (
            Path(frame_output_dir) if frame_output_dir else None
        )

        # Ensure frame directory exists if specified
        if self.frame_output_dir:
            self.frame_output_dir.mkdir(parents=True, exist_ok=True)

    def extract_frames(self, interval_seconds: float = 1.0) -> None:
        """
        Extract frames from the video at a fixed interval and save as PNGs.
        
        Args:
            interval_seconds (float): Time interval in seconds between saved frames.
        """
        container = av.open(str(self.input_path))
        stream = container.streams.video[0]
        fps = float(stream.average_rate)
        frame_interval = max(1, int(fps * interval_seconds))

        print(f"Extracting frames every {interval_seconds}s (~every {frame_interval} frames)")
        for index, frame in enumerate(container.decode(stream)):
            if index % frame_interval == 0 and self.frame_output_dir:
                frame_path = self.frame_output_dir / f"frame-{index}.png"
                frame.to_image().save(frame_path)

        container.close()
        print("Frame extraction complete.")

    def convert_to_whatsapp_mp4(self) -> None:
        """
        Convert the video to WhatsApp-compatible MP4:
        - Video codec: H.264 (libx264)
        - Pixel format: yuv420p
        - Frame rate and resolution same as original
        """
        input_container = av.open(str(self.input_path))
        input_stream = input_container.streams.video[0]

        output_container = av.open(str(self.output_path), mode='w')

        # Create a single output video stream with H.264
        output_stream = output_container.add_stream(
            'libx264', rate=input_stream.average_rate
        )
        output_stream.width = input_stream.codec_context.width
        output_stream.height = input_stream.codec_context.height
        output_stream.pix_fmt = 'yuv420p'
        output_stream.time_base = input_stream.time_base

        print(f"Converting {self.input_path.name} to WhatsApp-compatible MP4...")
        for frame in input_container.decode(input_stream):
            for packet in output_stream.encode(frame):
                output_container.mux(packet)

        # Flush remaining frames
        for packet in output_stream.encode():
            output_container.mux(packet)

        input_container.close()
        output_container.close()
        print(f"Conversion complete. Saved as {self.output_path.name}")


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    BASE_PATH = Path('/home/armando/git_repos/linux_playground/linux_playground/python_playground/python_camera/python_cctv/')

    converter = VideoConverter(
        input_path=str(BASE_PATH / 'output.mp4'),
        output_path=str(BASE_PATH / 'output_for_whatsapp.mp4'),
        frame_output_dir=str(BASE_PATH / 'temp_media')
    )

    # Extract frames at 1-second intervals
    converter.extract_frames(interval_seconds=10.0)

    # Convert video to WhatsApp-compatible MP4
    converter.convert_to_whatsapp_mp4()