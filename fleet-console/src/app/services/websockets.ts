import { Injectable } from '@angular/core';
import { Observable, take, tap, catchError, throwError } from 'rxjs';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

@Injectable({
  providedIn: 'root'
})
export class WebsocketService {
  public socket$: WebSocketSubject<any>;
  WS_ENDPOINT: string;


  constructor() {


  }
  
  generateGUID() {
    return 'xxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
  }



  // Method to connect to the WebSocket server
  public connect(): Observable<void> {
    const WS_ENDPOINT = this.determineWebSocketUrl() + this.generateGUID();
  
    // Initialize the WebSocket connection
    this.socket$ = webSocket(WS_ENDPOINT);
  
    // Return an Observable that emits once when the WebSocket connection is established
    return this.socket$.pipe(
      take(1), // Take the first message or event that indicates the connection is active
      tap({
        next: () => console.log('WebSocket connection established'),
        error: err => console.error('WebSocket connection error:', err)
      }),
      catchError(err => {
        // Handle any errors that occur during connection
        console.error('Failed to connect via WebSocket', err);
        return throwError(err); // Rethrow the error to be handled by the subscriber
      })
    );
  }

  // Method to receive messages from the server
  public getMessages(): Observable<any> {
    return this.socket$;
  }

  // Optional: Method to send messages to the server
  public sendMessage(message: any): void {
    this.socket$.next(message);
  }

  private determineWebSocketUrl() {
    // Detect the current host of the frontend
    const host = window.location.host;
  
    // Check if the frontend is running locally
    if (host.includes('localhost')) {
      // Use the hardcoded WebSocket URL for local development
      return 'ws://localhost:80';
    } else {
      // Build the WebSocket URL based on the current host
      // Assuming that the WebSocket server's subdomain and path are different
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const websocketHost = host.replace('fleetconsole', 'fleet-console-ws');
      return `${protocol}//${websocketHost}/`;
    }
  }
  
}
