import cv2
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaStreamTrack
from av import VideoFrame
import requests

class VideoFrameHandler(MediaStreamTrack):
    kind = "video"

    def __init__(self):
        super().__init__()

    async def recv(self):
        frame = await super().recv()

        # Convert the WebRTC frame to OpenCV format
        video_frame = frame.to_ndarray(format="bgr24")
        cv2.imshow("Received Video", video_frame)

        # Display the frame in an OpenCV window
        if cv2.waitKey(1) & 0xFF == ord("q"):
            exit(0)
        return frame

async def start_client():
    pc = RTCPeerConnection()

    # Add a track to receive video
    video_track = VideoFrameHandler()
    pc.addTrack(video_track)

    # Create an SDP offer
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    # Send the SDP offer to the server
    response = requests.post(
        "http://127.0.0.1:8000/offer",  # Adjust URL if server is running elsewhere
        json={"sdp": pc.localDescription.sdp, "type": pc.localDescription.type},
    )
    response_data = response.json()

    # Set the server's SDP answer
    answer = RTCSessionDescription(response_data["sdp"], response_data["type"])
    await pc.setRemoteDescription(answer)

    # Keep the connection alive to continue receiving frames
    await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(start_client())
