def frame_to_ndarray(frame):
    """
    Convert aiortc VideoFrame to OpenCV-compatible ndarray
    """
    return frame.to_ndarray(format="bgr24")