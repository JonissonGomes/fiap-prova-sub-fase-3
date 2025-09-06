// Import React for the hook  
import { useEffect } from 'react';

// Utility for notifying other components/pages about data changes
export const DATA_REFRESH_EVENTS = {
  VEHICLES: 'data-refresh-vehicles',
  CUSTOMERS: 'data-refresh-customers', 
  SALES: 'data-refresh-sales',
  ALL: 'data-refresh-all'
} as const;

export type DataRefreshEvent = typeof DATA_REFRESH_EVENTS[keyof typeof DATA_REFRESH_EVENTS];

// Debounce para evitar múltiplas atualizações muito rápidas
const debounceTimeouts = new Map<DataRefreshEvent | string, NodeJS.Timeout>();

// Controle de throttle para evitar refresh excessivo
const lastRefreshTimestamp = new Map<DataRefreshEvent, number>();
const THROTTLE_INTERVAL = 1000; // Mínimo 1 segundo entre refreshes do mesmo tipo

/**
 * Trigger a data refresh event to notify other components
 * @param eventType Type of data that was changed
 * @param details Optional details about the change
 * @param debounceMs Delay in milliseconds to debounce the event (default: 100ms)
 */
export const triggerDataRefresh = (eventType: DataRefreshEvent, details?: any, debounceMs: number = 500) => {
  // Check throttle - prevent too frequent refreshes
  const now = Date.now();
  const lastRefresh = lastRefreshTimestamp.get(eventType);
  if (lastRefresh && (now - lastRefresh) < THROTTLE_INTERVAL) {
    console.log(`Throttled: ${eventType} refresh too recent (${now - lastRefresh}ms ago)`);
    return;
  }
  
  // Clear previous timeout for this event type
  const existingTimeout = debounceTimeouts.get(eventType);
  if (existingTimeout) {
    clearTimeout(existingTimeout);
  }
  
  // Set new timeout
  const timeout = setTimeout(() => {
    const event = new CustomEvent(eventType, { detail: details });
    window.dispatchEvent(event);
    
    // Update throttle timestamp
    lastRefreshTimestamp.set(eventType, Date.now());
    
    // Also use localStorage to notify other tabs/windows
    localStorage.setItem('data-refresh-timestamp', Date.now().toString());
    localStorage.setItem('data-refresh-type', eventType);
    
    // Remove timeout from map
    debounceTimeouts.delete(eventType);
  }, debounceMs);
  
  debounceTimeouts.set(eventType, timeout);
};

/**
 * Trigger multiple data refresh events efficiently
 * @param eventTypes Array of event types to trigger
 * @param details Optional details about the change
 * @param debounceMs Delay in milliseconds to debounce the event (default: 500ms)
 */
export const triggerMultipleDataRefresh = (eventTypes: DataRefreshEvent[], details?: any, debounceMs: number = 500) => {
  // Use a single timeout for all events to avoid too many simultaneous calls
  const multiKey = eventTypes.sort().join('|');
  
  // Clear any existing timeout for this combination
  const existingTimeout = debounceTimeouts.get(multiKey as DataRefreshEvent);
  if (existingTimeout) {
    clearTimeout(existingTimeout);
  }
  
  const timeout = setTimeout(() => {
    // Trigger each event
    eventTypes.forEach(eventType => {
      const event = new CustomEvent(eventType, { detail: details });
      window.dispatchEvent(event);
    });
    
    // Update localStorage only once with the most relevant event
    localStorage.setItem('data-refresh-timestamp', Date.now().toString());
    localStorage.setItem('data-refresh-type', eventTypes[0]); // Use first event as primary
    
    // Remove timeout from map
    debounceTimeouts.delete(multiKey as DataRefreshEvent);
  }, debounceMs);
  
  debounceTimeouts.set(multiKey as DataRefreshEvent, timeout);
};

/**
 * Listen for data refresh events
 * @param eventType Type of event to listen for
 * @param callback Function to call when event occurs
 * @returns Cleanup function to remove the listener
 */
export const onDataRefresh = (eventType: DataRefreshEvent, callback: (details?: any) => void) => {
  const handler = (event: CustomEvent) => {
    callback(event.detail);
  };
  
  window.addEventListener(eventType, handler as EventListener);
  
  // Cleanup function
  return () => {
    window.removeEventListener(eventType, handler as EventListener);
  };
};

/**
 * Hook to refresh data when certain entities change
 * @param refreshFunction Function to call for refresh
 * @param eventTypes Array of event types to listen for
 */
export const useDataRefresh = (
  refreshFunction: () => void, 
  eventTypes: DataRefreshEvent[] = [DATA_REFRESH_EVENTS.ALL]
) => {
  useEffect(() => {
    const cleanupFunctions: (() => void)[] = [];
    
    eventTypes.forEach(eventType => {
      const cleanup = onDataRefresh(eventType, refreshFunction);
      cleanupFunctions.push(cleanup);
    });
    
    return () => {
      cleanupFunctions.forEach(cleanup => cleanup());
    };
  }, [refreshFunction, eventTypes]);
};
