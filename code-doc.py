import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import time

# Anomaly Detection Class using Exponentially Weighted Moving Average (EWMA) and Z-Score
class AnomalyDetector:
    def __init__(self, alpha=0.1, z_threshold=2):
        """
        Initializes the anomaly detector using EWMA and Z-score.

        Parameters:
        - alpha: Smoothing factor for EWMA (0 < alpha < 1). A lower value gives more weight to recent data.
        - z_threshold: Z-Score threshold for detecting anomalies. A higher value reduces false positives.
        """
        self.alpha = alpha  # EWMA smoothing factor
        self.z_threshold = z_threshold  # Z-Score anomaly threshold
        self.ewma = None  # Initial EWMA value is None (not calculated)
        self.variance = 0  # Initial variance for Z-score calculation
        self.n = 0  # Number of processed data points

    def detect(self, new_value):
        """
        Detects if the new value is an anomaly based on EWMA and Z-score.
        
        Parameters:
        - new_value: The incoming data point from the stream.

        Returns:
        - bool: True if the value is an anomaly, False otherwise.
        """
        # Initialize EWMA and variance on the first data point
        if self.ewma is None:
            self.ewma = new_value
            self.variance = 0
            self.n = 1
            return False  # First point cannot be an anomaly
        
        # Update EWMA and variance incrementally
        self.ewma = self.alpha * new_value + (1 - self.alpha) * self.ewma
        self.variance = self.alpha * (new_value - self.ewma) ** 2 + (1 - self.alpha) * self.variance
        std_dev = np.sqrt(self.variance)  # Calculate standard deviation
        
        # Calculate Z-Score; avoid division by zero
        z_score = abs(new_value - self.ewma) / std_dev if std_dev != 0 else 0
        
        # Detect anomaly based on Z-Score threshold
        is_anomaly = z_score > self.z_threshold
        
        # Print anomaly details if detected
        if is_anomaly:
            print(f"Anomaly detected: {new_value:.2f} (z_score: {z_score:.2f}, ewma: {self.ewma:.2f}, std_dev: {std_dev:.2f})")

        self.n += 1  # Increment the number of processed data points
        
        return is_anomaly

# Data Stream Simulation Function
def simulate_data_stream(duration=60, interval=0.5):
    """
    Simulates a continuous data stream with realistic patterns and noise.
    
    Parameters:
    - duration: Total time (in seconds) for the stream.
    - interval: Time interval between data points (in seconds).
    
    Yields:
    - Floating-point data points representing the simulated stream.
    """
    start_time = 0
    base_value = 10  # Base level for the data
    trend = 0.05  # Slow upward trend
    noise_level = 2  # Noise level for random fluctuations

    while start_time < duration:
        # Simulate realistic data with trend and noise
        time_component = base_value + trend * start_time
        noise = np.random.normal(0, noise_level)
        data_point = time_component + noise
        
        # Introduce anomalies at specific intervals
        if int(start_time) % 15 == 0 and start_time > 0:  # Every 15 seconds
            data_point += np.random.normal(15, 3)  # Significant spike anomaly
            
        yield data_point
        time.sleep(interval)
        start_time += interval

# Real-Time Visualization and Anomaly Detection
def real_time_anomaly_detection(duration=60, interval=0.5, window_size=100):
    """
    Real-time anomaly detection and visualization tool for a streaming data source.
    
    Parameters:
    - duration: Total duration for the simulation.
    - interval: Time interval between data points.
    - window_size: Number of data points to display in the plot at any time.
    """
    plt.ion()  # Enable interactive mode for real-time plotting
    fig, ax = plt.subplots()
    data_points = deque(maxlen=window_size)  # Holds last 'window_size' data points
    anomaly_points = deque(maxlen=window_size)  # Holds anomalies
    
    # Initialize the anomaly detector with defined parameters
    detector = AnomalyDetector(alpha=0.1, z_threshold=2.5)  # Adjusted parameters
    data_stream = simulate_data_stream(duration, interval)
    
    # Process each data point from the stream
    for i, data_point in enumerate(data_stream):
        # Ensure data_point is a valid number
        if not isinstance(data_point, (int, float)):
            print(f"Invalid data point: {data_point}. Skipping.")
            continue
        
        is_anomaly = detector.detect(data_point)  # Detect if the data point is an anomaly
        
        # Add the data point to the deque and mark anomaly if detected
        data_points.append(data_point)
        anomaly_points.append(data_point if is_anomaly else np.nan)
        
        # Clear and re-plot data and anomalies
        ax.clear()
        ax.plot(data_points, label="Data Stream", color='blue')
        ax.plot(anomaly_points, 'ro', label="Anomalies")
        ax.set_title(f"Real-Time Anomaly Detection (Step {i})")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Value")
        ax.legend(loc="upper left")
        plt.pause(0.01)  # Adjust this for faster/slower plotting
    
    plt.ioff()  # Disable interactive mode
    plt.show()  # Show the final plot

# Example: Run the simulation for 60 seconds with 0.5-second intervals
if __name__ == "__main__":
    try:
        real_time_anomaly_detection(duration=60, interval=0.5)
    except Exception as e:
        print(f"An error occurred: {e}")
