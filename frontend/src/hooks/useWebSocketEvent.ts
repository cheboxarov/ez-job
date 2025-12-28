import { useEffect } from 'react';
import { wsClient, type WebSocketEventType } from '../api/websocket';

export function useWebSocketEvent<T>(
  eventType: WebSocketEventType,
  callback: (payload: T) => void
): void {
  useEffect(() => {
    const unsubscribe = wsClient.on(eventType, callback);
    return () => unsubscribe();
  }, [eventType, callback]);
}
