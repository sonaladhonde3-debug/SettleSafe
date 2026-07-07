import { useEffect, useRef, useState, useCallback } from "react";

/**
 * Custom hook managing the lifecycle of a persistent WebSocket connection
 * to the FastAPI alerts channel, including automatic reconnection with
 * exponential backoff.
 */
export function useWebSocket(url, { maxBackoffMs = 15000 } = {}) {
  const [alerts, setAlerts] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const socketRef = useRef(null);
  const backoffRef = useRef(1000);
  const shouldReconnectRef = useRef(true);

  const connect = useCallback(() => {
    const socket = new WebSocket(url);
    socketRef.current = socket;

    socket.onopen = () => {
      setConnectionStatus("connected");
      backoffRef.current = 1000;
    };

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === "RISK_ALERT") {
          setAlerts((prev) => [message.data, ...prev].slice(0, 200));
        }
        // HEARTBEAT messages are ignored beyond keeping the connection alive.
      } catch (err) {
        console.error("Failed to parse websocket message", err);
      }
    };

    socket.onclose = () => {
      setConnectionStatus("disconnected");
      if (shouldReconnectRef.current) {
        setTimeout(connect, backoffRef.current);
        backoffRef.current = Math.min(backoffRef.current * 2, maxBackoffMs);
      }
    };

    socket.onerror = () => {
      socket.close();
    };
  }, [url, maxBackoffMs]);

  useEffect(() => {
    shouldReconnectRef.current = true;
    connect();
    return () => {
      shouldReconnectRef.current = false;
      socketRef.current?.close();
    };
  }, [connect]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/v1/trades/history")
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          // Pre-populate with historical data, wait for WebSocket to prepend new ones
          setAlerts(data);
        }
      })
      .catch(err => console.error("Failed to load database history", err));
  }, []);

  return { alerts, connectionStatus };
}
